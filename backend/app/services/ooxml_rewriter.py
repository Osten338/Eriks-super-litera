"""OOXML rewriter for applying revision tracking to DOCX documents.

Preserves run formatting (<w:rPr>) while splitting runs and injecting
<w:ins>, <w:del>, <w:moveFrom>, <w:moveTo> elements.
"""
import io
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from xml.etree import ElementTree as ET

from docx import Document
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import RGBColor
from docx.text.paragraph import Paragraph as _DocxParagraph
from docx.text.run import Run as _DocxRun

from .ooxml_layer import ParagraphInfo, RunInfo, enumerate_runs, Block

# OOXML namespace
W_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

# Brand colors for revision tracking (when force_brand_colors=True)
COLOR_INSERT = RGBColor(30, 58, 138)   # blue-800
COLOR_DELETE = RGBColor(185, 28, 28)   # red-700
COLOR_MOVE = RGBColor(6, 95, 70)       # emerald-800


def _ensure_rPr(run_element: Any) -> Any:
    """Ensure a run has a <w:rPr> element, creating it if missing."""
    rPr = run_element.find(f"./{W_NS}rPr")
    if rPr is None:
        rPr = OxmlElement("w:rPr")
        # Insert at beginning of run
        if len(run_element) > 0:
            run_element.insert(0, rPr)
        else:
            run_element.append(rPr)
    return rPr


def _apply_brand_color(run_element: Any, color: RGBColor) -> None:
    """Apply brand color to run's <w:rPr>."""
    rPr = _ensure_rPr(run_element)
    
    # Set color
    color_elem = rPr.find(f"./{W_NS}color")
    if color_elem is None:
        color_elem = OxmlElement("w:color")
        rPr.append(color_elem)
    
    # Convert RGBColor to hex (without #)
    hex_color = f"{color.r:02x}{color.g:02x}{color.b:02x}"
    color_elem.set(qn("w:val"), hex_color)


def split_run_at_boundary(run_element: Any, char_offset: int) -> Tuple[Any, Any]:
    """Split a <w:r> element at a character offset.
    
    Args:
        run_element: The <w:r> XML element to split
        char_offset: Character offset where to split
    
    Returns:
        Tuple of (left_run, right_run) elements
    """
    # Get all text elements in the run
    text_elements = list(run_element.findall(f"./{W_NS}t"))
    
    if not text_elements:
        # No text, return original and empty run
        right_run = OxmlElement("w:r")
        # Copy rPr to right run
        rPr = run_element.find(f"./{W_NS}rPr")
        if rPr is not None:
            rPr_copy = ET.fromstring(ET.tostring(run_element.find(f"./{W_NS}rPr")))
            right_run.append(rPr_copy)
        return run_element, right_run
    
    # Find the text element and position where to split
    current_pos = 0
    split_elem_idx = 0
    split_elem_offset = 0
    
    for idx, t_elem in enumerate(text_elements):
        text = t_elem.text or ""
        text_len = len(text)
        
        if current_pos + text_len > char_offset:
            split_elem_idx = idx
            split_elem_offset = char_offset - current_pos
            break
        
        current_pos += text_len
    
    # Create new run for right side
    right_run = OxmlElement("w:r")
    
    # Copy rPr to right run
    rPr = run_element.find(f"./{W_NS}rPr")
    if rPr is not None:
        rPr_copy = ET.fromstring(ET.tostring(rPr))
        right_run.append(rPr_copy)
    
    # Split text at the boundary
    if split_elem_idx < len(text_elements):
        t_elem = text_elements[split_elem_idx]
        text = t_elem.text or ""
        
        # Left part stays in original run
        left_text = text[:split_elem_offset]
        right_text = text[split_elem_offset:]
        
        # Update left element
        t_elem.text = left_text
        
        # Add right text to new run
        if right_text:
            right_t = OxmlElement("w:t")
            right_t.text = right_text
            right_run.append(right_t)
        
        # Move remaining text elements to right run
        for remaining_elem in text_elements[split_elem_idx + 1:]:
            run_element.remove(remaining_elem)
            right_run.append(remaining_elem)
    else:
        # Split at end, right run is empty
        pass
    
    return run_element, right_run


def wrap_with_ins(
    element: Any,
    author: str = "Erik's Super Compare",
    date: Optional[datetime] = None,
    force_brand_color: bool = False,
) -> Any:
    """Wrap an element with <w:ins> (insertion) revision tracking.
    
    Args:
        element: The XML element to wrap (typically <w:r> or <w:p>)
        author: Revision author
        date: Revision date (default: current time)
        force_brand_color: If True, apply brand color to runs
    
    Returns:
        The <w:ins> wrapper element containing the original element
    """
    if date is None:
        date = datetime.now()
    
    ins = OxmlElement("w:ins")
    ins.set(qn("w:author"), author)
    ins.set(qn("w:date"), date.isoformat())
    
    # Move element into ins
    parent = element.getparent()
    if parent is not None:
        parent.remove(element)
    
    ins.append(element)
    
    # Apply brand color if requested
    if force_brand_color:
        # Find all runs within the element
        for run_elem in ins.findall(f".//{W_NS}r"):
            _apply_brand_color(run_elem, COLOR_INSERT)
    
    return ins


