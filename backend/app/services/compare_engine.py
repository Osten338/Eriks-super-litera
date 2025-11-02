from typing import Any, Dict, List, Tuple, Iterable, Optional, Callable
from html import escape as html_escape
from difflib import SequenceMatcher
import diff_match_patch as dmp_module
import io

from ..models.schemas import DiffResponse, Stats, ParagraphHtml
from ..utils.text_ops import tokenize_preserve_spacing, tokenize_for_diff, normalize_for_compare


def _char_ngrams(text: str, window: int) -> Iterable[str]:
    if window <= 0 or not text or len(text) < window:
        return []
    for i in range(0, len(text) - window + 1):
        yield text[i : i + window]


def _build_ngram_index(paragraphs: List[Dict[str, str]], window: int = 15) -> set[str]:
    """Build a set index of normalized character n-grams for move detection."""
    index: set[str] = set()
    for p in paragraphs:
        norm = normalize_for_compare(p.get("text", ""))
        for key in _char_ngrams(norm, window):
            index.add(key)
    return index


def _classify_and_wrap(tokens_a: List[str], tokens_b: List[str], mod_index: set[str], orig_index: set[str]) -> Tuple[str, int, int, int]:
    sm = SequenceMatcher(a=tokens_a, b=tokens_b, autojunk=False)
    html_parts: List[str] = []
    insertions = deletions = moves = 0
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            html_parts.append(html_escape("".join(tokens_b[j1:j2])))
        elif tag == "replace":
            # treat as delete then insert
            del_seg = "".join(tokens_a[i1:i2])
            ins_seg = "".join(tokens_b[j1:j2])
            # moved heuristics
            is_move_old = del_seg in mod_index if del_seg else False
            is_move_new = ins_seg in orig_index if ins_seg else False
            if del_seg:
                cls = "diff-move line-through" if is_move_old else "diff-delete line-through"
                moves += 1 if is_move_old else 0
                deletions += 0 if is_move_old else 1
                html_parts.append(f"<span class=\"{cls}\">{html_escape(del_seg)}</span>")
            if ins_seg:
                cls = "diff-move" if is_move_new else "diff-insert"
                moves += 1 if is_move_new else 0
                insertions += 0 if is_move_new else 1
                html_parts.append(f"<span class=\"{cls}\">{html_escape(ins_seg)}</span>")
        elif tag == "delete":
            seg = "".join(tokens_a[i1:i2])
            is_move = seg in mod_index
            cls = "diff-move line-through" if is_move else "diff-delete line-through"
            moves += 1 if is_move else 0
            deletions += 0 if is_move else 1
            html_parts.append(f"<span class=\"{cls}\">{html_escape(seg)}</span>")
        elif tag == "insert":
            seg = "".join(tokens_b[j1:j2])
            is_move = seg in orig_index
            cls = "diff-move" if is_move else "diff-insert"
            moves += 1 if is_move else 0
            insertions += 0 if is_move else 1
            html_parts.append(f"<span class=\"{cls}\">{html_escape(seg)}</span>")

    return "".join(html_parts), insertions, deletions, moves


def _align_paragraphs(original: List[Dict[str, str]], modified: List[Dict[str, str]]) -> List[Tuple[int, int]]:
    """Return list of index pairs (i, j) with -1 for gaps where needed."""
    a_norm = [normalize_for_compare(p.get("text", "")) for p in original]
    b_norm = [normalize_for_compare(p.get("text", "")) for p in modified]
    sm = SequenceMatcher(a=a_norm, b=b_norm, autojunk=False)
    pairs: List[Tuple[int, int]] = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            for off in range(i2 - i1):
                pairs.append((i1 + off, j1 + off))
        elif tag == "replace":
            len_a = i2 - i1
            len_b = j2 - j1
            # Pair by position up to min length, rest as gaps
            m = min(len_a, len_b)
            for off in range(m):
                pairs.append((i1 + off, j1 + off))
            for off in range(m, len_a):
                pairs.append((i1 + off, -1))
            for off in range(m, len_b):
                pairs.append((-1, j1 + off))
        elif tag == "delete":
            for i in range(i1, i2):
                pairs.append((i, -1))
        elif tag == "insert":
            for j in range(j1, j2):
                pairs.append((-1, j))
    return pairs


