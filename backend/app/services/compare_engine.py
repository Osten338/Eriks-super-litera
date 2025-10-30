from typing import Any, Dict, List, Tuple, Iterable
from html import escape as html_escape
from difflib import SequenceMatcher

from ..models.schemas import DiffResponse, Stats, ParagraphHtml
from ..utils.text_ops import tokenize_preserve_spacing


def _ngram_tokens(tokens: List[str], n: int) -> Iterable[Tuple[str, Tuple[int, int]]]:
    if n <= 0 or len(tokens) < n:
        return []
    joined_tokens = [t for t in tokens]
    for i in range(0, len(joined_tokens) - n + 1):
        window = "".join(joined_tokens[i : i + n])
        yield window, (i, i + n)


def _build_ngram_index(paragraphs: List[Dict[str, str]], n: int = 5) -> set[str]:
    index: set[str] = set()
    for p in paragraphs:
        tokens = tokenize_preserve_spacing(p.get("text", ""))
        for key, _ in _ngram_tokens(tokens, n):
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
            is_move_old = any("".join(k) in mod_index for k in [del_seg]) if del_seg else False
            is_move_new = any("".join(k) in orig_index for k in [ins_seg]) if ins_seg else False
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


def run_compare(
    original_paragraphs: List[Dict[str, str]],
    modified_paragraphs: List[Dict[str, str]],
    options: Dict[str, Any],
) -> DiffResponse:
    include_formatting = bool(options.get("includeFormatting", True))
    # Build global ngram indices for move detection
    orig_index = _build_ngram_index(original_paragraphs, n=5)
    mod_index = _build_ngram_index(modified_paragraphs, n=5)

    max_len = max(len(original_paragraphs), len(modified_paragraphs))
    paragraphs: List[ParagraphHtml] = []
    total_insertions = total_deletions = total_moves = 0

    for i in range(max_len):
        orig_text = original_paragraphs[i]["text"] if i < len(original_paragraphs) else ""
        mod_text = modified_paragraphs[i]["text"] if i < len(modified_paragraphs) else ""

        if orig_text == mod_text:
            paragraphs.append(ParagraphHtml(html=f"<p>{html_escape(mod_text)}</p>"))
            continue

        tokens_a = tokenize_preserve_spacing(orig_text)
        tokens_b = tokenize_preserve_spacing(mod_text)

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

    meta = {"sourceTypes": {"original": "mixed", "modified": "mixed"}}
    return DiffResponse(paragraphs=paragraphs, stats=stats, meta=meta)


