# -*- coding: utf-8 -*-
"""
BDbase Scraper - Text Processing Module
Extracted from BDbaseScraper.py for better code organization
All text processing and French language functions are defined here
"""

from __future__ import unicode_literals
import re
try:
    import json
except:
    json = None

# Import utility functions that text processing depends on
from bdbase_utils import strip_tags, checkWebChar

# Constants for text processing
TITLE_CLEAN_RE = re.compile(
    r'^(?:tome|vol(?:ume)?|t\.?|v\.?|int[ée]grale|coffret|hors[\s-]?s[ée]rie)\s*'
    r'(?:[0-9]+|[ivxlcdm]+)?(?:\s*(?:a|à|au|&|et|\-|–|—)\s*'
    r'(?:[0-9]+|[ivxlcdm]+))?\s*[:\-–—]?\s*',
    re.IGNORECASE
)

# Article handling for title formatting
# These variables can be modified by the importing module
ARTICLES = "Le,La,Les,L',The"
FORMATARTICLES = True
TITLEIT = True


def remove_accents(raw_text):
    """
    Remove French accents from text for normalization
    """
    raw_text = re.sub(u"[àáâãäåÀÁÂÄÅÃ]", 'a', raw_text)
    raw_text = re.sub(u"[èéêëÉÈÊË]", 'e', raw_text)
    raw_text = re.sub(u"[çÇ]", 'c', raw_text)
    raw_text = re.sub(u"[ìíîïÍÌÎÏ]", 'i', raw_text)
    raw_text = re.sub(u"[òóôõöÓÒÔÖÕ]", 'o', raw_text)
    raw_text = re.sub(u"[ùúûüÚÙÛÜ]", 'u', raw_text)
    raw_text = re.sub(u"[œŒ]", 'oe', raw_text)
    return raw_text


def normalize_text(raw_text):
    """
    Normalize text by removing HTML, accents, and converting to lowercase
    """
    if not raw_text:
        return ""
    return remove_accents(strip_tags(checkWebChar(raw_text))).lower().strip()


def parse_date_fr(raw_text):
    """
    Parse French date format (e.g., "15 janvier 2021") and return (month, year)
    Returns (None, None) if parsing fails
    """
    if not raw_text:
        return None, None
    text = normalize_text(raw_text)
    m = re.search(r'(\d{1,2})\s+([a-z]+)\s+(\d{4})', text)
    if not m:
        return None, None
    month_map = {
        "janvier": 1, "fevrier": 2, "mars": 3, "avril": 4,
        "mai": 5, "juin": 6, "juillet": 7, "aout": 8, "septembre": 9,
        "octobre": 10, "novembre": 11, "decembre": 12
    }
    month = month_map.get(m.group(2), None)
    year = int(m.group(3)) if m.group(3) else None
    return month, year


def extract_ld_json(html):
    """
    Extract JSON-LD structured data from HTML
    Returns parsed JSON object or None if not found/invalid
    """
    if not html:
        return None
    if not json:
        return None
    try:
        m = re.search(r'<script[^>]+type="application/ld\+json"[^>]*>(.*?)</script>', html, re.IGNORECASE | re.DOTALL)
        if not m:
            return None
        data = m.group(1).strip()
        return json.loads(data)
    except:
        return None


def extract_number_from_title(raw_text):
    """
    Extract volume/tome number from French BD title
    Returns number as string, "HS" for hors-série, or "" if not found
    """
    if not raw_text:
        return ""
    text = normalize_text(raw_text)
    if re.search(r'\bhors[-\s]?serie\b', text) or re.search(r'\bhs\b', text):
        return "HS"
    if re.search(r'\d+\s*(?:a|à|-)\s*\d+', text):
        return ""
    m = re.search(r'(?:tome|vol|volume|t)[-\s]*([0-9]+)', text)
    if m:
        return m.group(1)
    word_map = {
        "un": "1", "premier": "1",
        "deux": "2", "second": "2",
        "trois": "3", "quatre": "4", "cinq": "5",
        "six": "6", "sept": "7", "huit": "8", "neuf": "9", "dix": "10",
        "onze": "11", "douze": "12"
    }
    m = re.search(r'(?:tome|vol|volume|t)[-\s]*([a-z]+)', text)
    if m and m.group(1) in word_map:
        return word_map[m.group(1)]
    return ""


def is_hors_serie_text(raw_text):
    """
    Check if text indicates a "hors-série" (special edition)
    """
    if not raw_text:
        return False
    text = normalize_text(raw_text)
    if re.search(r'\bhors[-\s]?serie\b', text) or re.search(r'\bhs\b', text):
        return True
    return False


def cleanARTICLES(s):
    """
    Remove articles (Le, La, Les, etc.) from the beginning of series names
    """
    ns = re.search(r"^(" + ARTICLES.replace(',','|') + r")\s*(?<=['\s])((?=[^/\r\n\(:\,!]*(?:\s[-–]\s))[^-–\r\n]*|.[^/\r\n\(:\,!]*)", s, re.IGNORECASE)
    if ns:
        s = ns.group(2).strip()
    ns2 = re.search(r"^[#]*(.(?=[^/\r\n\(:\,!]*(?:\s[-–]\s))[^-–\r\n]*|.[^/\r\n\(:\,!]*)", s, re.IGNORECASE)
    if ns2:
        s = ns2.group(1).strip()

    return s


def formatARTICLES(s):
    """
    Format articles by moving them to parentheses (e.g., "Le Chat" -> "Chat (Le)")
    """
    ns = re.sub(r"^(" + ARTICLES.replace(',','|') + r")\s*(?<=['\s])((?=[^(]*(?:\s[-–:]\s))[^-–:\r\n]*|[^\(/\r\n]*)(?![-–:/\(])\s*([^\r\n]*)", r"\2 (\1) \3", s, re.IGNORECASE)
    if ns:
        s = Capitalize(ns.strip())

    return s


def titlize(s, formatArticles=False):
    """
    Capitalize each word in a title according to configured rules
    Optionally format articles if FORMATARTICLES is enabled
    """
    if formatArticles and FORMATARTICLES:
        s = formatARTICLES(s)

    if TITLEIT:
        NewString = ""
        Ucase = False
        for i in range(len(s.strip())):
            if Ucase or i == 0:
                NewString += s[i:i + 1].upper()
            else:
                NewString += s[i:i + 1]

            if not (s[i:i + 1]).isalnum() and s[i:i + 2].lower() != "'s":
                Ucase = True
            else:
                Ucase = False
        test = s.title()
        return NewString
    else:
        return s


def Capitalize(s):
    """
    Capitalize only the first letter of a string
    """
    ns = s[0:1].upper() + s[1:]
    return ns