def run_compare(
    original_paragraphs: List[Dict[str, str]],
    modified_paragraphs: List[Dict[str, str]],
    options: Dict[str, Any],
) -> DiffResponse:
    include_formatting = bool(options.get("includeFormatting", True))
    granularity = (options.get("diffGranularity") or "word").lower()
    if granularity not in {"word", "char"}:
        granularity = "word"

    # Build global ngram indices for move detection (on normalized text)
    orig_index = _build_ngram_index(original_paragraphs, window=15)
    mod_index = _build_ngram_index(modified_paragraphs, window=15)

    pairs = _align_paragraphs(original_paragraphs, modified_paragraphs)

    paragraphs: List[ParagraphHtml] = []
    total_insertions = total_deletions = total_moves = 0

    for i, j in pairs:
        orig_text = original_paragraphs[i]["text"] if i >= 0 else ""
        mod_text = modified_paragraphs[j]["text"] if j >= 0 else ""

        if orig_text == mod_text:
            paragraphs.append(ParagraphHtml(html=f"<p>{html_escape(mod_text)}</p>"))
            continue

        tokens_a = tokenize_for_diff(orig_text, granularity)
        tokens_b = tokenize_for_diff(mod_text, granularity)

        body_html, ins, dels, mov = _classify_and_wrap(tokens_a, tokens_b, mod_index, orig_index)
        total_insertions += ins
        total_deletions += dels
        total_moves += mov
        paragraphs.append(ParagraphHtml(html=f"<p>{body_html}</p>"))

    stats = Stats(
        insertions=total_insertions,
        deletions=total_deletions,
        moves=total_moves,
        total=total_insertions + total_deletions + total_moves,
    )

    # Expose alignment pairs so exporters can map diff paragraphs back to
    # original paragraph indices and preserve layout when applying redlines.
    # Each entry is a tuple (i, j) where -1 denotes a gap/insert/delete.
    meta = {
        "sourceTypes": {"original": "mixed", "modified": "mixed"},
        "granularity": granularity,
        "pairs": pairs,
    }
    return DiffResponse(paragraphs=paragraphs, stats=stats, meta=meta)


# ============================================================================
# Patience + Myers Diff Algorithms for OOXML
# ============================================================================

def _patience_lis(sequence: List[Tuple[int, int]]) -> List[int]:
    """Find Longest Increasing Subsequence using patience sorting.
    
    Input: sequence of (value, original_index) tuples
    Output: list of original indices in the LIS
    """
    if not sequence:
        return []
    
    # Patience sorting: maintain piles, each pile is a decreasing sequence
    piles: List[List[Tuple[int, int]]] = []
    predecessors: Dict[int, Optional[int]] = {}
    
    for val, idx in sequence:
        # Binary search for the leftmost pile where we can place this value
        left, right = 0, len(piles)
        while left < right:
            mid = (left + right) // 2
            if piles[mid][-1][0] >= val:
                right = mid
            else:
                left = mid + 1
        
        # Create new pile if needed
        if left == len(piles):
            piles.append([])
        
        piles[left].append((val, idx))
        
        # Track predecessor (element in previous pile that's < val)
        if left > 0:
            predecessors[idx] = piles[left - 1][-1][1]
        else:
            predecessors[idx] = None
    
    # Reconstruct LIS by following predecessors from the last element
    if not piles:
        return []
    
    lis: List[int] = []
    current_idx = piles[-1][-1][1]
    while current_idx is not None:
        lis.append(current_idx)
        current_idx = predecessors.get(current_idx)
    
    lis.reverse()
    return lis


