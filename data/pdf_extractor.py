"""Downloads and extracts order book, guidance, capex, and concall text from PDFs."""

import io
import logging
import re
import requests
import pdfplumber

logger = logging.getLogger(__name__)

_CONCALL_KEYWORDS = re.compile(
    r"((?:management|guidance|outlook|order book|revenue guidance|capex|"
    r"margin expansion|growth target|expansion plan|new order|capex plan|"
    r"we expect|confident|cautious|headwind|tailwind)[^.]{5,150}\.)",
    re.IGNORECASE,
)


def extract_investor_presentation(pdf_url: str) -> dict:
    """Download a PDF from pdf_url and extract key metrics.

    Returns dict with orderBook (float|None), guidance (str|None), capex (str|None).
    Never raises — returns empty values on any failure.
    """
    try:
        resp = requests.get(pdf_url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
        if resp.status_code != 200:
            logger.warning("PDF download failed: %s for %s", resp.status_code, pdf_url)
            return {"orderBook": None, "guidance": None, "capex": None}
        return _parse_pdf_bytes(resp.content)
    except Exception as exc:
        logger.warning("PDF extraction failed for %s: %s", pdf_url, exc)
        return {"orderBook": None, "guidance": None, "capex": None}


def _parse_pdf_bytes(content: bytes) -> dict:
    """Parse raw PDF bytes and extract order book value, guidance, and capex info."""
    result = {"orderBook": None, "guidance": None, "capex": None}
    text_pages = []
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        for page in pdf.pages[:20]:  # scan first 20 pages
            text = page.extract_text() or ""
            text_pages.append(text)

    full_text = "\n".join(text_pages)

    # Order book: look for patterns like "Order Book: ₹12,345 Cr" or "order backlog of 12345"
    ob_match = re.search(
        r"order\s*book[:\s]+[₹\$]?\s*([\d,]+(?:\.\d+)?)\s*(cr|crore|bn|billion)?",
        full_text, re.IGNORECASE
    )
    if ob_match:
        try:
            val = float(ob_match.group(1).replace(",", ""))
            unit = (ob_match.group(2) or "").lower()
            result["orderBook"] = val * 100 if "bn" in unit or "billion" in unit else val
        except ValueError:
            pass

    # Guidance: sentence containing "guidance" or "expect" or "target"
    guidance_match = re.search(
        r"([^.]*(?:guidance|we expect|management expect|target revenue|revenue target)[^.]*\.)",
        full_text, re.IGNORECASE
    )
    if guidance_match:
        result["guidance"] = guidance_match.group(1).strip()[:300]

    # Capex: sentence containing "capex" or "capital expenditure"
    capex_match = re.search(
        r"([^.]*(?:capex|capital expenditure)[^.]*\.)",
        full_text, re.IGNORECASE
    )
    if capex_match:
        result["capex"] = capex_match.group(1).strip()[:300]

    return result


def extract_concall_text(pdf_url: str) -> str:
    """Extract management commentary and Q&A excerpts from a concall transcript PDF.

    Returns up to 3 000 chars of the most signal-rich sentences, or '' on failure.
    """
    try:
        resp = requests.get(pdf_url, timeout=25, headers={"User-Agent": "Mozilla/5.0"})
        if resp.status_code != 200:
            return ""
        return _parse_concall_pdf(resp.content)
    except Exception as exc:
        logger.debug("Concall PDF extraction failed for %s: %s", pdf_url, exc)
        return ""


def _parse_concall_pdf(content: bytes) -> str:
    """Extract keyword-bearing sentences from concall PDF bytes."""
    text_pages: list[str] = []
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        for page in pdf.pages[:35]:
            t = page.extract_text() or ""
            text_pages.append(t)

    full_text = "\n".join(text_pages)
    sentences = _CONCALL_KEYWORDS.findall(full_text)

    if sentences:
        excerpt = " ".join(sentences[:20])
    else:
        # Fallback: first 2 000 chars
        excerpt = full_text[:2000]

    return excerpt[:3000].strip()