def wrap_with_del(
    element: Any,
    author: str = "Erik's Super Compare",
    date: Optional[datetime] = None,
    force_brand_color: bool = False,
) -> Any:
    """Wrap an element with <w:del> (deletion) revision tracking.
    
    Args:
        element: The XML element to wrap
        author: Revision author
        date: Revision date (default: current time)
        force_brand_color: If True, apply brand color and strike-through to runs
    
    Returns:
        The <w:del> wrapper element containing the original element
    """
    if date is None:
        date = datetime.now()
    
    dele = OxmlElement("w:del")
    dele.set(qn("w:author"), author)
    dele.set(qn("w:date"), date.isoformat())
    
    # Move element into del
    parent = element.getparent()
    if parent is not None:
        parent.remove(element)
    
    dele.append(element)
    
    # Apply brand color and strike-through if requested
    if force_brand_color:
        for run_elem in dele.findall(f".//{W_NS}r"):
            _apply_brand_color(run_elem, COLOR_DELETE)
            # Add strike-through
            rPr = _ensure_rPr(run_elem)
            strike = rPr.find(f"./{W_NS}strike")
            if strike is None:
                strike = OxmlElement("w:strike")
                rPr.append(strike)
            strike.set(qn("w:val"), "1")
    
    return dele


def create_move_pair(
    move_from_text: str,
    move_to_text: str,
    author: str = "Erik's Super Compare",
    date: Optional[datetime] = None,
    force_brand_color: bool = False,
) -> Tuple[Any, Any]:
    """Create <w:moveFrom> and <w:moveTo> pair for moved content.
    
    Args:
        move_from_text: Text being moved from (original location)
        move_to_text: Text being moved to (new location)
        author: Revision author
        date: Revision date (default: current time)
        force_brand_color: If True, apply brand color to runs
    
    Returns:
        Tuple of (moveFrom_element, moveTo_element)
    """
    if date is None:
        date = datetime.now()
    
    # Create moveFrom (deletion at original location)
    move_from = OxmlElement("w:moveFrom")
    move_from.set(qn("w:author"), author)
    move_from.set(qn("w:date"), date.isoformat())
    
    # Create moveTo (insertion at new location)
    move_to = OxmlElement("w:moveTo")
    move_to.set(qn("w:author"), author)
    move_to.set(qn("w:date"), date.isoformat())
    
    # For simplicity, wrap text in runs
    # In production, these would be proper paragraph/run structures
    move_from_run = OxmlElement("w:r")
    move_from_t = OxmlElement("w:t")
    move_from_t.text = move_from_text
    move_from_run.append(move_from_t)
    move_from.append(move_from_run)
    
    move_to_run = OxmlElement("w:r")
    move_to_t = OxmlElement("w:t")
    move_to_t.text = move_to_text
    move_to_run.append(move_to_t)
    move_to.append(move_to_run)
    
    # Apply brand color if requested
    if force_brand_color:
        for run_elem in [move_from_run, move_to_run]:
            _apply_brand_color(run_elem, COLOR_MOVE)
    
    return move_from, move_to


def apply_revision_tracking(
    original_doc: Document,
    diff_result: Dict[str, Any],
    force_brand_colors: bool = False,
) -> Document:
    """Apply revision tracking to a document based on diff results.
    
    This is a high-level function that coordinates the application of revisions.
    The actual implementation will work with paragraph-level operations.
    
    Args:
        original_doc: Original document
        diff_result: Diff result containing alignment pairs and operations
        force_brand_colors: If True, force brand colors via <w:rPr>
    
    Returns:
        Document with revision tracking applied
    """
    # This is a placeholder for the main rewriter logic
    # Full implementation would:
    # 1. Process alignment pairs from diff_result
    # 2. For each paragraph pair, apply inline diffs
    # 3. Split runs at change boundaries
    # 4. Wrap changes in <w:ins>/<w:del>/<w:moveFrom>/<w:moveTo>
    # 5. Preserve formatting from original runs
    
    # For now, return the document as-is
    # This will be fully implemented when integrating with the compare engine
    return original_doc


def _rewrite_paragraph_with_revisions(
    para_element: Any,
    original_runs: List[RunInfo],
    modified_runs: List[RunInfo],
    diff_operations: List[Tuple[str, int, int, int, int, bool]],
    force_brand_colors: bool = False,
) -> None:
    """Rewrite a paragraph element with revision tracking.
    
    Args:
        para_element: The <w:p> XML element
        original_runs: Original run information
        modified_runs: Modified run information
        diff_operations: List of (tag, orig_start, orig_end, mod_start, mod_end, is_move)
        force_brand_colors: Whether to force brand colors
    """
    # Clear existing content (we'll rebuild it)
    for child in list(para_element):
        if child.tag.endswith("}r"):
            para_element.remove(child)
    
    # Build new content with revisions
    # This is a simplified version - full implementation would:
    # 1. Process diff operations in order
    # 2. Split runs at boundaries
    # 3. Wrap with appropriate revision elements
    # 4. Preserve formatting
    
    # Placeholder: just add modified runs
    for run_info in modified_runs:
        # Create new run from run_info.xml_element
        # Wrap with <w:ins> if it's an insertion
        # This is simplified - full logic would handle all cases
        pass