def _myers_diff(a: List[str], b: List[str]) -> List[Tuple[str, int, int, int, int]]:
    """Myers diff algorithm for aligning sequences.
    
    Returns list of opcodes: (tag, i1, i2, j1, j2)
    where tag is 'equal', 'delete', 'insert', 'replace'
    """
    if not a and not b:
        return []
    if not a:
        return [("insert", 0, 0, 0, len(b))]
    if not b:
        return [("delete", 0, len(a), 0, 0)]
    
    # Simplified Myers using dynamic programming
    # For production, consider using a more optimized implementation
    n, m = len(a), len(b)
    dp: List[List[int]] = [[0] * (m + 1) for _ in range(n + 1)]
    
    # Fill DP table
    for i in range(n + 1):
        for j in range(m + 1):
            if i == 0:
                dp[i][j] = j
            elif j == 0:
                dp[i][j] = i
            elif a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])
    
    # Backtrack to get opcodes
    opcodes: List[Tuple[str, int, int, int, int]] = []
    i, j = n, m
    
    while i > 0 or j > 0:
        if i > 0 and j > 0 and a[i - 1] == b[j - 1]:
            # Equal - will be merged later
            i -= 1
            j -= 1
        elif i > 0 and (j == 0 or dp[i][j] == dp[i - 1][j] + 1):
            # Delete
            opcodes.append(("delete", i - 1, i, j, j))
            i -= 1
        elif j > 0 and (i == 0 or dp[i][j] == dp[i][j - 1] + 1):
            # Insert
            opcodes.append(("insert", i, i, j - 1, j))
            j -= 1
        else:
            # Replace
            opcodes.append(("replace", i - 1, i, j - 1, j))
            i -= 1
            j -= 1
    
    opcodes.reverse()
    
    # Merge consecutive operations
    merged: List[Tuple[str, int, int, int, int]] = []
    for op in opcodes:
        if merged and merged[-1][0] == op[0] and merged[-1][2] == op[1] and merged[-1][4] == op[3]:
            # Merge with previous
            prev = merged.pop()
            merged.append((op[0], prev[1], op[2], prev[3], op[4]))
        else:
            merged.append(op)
    
    # Convert replaces to delete+insert for consistency
    final: List[Tuple[str, int, int, int, int]] = []
    for op in merged:
        if op[0] == "replace":
            final.append(("delete", op[1], op[2], op[3], op[3]))
            final.append(("insert", op[2], op[2], op[3], op[4]))
        else:
            final.append(op)
    
    return final


def _align_patience_myers(
    original: List[str],
    modified: List[str],
    hash_fn: Optional[Callable[[str], str]] = None,
) -> List[Tuple[int, int]]:
    """Align sequences using patience diff + Myers fallback.
    
    Args:
        original: Original sequence (list of normalized strings)
        modified: Modified sequence (list of normalized strings)
        hash_fn: Optional hash function for comparison (default: identity)
    
    Returns:
        List of alignment pairs (i, j) where -1 indicates a gap
    """
    if hash_fn is None:
        hash_fn = lambda x: x
    
    # Build index of modified items
    mod_hash_to_indices: Dict[str, List[int]] = {}
    for j, item in enumerate(modified):
        h = hash_fn(item)
        mod_hash_to_indices.setdefault(h, []).append(j)
    
    # Find matching pairs (items that appear in both sequences with same hash)
    matches: List[Tuple[int, int]] = []
    used_mod_indices: set[int] = set()
    
    for i, orig_item in enumerate(original):
        h = hash_fn(orig_item)
        if h in mod_hash_to_indices:
            # Find the closest unused match
            candidates = [j for j in mod_hash_to_indices[h] if j not in used_mod_indices]
            if candidates:
                # Use the first available candidate (could be improved with position heuristics)
                j = candidates[0]
                matches.append((i, j))
                used_mod_indices.add(j)
    
    if not matches:
        # No matches found, use Myers for everything
        opcodes = _myers_diff(original, modified)
        pairs: List[Tuple[int, int]] = []
        orig_idx = mod_idx = 0
        for tag, i1, i2, j1, j2 in opcodes:
            if tag == "equal":
                for off in range(i2 - i1):
                    pairs.append((i1 + off, j1 + off))
                orig_idx = i2
                mod_idx = j2
            elif tag == "delete":
                for i in range(i1, i2):
                    pairs.append((i, -1))
                orig_idx = i2
            elif tag == "insert":
                for j in range(j1, j2):
                    pairs.append((-1, j))
                mod_idx = j2
        return pairs
    
    # Extract LIS from matches using patience algorithm
    # Sort matches by original index, then use patience on modified indices
    sorted_matches = sorted(matches, key=lambda x: x[0])
    match_sequence = [(j, i) for i, j in sorted_matches]  # (modified_idx, original_idx)
    lis_indices = _patience_lis(match_sequence)
    
    # Build alignment pairs from LIS matches
    pairs: List[Tuple[int, int]] = []
    orig_idx = mod_idx = 0
    
    for lis_pos, orig_i in enumerate(lis_indices):
        mod_j = sorted_matches[orig_i][1]
        
        # Handle gap before this match using Myers
        orig_gap = original[orig_idx:orig_i]
        mod_gap = modified[mod_idx:mod_j]
        if orig_gap or mod_gap:
            gap_opcodes = _myers_diff(orig_gap, mod_gap)
            for tag, gi1, gi2, gj1, gj2 in gap_opcodes:
                if tag == "equal":
                    for off in range(gi2 - gi1):
                        pairs.append((orig_idx + gi1 + off, mod_idx + gj1 + off))
                elif tag == "delete":
                    for gi in range(gi1, gi2):
                        pairs.append((orig_idx + gi, -1))
                elif tag == "insert":
                    for gj in range(gj1, gj2):
                        pairs.append((-1, mod_idx + gj))
            orig_idx = orig_i
            mod_idx = mod_j
        
        # Add the match
        pairs.append((orig_i, mod_j))
        orig_idx = orig_i + 1
        mod_idx = mod_j + 1
    
    # Handle trailing gaps
    if orig_idx < len(original) or mod_idx < len(modified):
        orig_gap = original[orig_idx:]
        mod_gap = modified[mod_idx:]
        gap_opcodes = _myers_diff(orig_gap, mod_gap)
        for tag, gi1, gi2, gj1, gj2 in gap_opcodes:
            if tag == "equal":
                for off in range(gi2 - gi1):
                    pairs.append((orig_idx + gi1 + off, mod_idx + gj1 + off))
            elif tag == "delete":
                for gi in range(gi1, gi2):
                    pairs.append((orig_idx + gi, -1))
            elif tag == "insert":
                for gj in range(gj1, gj2):
                    pairs.append((-1, mod_idx + gj))
    
    return pairs


