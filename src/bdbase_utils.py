# -*- coding: utf-8 -*-
"""
BDbase Scraper - Utility Functions Module
Extracted from BDbaseScraper.py for better code organization
All utility and helper functions are defined here
"""

from __future__ import unicode_literals
import re
import sys

# Python 2/3 compatibility
if sys.version_info[0] >= 3:
    unicode = str

try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse

try:
    from urllib import quote, quote_plus
except ImportError:
    from urllib.parse import quote, quote_plus

# Constants
BASE_DOMAIN = "www.bdbase.fr"
BASE_URL = "https://www.bdbase.fr"

# Pre-compiled regex patterns for better performance
TAG_RE_COMP = re.compile(r'<[^<>]+?>', re.IGNORECASE | re.DOTALL | re.MULTILINE)


def sstr(object):
    """
    Safely converts the given object into a string (sstr = safestr)
    Handles None and unicode strings properly
    """
    if object is None:
        return '<None>'

    if type(object) is str:
        # this is needed, because str() breaks on some strings that have unicode
        # characters, due to a python bug (all strings in python are unicode).
        return object

    return str(object)


def isPositiveInt(value):
    """
    Check if a value can be converted to a positive integer
    """
    try:
        return int(value) >= 0
    except:
        return False


def isnumeric(nNum):
    """
    Check if a value is numeric (can be converted to float)
    """
    try:
        n = float(nNum)
    except ValueError:
        return False
    else:
        return True


def checkWebChar(strIn):
    """
    Decode HTML entities and special characters
    """
    strIn = re.sub('&lt;', '<', strIn)
    strIn = re.sub('&gt;', '>', strIn)
    strIn = re.sub('&amp;', '&', strIn)
    strIn = re.sub('&nbsp;', ' ', strIn)
    strIn = re.sub('<br />', '', strIn)
    strIn = re.sub('&quot;', '"', strIn)
    strIn = re.sub('\x92', '\'', strIn)
    strIn = re.sub('\xc3', u'\xc3', strIn)
    strIn = re.sub('\xa2', u'\xa2', strIn)
    strIn = re.sub('\xc3', u'\xc3', strIn)

    return strIn


def checkRegExp(strIn):
    """
    Escape special regex characters for safe use in regular expressions
    """
    strIn = re.sub('\\(', '.', strIn)
    strIn = re.sub('\\)', '.', strIn)
    strIn = re.sub('&', '&amp;', strIn)
    strIn = re.sub('"', '&quot;', strIn)
    strIn = re.sub(r'\$', r'\\$', strIn)

    return strIn


def strip_tags(html):
    """
    Remove all HTML tags from a string
    """
    try:
        return TAG_RE_COMP.sub("", html)
    except:
        return html


def url_fix(s, charset='utf-8'):
    """
    Fix and encode URL properly for HTTP requests
    """
    if isinstance(s, unicode):
        s = s.encode(charset, 'ignore')

    scheme, netloc, path, qs, anchor = urlparse.urlsplit(s)
    path = quote(path, "%/:=&~#+$!,?;'@()*[]")
    qs = quote_plus(qs, ':&=')

    return urlparse.urlunsplit((scheme, netloc, path, qs, anchor))


def if_else(condition, trueVal, falseVal):
    """
    Simple ternary operator function
    """
    if condition:
        return trueVal
    else:
        return falseVal


def ft(n):
    """
    Convert string flag to boolean (flag-to-bool)
    "1" -> True, "0" -> False, "2" -> "2"
    """
    if n == "1":
        return True
    elif n == "0":
        return False
    elif n == "2":
        return "2"


def tf(bool):
    """
    Convert boolean to string flag (to-flag)
    True -> "1", False -> "0", "2" -> "2"
    """
    if bool == True:
        return "1"
    elif bool == False:
        return "0"
    elif bool == "2":
        return "2"


def GetFullURL(url):
    """
    Convert a relative URL to an absolute URL using BASE_URL
    """
    if url:
        if re.search(r"https?://%s/" % BASE_DOMAIN, url, re.IGNORECASE):
            return url
        else:
            return BASE_URL + "/" + url.lstrip("/")
    else:
        return ''


def is_probable_album_url(url):
    """
    Check if a URL is likely an album URL based on pattern matching
    """
    if not url:
        return False
    url_l = url.lower()
    # Album URLs often contain a numeric part (e.g. -1-, -12-)
    if re.search(r'/bd/[^/]*-\d{1,3}(?:\b|-)\S*', url_l):
        return True
    # Some albums don't have a number but include a tome/volume keyword
    if re.search(r'/bd/[^/]*(tome|volume|vol|integrale|coffret|hors[-\s]?serie|hs)[^/]*', url_l):
        return True
    return False