def _align_blocks_patience(
    original_blocks: List[Any],
    modified_blocks: List[Any],
    hash_fn: Optional[Callable[[Any], str]] = None,
) -> List[Tuple[int, int]]:
    """Align blocks using patience + Myers algorithm.
    
    Args:
        original_blocks: List of block objects with normalized text + style signature
        modified_blocks: List of block objects with normalized text + style signature
        hash_fn: Function to hash a block for comparison
    
    Returns:
        List of alignment pairs (i, j) where -1 indicates a gap
    """
    # Extract normalized text + style signature for each block
    orig_hashes = []
    mod_hashes = []
    
    for block in original_blocks:
        if hasattr(block, "normalized"):
            text = block.normalized
        elif isinstance(block, dict):
            text = normalize_for_compare(block.get("text", ""))
        else:
            text = str(block)
        
        # Include style signature if available
        style_sig = getattr(block, "style_sig", "") if hasattr(block, "style_sig") else ""
        sig = f"{text}|{style_sig}"
        orig_hashes.append(sig)
    
    for block in modified_blocks:
        if hasattr(block, "normalized"):
            text = block.normalized
        elif isinstance(block, dict):
            text = normalize_for_compare(block.get("text", ""))
        else:
            text = str(block)
        
        style_sig = getattr(block, "style_sig", "") if hasattr(block, "style_sig") else ""
        sig = f"{text}|{style_sig}"
        mod_hashes.append(sig)
    
    return _align_patience_myers(orig_hashes, mod_hashes)


def _align_paragraphs_patience(
    original_paragraphs: List[Any],
    modified_paragraphs: List[Any],
) -> List[Tuple[int, int]]:
    """Align paragraphs using patience + Myers algorithm.
    
    Args:
        original_paragraphs: List of paragraph info objects
        modified_paragraphs: List of paragraph info objects
    
    Returns:
        List of alignment pairs (i, j) where -1 indicates a gap
    """
    orig_hashes = []
    mod_hashes = []
    
    for para in original_paragraphs:
        if hasattr(para, "normalized"):
            text = para.normalized
        elif isinstance(para, dict):
            text = normalize_for_compare(para.get("text", ""))
        else:
            text = str(para)
        
        style_sig = getattr(para, "style_sig", "") if hasattr(para, "style_sig") else ""
        sig = f"{text}|{style_sig}"
        orig_hashes.append(sig)
    
    for para in modified_paragraphs:
        if hasattr(para, "normalized"):
            text = para.normalized
        elif isinstance(para, dict):
            text = normalize_for_compare(para.get("text", ""))
        else:
            text = str(para)
        
        style_sig = getattr(para, "style_sig", "") if hasattr(para, "style_sig") else ""
        sig = f"{text}|{style_sig}"
        mod_hashes.append(sig)
    
    return _align_patience_myers(orig_hashes, mod_hashes)


def _diff_runs_inline(
    original_runs: List[str],
    modified_runs: List[str],
) -> List[Tuple[str, int, int, int, int]]:
    """Diff runs at token level using diff-match-patch.
    
    Args:
        original_runs: List of run text strings
        modified_runs: List of run text strings
    
    Returns:
        List of edit operations: (tag, orig_start, orig_end, mod_start, mod_end)
        where tag is 'equal', 'delete', 'insert', 'replace'
    """
    orig_text = "".join(original_runs)
    mod_text = "".join(modified_runs)
    
    # Use diff-match-patch for token-level diff
    dmp = dmp_module.diff_match_patch()
    dmp.Diff_Timeout = 0  # No timeout
    
    # Tokenize for better diff (words)
    orig_tokens = tokenize_for_diff(orig_text, "word")
    mod_tokens = tokenize_for_diff(mod_text, "word")
    
    orig_token_str = "\0".join(orig_tokens)  # Use null separator
    mod_token_str = "\0".join(mod_tokens)
    
    diffs = dmp.diff_main(orig_token_str, mod_token_str)
    dmp.diff_cleanupSemantic(diffs)
    
    # Convert diffs to opcodes with character positions
    # diff-match-patch returns list of tuples: (-1 for delete, 0 for equal, 1 for insert, text)
    opcodes: List[Tuple[str, int, int, int, int]] = []
    orig_pos = 0
    mod_pos = 0
    
    for diff_tuple in diffs:
        if len(diff_tuple) != 2:
            continue
        op, text = diff_tuple
        orig_start = orig_pos
        mod_start = mod_pos
        
        if op == 0:  # DIFF_EQUAL
            orig_len = len(text)
            mod_len = len(text)
            opcodes.append(("equal", orig_start, orig_start + orig_len, mod_start, mod_start + mod_len))
            orig_pos += orig_len
            mod_pos += mod_len
        elif op == -1:  # DIFF_DELETE
            orig_len = len(text)
            opcodes.append(("delete", orig_start, orig_start + orig_len, mod_start, mod_start))
            orig_pos += orig_len
        elif op == 1:  # DIFF_INSERT
            mod_len = len(text)
            opcodes.append(("insert", orig_start, orig_start, mod_start, mod_start + mod_len))
            mod_pos += mod_len
    
    return opcodes


def _token_shingles(tokens: List[str], shingle_size: int) -> set[str]:
    """Generate shingled hash set from tokens.
    
    Args:
        tokens: List of token strings
        shingle_size: Number of consecutive tokens per shingle
    
    Returns:
        Set of shingle strings (concatenated tokens)
    """
    if len(tokens) < shingle_size:
        return set()
    
    shingles: set[str] = set()
    for i in range(len(tokens) - shingle_size + 1):
        shingle = " ".join(tokens[i:i + shingle_size])
        shingles.add(shingle)
    
    return shingles


def _jaccard_similarity(set1: set[str], set2: set[str]) -> float:
    """Compute Jaccard similarity between two sets.
    
    J(A, B) = |A ∩ B| / |A ∪ B|
    """
    if not set1 and not set2:
        return 1.0
    if not set1 or not set2:
        return 0.0
    
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    
    return intersection / union if union > 0 else 0.0


def _detect_moves_shingled(
    deleted_spans: List[Tuple[str, List[str], int, int]],  # (text, tokens, start, end)
    inserted_spans: List[Tuple[str, List[str], int, int]],  # (text, tokens, start, end)
    shingle_size: int = 5,
    jaccard_threshold: float = 0.85,
    min_span_tokens: int = 12,
) -> Dict[Tuple[int, int, int], Tuple[int, int, int]]:
    """Detect moved content using shingled-hash matching with Jaccard similarity.
    
    Args:
        deleted_spans: List of (text, tokens, orig_start_idx, orig_end_idx) for deleted content
        inserted_spans: List of (text, tokens, mod_start_idx, mod_end_idx) for inserted content
        shingle_size: Number of tokens per shingle (default: 5)
        jaccard_threshold: Minimum Jaccard similarity to consider a move (default: 0.85)
        min_span_tokens: Minimum tokens in span to consider for move detection (default: 12)
    
    Returns:
        Dictionary mapping (del_idx, del_start, del_end) -> (ins_idx, ins_start, ins_end)
        indicating which deletions match which insertions as moves
    """
    move_mappings: Dict[Tuple[int, int, int], Tuple[int, int, int]] = {}
    
    # Build shingle sets for all spans
    deleted_shingles: List[set[str]] = []
    inserted_shingles: List[set[str]] = []
    
    for text, tokens, start, end in deleted_spans:
        if len(tokens) >= min_span_tokens:
            shingles = _token_shingles(tokens, shingle_size)
            deleted_shingles.append(shingles)
        else:
            deleted_shingles.append(set())  # Too small, skip move detection
    
    for text, tokens, start, end in inserted_spans:
        if len(tokens) >= min_span_tokens:
            shingles = _token_shingles(tokens, shingle_size)
            inserted_shingles.append(shingles)
        else:
            inserted_shingles.append(set())  # Too small, skip move detection
    
    # Match deletions to insertions
    used_insertions: set[int] = set()
    
    # Sort by span size (larger first) to match longest moves first
    del_with_size = [(i, s, deleted_spans[i]) for i, s in enumerate(deleted_shingles)]
    del_with_size.sort(key=lambda x: len(x[1]), reverse=True)
    
    for del_idx, del_shingles, (del_text, del_tokens, del_start, del_end) in del_with_size:
        if not del_shingles:
            continue
        
        best_match: Optional[Tuple[int, float]] = None
        best_jaccard = 0.0
        
        # Find best matching insertion
        for ins_idx, (ins_shingles, (ins_text, ins_tokens, ins_start, ins_end)) in enumerate(
            zip(inserted_shingles, inserted_spans)
        ):
            if ins_idx in used_insertions or not ins_shingles:
                continue
            
            jaccard = _jaccard_similarity(del_shingles, ins_shingles)
            if jaccard >= jaccard_threshold and jaccard > best_jaccard:
                best_match = (ins_idx, jaccard)
                best_jaccard = jaccard
        
        if best_match:
            ins_idx, _ = best_match
            move_mappings[(del_idx, del_start, del_end)] = (
                ins_idx,
                inserted_spans[ins_idx][2],  # ins_start
                inserted_spans[ins_idx][3],   # ins_end
            )
            used_insertions.add(ins_idx)
    
    return move_mappings


def _classify_operations_with_moves(
    opcodes: List[Tuple[str, int, int, int, int]],
    original_text: str,
    modified_text: str,
    original_tokens: List[str],
    modified_tokens: List[str],
    shingle_size: int = 5,
    jaccard_threshold: float = 0.85,
    min_move_span_tokens: int = 12,
) -> List[Tuple[str, int, int, int, int, bool]]:
    """Classify diff operations, detecting moves via shingled-hash matching.
    
    Args:
        opcodes: List of (tag, orig_start, orig_end, mod_start, mod_end) operations
        original_text: Full original text
        modified_text: Full modified text
        original_tokens: Tokenized original text
        modified_tokens: Tokenized modified text
        shingle_size: Size of shingles for move detection
        jaccard_threshold: Minimum Jaccard similarity for move detection
        min_move_span_tokens: Minimum tokens to consider for move detection
    
    Returns:
        List of (tag, orig_start, orig_end, mod_start, mod_end, is_move) operations
    """
    # Extract deleted and inserted spans
    deleted_spans: List[Tuple[str, List[str], int, int]] = []
    inserted_spans: List[Tuple[str, List[str], int, int]] = []
    
    for tag, orig_start, orig_end, mod_start, mod_end in opcodes:
        if tag == "delete":
            span_text = original_text[orig_start:orig_end]
            # Map character positions to token positions
            char_to_token_orig = _build_char_to_token_map(original_tokens)
            token_start = char_to_token_orig.get(orig_start, 0)
            token_end = char_to_token_orig.get(orig_end, len(original_tokens))
            span_tokens = original_tokens[token_start:token_end]
            deleted_spans.append((span_text, span_tokens, len(deleted_spans), len(deleted_spans)))
        elif tag == "insert":
            span_text = modified_text[mod_start:mod_end]
            char_to_token_mod = _build_char_to_token_map(modified_tokens)
            token_start = char_to_token_mod.get(mod_start, 0)
            token_end = char_to_token_mod.get(mod_end, len(modified_tokens))
            span_tokens = modified_tokens[token_start:token_end]
            inserted_spans.append((span_text, span_tokens, len(inserted_spans), len(inserted_spans)))
    
    # Detect moves
    move_mappings = _detect_moves_shingled(
        deleted_spans,
        inserted_spans,
        shingle_size=shingle_size,
        jaccard_threshold=jaccard_threshold,
        min_span_tokens=min_move_span_tokens,
    )
    
    # Build reverse mapping: (orig_start, orig_end) -> (mod_start, mod_end) for moves
    char_move_map: Dict[Tuple[int, int], Tuple[int, int]] = {}
    for (del_idx, del_start_char, del_end_char), (ins_idx, ins_start_char, ins_end_char) in move_mappings.items():
        char_move_map[(deleted_spans[del_idx][2], deleted_spans[del_idx][3])] = (
            inserted_spans[ins_idx][2],
            inserted_spans[ins_idx][3],
        )
    
    # Classify operations
    classified: List[Tuple[str, int, int, int, int, bool]] = []
    del_idx = 0
    ins_idx = 0
    
    for tag, orig_start, orig_end, mod_start, mod_end in opcodes:
        is_move = False
        
        if tag == "delete":
            if (orig_start, orig_end) in char_move_map:
                is_move = True
            del_idx += 1
        elif tag == "insert":
            # Check if this insertion is part of a move
            for (del_char_start, del_char_end), (ins_char_start, ins_char_end) in char_move_map.items():
                if mod_start >= ins_char_start and mod_end <= ins_char_end:
                    is_move = True
                    break
            ins_idx += 1
        
        classified.append((tag, orig_start, orig_end, mod_start, mod_end, is_move))
    
    return classified


def _build_char_to_token_map(tokens: List[str]) -> Dict[int, int]:
    """Build mapping from character position to token index.
    
    Args:
        tokens: List of token strings
    
    Returns:
        Dictionary mapping character position to token index
    """
    char_to_token: Dict[int, int] = {}
    char_pos = 0
    
    for token_idx, token in enumerate(tokens):
        char_to_token[char_pos] = token_idx
        char_pos += len(token)
        char_to_token[char_pos] = token_idx + 1  # End position maps to next token
    
    return char_to_token


# ============================================================================
# Main OOXML Comparison Function
# ============================================================================

def run_compare_ooxml(
    original_docx_bytes: bytes,
    modified_docx_bytes: bytes,
    options: Dict[str, Any],
) -> Dict[str, Any]:
    """Compare two DOCX documents natively using OOXML revision tracking.
    
    Args:
        original_docx_bytes: Original DOCX file as bytes
        modified_docx_bytes: Modified DOCX file as bytes
        options: Configuration options including:
            - shingle_size: int (default 5)
            - jaccard_threshold: float (default 0.85)
            - min_move_span_tokens: int (default 12)
            - force_brand_colors: bool (default False)
    
    Returns:
        Dictionary containing:
            - document_bytes: bytes (revision-tracked DOCX)
            - stats: Stats object
            - meta: Dict with alignment pairs, move mappings, etc.
    """
    from .ooxml_layer import load_docx, enumerate_blocks, enumerate_paragraphs
    
    # Load documents
    orig_doc = load_docx(original_docx_bytes)
    mod_doc = load_docx(modified_docx_bytes)
    
    # Extract configuration
    shingle_size = int(options.get("shingle_size", 5))
    jaccard_threshold = float(options.get("jaccard_threshold", 0.85))
    min_move_span_tokens = int(options.get("min_move_span_tokens", 12))
    force_brand_colors = bool(options.get("force_brand_colors", False))
    
    # Enumerate blocks and paragraphs
    orig_blocks = enumerate_blocks(orig_doc)
    mod_blocks = enumerate_blocks(mod_doc)
    
    # Extract all paragraphs from blocks
    orig_paragraphs: List = []
    mod_paragraphs: List = []
    
    for block in orig_blocks:
        orig_paragraphs.extend(block.paragraphs)
    
    for block in mod_blocks:
        mod_paragraphs.extend(block.paragraphs)
    
    # Align paragraphs using patience+Myers
    para_pairs = _align_paragraphs_patience(orig_paragraphs, mod_paragraphs)
    
    # Process each paragraph pair
    total_insertions = 0
    total_deletions = 0
    total_moves = 0
    
    revision_operations: List[Dict[str, Any]] = []
    
    for orig_idx, mod_idx in para_pairs:
        orig_para = orig_paragraphs[orig_idx] if orig_idx >= 0 else None
        mod_para = mod_paragraphs[mod_idx] if mod_idx >= 0 else None
        
        if orig_para is None and mod_para is None:
            continue
        
        if orig_para is None:
            # Pure insertion
            revision_operations.append({
                "kind": "insert",
                "para_idx": mod_idx,
                "paragraph": mod_para,
            })
            total_insertions += 1
            continue
        
        if mod_para is None:
            # Pure deletion
            revision_operations.append({
                "kind": "delete",
                "para_idx": orig_idx,
                "paragraph": orig_para,
            })
            total_deletions += 1
            continue
        
        # Both exist - do inline diff
        orig_text = orig_para.text
        mod_text = mod_para.text
        
        if orig_text == mod_text:
            # No changes
            continue
        
        # Tokenize for inline diff
        orig_tokens = tokenize_for_diff(orig_text, "word")
        mod_tokens = tokenize_for_diff(mod_text, "word")
        
        # Get runs
        orig_runs = [run.text for run in orig_para.runs]
        mod_runs = [run.text for run in mod_para.runs]
        
        # Diff runs inline
        opcodes = _diff_runs_inline(orig_runs, mod_runs)
        
        # Classify operations with move detection
        classified = _classify_operations_with_moves(
            opcodes,
            orig_text,
            mod_text,
            orig_tokens,
            mod_tokens,
            shingle_size=shingle_size,
            jaccard_threshold=jaccard_threshold,
            min_move_span_tokens=min_move_span_tokens,
        )
        
        # Count changes
        for tag, _, _, _, _, is_move in classified:
            if tag == "insert":
                if is_move:
                    total_moves += 1
                else:
                    total_insertions += 1
            elif tag == "delete":
                if is_move:
                    total_moves += 1
                else:
                    total_deletions += 1
        
        revision_operations.append({
            "kind": "replace",
            "orig_para_idx": orig_idx,
            "mod_para_idx": mod_idx,
            "orig_para": orig_para,
            "mod_para": mod_para,
            "operations": classified,
        })
    
    # Build stats
    stats = Stats(
        insertions=total_insertions,
        deletions=total_deletions,
        moves=total_moves,
        total=total_insertions + total_deletions + total_moves,
    )
    
    # Apply revisions to document
    # For now, return original document (rewriter will be fully implemented)
    from .ooxml_rewriter import apply_revision_tracking
    revised_doc = apply_revision_tracking(
        orig_doc,
        {
            "operations": revision_operations,
            "pairs": para_pairs,
        },
        force_brand_colors=force_brand_colors,
    )
    
    # Serialize to bytes
    bio = io.BytesIO()
    revised_doc.save(bio)
    doc_bytes = bio.getvalue()
    
    return {
        "document_bytes": doc_bytes,
        "stats": stats,
        "meta": {
            "pairs": para_pairs,
            "revision_operations": len(revision_operations),
        },
    }

