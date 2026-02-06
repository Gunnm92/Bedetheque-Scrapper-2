# -*- coding: utf-8 -*-
"""
Utility functions module for BDbase Scraper
Contains text processing, parsing, logging, and HTTP request utilities
"""

from __future__ import unicode_literals
import re
import sys
import os
import urlparse
from urllib import quote, quote_plus
from urllib2 import URLError
from datetime import datetime
import System
from System.Net import DecompressionMethods
from System.Windows.Forms import Application, MessageBox, MessageBoxButtons, MessageBoxIcon, MessageBoxDefaultButton

try:
    unicode
except NameError:
    unicode = str

# These will be imported from config module
from config import (
    BASE_DOMAIN, BASE_URL, CookieContainer, VERSION,
    DBGONOFF, FORMATARTICLES, TITLEIT, ARTICLES, LAST_FIRST_NAMES,
    AcceptGenericArtists, log_messages
)

# Import ComicRack if available
try:
    from cYo.Projects.ComicRack.Engine import ComicRack
except:
    ComicRack = None

# Global variables that need to be accessible
bStopit = False
bError = False

# ========================================
# URL and Web Utilities
# ========================================

def GetFullURL(url):
    """Convert relative URL to absolute URL"""
    if url:
        if re.search(r"https?://%s/" % BASE_DOMAIN, url, re.IGNORECASE):
            return url
        else:
            return BASE_URL + "/" + url.lstrip("/")
    else:
        return ''

def url_fix(s, charset='utf-8'):
    """Fix URL encoding"""
    if isinstance(s, unicode):
        s = s.encode(charset, 'ignore')

    scheme, netloc, path, qs, anchor = urlparse.urlsplit(s)
    path = quote(path, "%/:=&~#+$!,?;'@()*[]")
    qs = quote_plus(qs, ':&=')

    return urlparse.urlunsplit((scheme, netloc, path, qs, anchor))

def _read_url(url, bSingle):
    """Read content from a URL"""
    global bStopit

    page = ''
    if bStopit:
        debuglog("Cancelled from _read_url Start")
        return page

    if not bSingle and re.search(r"https?://%s/" % BASE_DOMAIN, url, re.IGNORECASE):
        bSingle = True

    if bSingle:
        requestUri = url_fix(url)
    else:
        requestUri = url_fix(BASE_URL + "/" + url.lstrip("/"))

    webresponse = None
    inStream = None

    try:
        System.Net.ServicePointManager.SecurityProtocol = System.Net.SecurityProtocolType.Tls12
        Req = System.Net.HttpWebRequest.Create(requestUri)
        Req.CookieContainer = CookieContainer
        Req.Timeout = 15000
        Req.UserAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        Req.AutomaticDecompression = DecompressionMethods.Deflate | DecompressionMethods.GZip
        Req.Referer = requestUri
        Req.Accept = 'text/html, application/xhtml+xml, */*'
        Req.Headers.Add('Accept-Language','fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7')
        Req.KeepAlive = True
        webresponse = Req.GetResponse()

        Application.DoEvents()
        if bStopit:
            debuglog("Cancelled from _read_url End")
            return page

        inStream = webresponse.GetResponseStream()
        encode = System.Text.Encoding.GetEncoding("utf-8")
        ReadStream = System.IO.StreamReader(inStream, encode)
        page = ReadStream.ReadToEnd()

    except URLError as e:
        debuglog("URL Error")
        debuglog("Error: ", e)
        cError = debuglogOnError()
        # Note: dlgName, dlgNumber, dlgAltNumber are global vars from main module
        # log_BD("   [" + dlgName + "] " + dlgNumber + " Alt.No " + dlgAltNumber + " -> " , cError, 1)
        if ComicRack:
            Result = MessageBox.Show(ComicRack.MainWindow, "Error: " + cError, "HTTP Error", MessageBoxButtons.OK, MessageBoxIcon.Warning, MessageBoxDefaultButton.Button1)

    finally:
        if inStream:
            inStream.Close()
        if webresponse:
            webresponse.Close()

    return page

def is_probable_album_url(url):
    """Check if a URL is likely an album page"""
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

# ========================================
# Text Processing Utilities
# ========================================

def remove_accents(raw_text):
    """Remove accents from text"""
    raw_text = re.sub(u"[àáâãäåÀÁÂÄÅÃ]", 'a', raw_text)
    raw_text = re.sub(u"[èéêëÉÈÊË]", 'e', raw_text)
    raw_text = re.sub(u"[çÇ]", 'c', raw_text)
    raw_text = re.sub(u"[ìíîïÍÌÎÏ]", 'i', raw_text)
    raw_text = re.sub(u"[òóôõöÓÒÔÖÕ]", 'o', raw_text)
    raw_text = re.sub(u"[ùúûüÚÙÛÜ]", 'u', raw_text)
    raw_text = re.sub(u"[œŒ]", 'oe', raw_text)
    return raw_text

def normalize_text(raw_text):
    """Normalize text: remove accents, HTML, and convert to lowercase"""
    if not raw_text:
        return ""
    return remove_accents(strip_tags(checkWebChar(raw_text))).lower().strip()

def strip_tags(html):
    """Remove HTML tags from text"""
    try:
        return re.sub("<[^<>]+?>", "", html, flags=re.IGNORECASE | re.DOTALL | re.MULTILINE)
    except:
        return html

def checkWebChar(strIn):
    """Convert HTML entities to characters"""
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
    """Escape special characters for regex"""
    strIn = re.sub('\\(', '.', strIn)
    strIn = re.sub('\\)', '.', strIn)
    strIn = re.sub('&', '&amp;', strIn)
    strIn = re.sub('"', '&quot;', strIn)
    strIn = re.sub('\$', '\\$', strIn)
    return strIn

def sstr(object):
    """Safely converts the given object into a string (safestr)"""
    if object is None:
        return '<None>'

    if type(object) is str:
        # this is needed, because str() breaks on some strings that have unicode
        # characters, due to a python bug (all strings in python are unicode).
        return object

    return str(object)

def write_book_notes(book):
    """Write standard notes to book metadata"""
    book.Notes = "BDbase.fr - " + str(datetime.now().strftime("%A %d %B %Y %H:%M:%S")) + chr(10) + "BDbase scraper v" + VERSION

# ========================================
# Parsing Utilities
# ========================================

def parse_date_fr(raw_text):
    """Parse French date format and return month, year"""
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
    """Extract and parse LD+JSON data from HTML"""
    if not html:
        return None
    try:
        import json
    except:
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
    """Extract album number from title text"""
    if not raw_text:
        return ""
    text = normalize_text(raw_text)
    if re.search(r'\bhors[-\s]?serie\b', text) or re.search(r'\bhs\b', text):
        return "HS"
    if re.search(r'\d+\s*(?:a|à|-)\s*\d+', text):
        return ""
    m = re.search(r'(?:tome|vol|volume|t)\s*([0-9]+)', text)
    if m:
        return m.group(1)
    word_map = {
        "un": "1", "premier": "1",
        "deux": "2", "second": "2",
        "trois": "3", "quatre": "4", "cinq": "5",
        "six": "6", "sept": "7", "huit": "8", "neuf": "9", "dix": "10",
        "onze": "11", "douze": "12"
    }
    m = re.search(r'(?:tome|vol|volume|t)\s*([a-z]+)', text)
    if m and m.group(1) in word_map:
        return word_map[m.group(1)]
    return ""

def is_hors_serie_text(raw_text):
    """Check if text indicates 'hors série' (special issue)"""
    if not raw_text:
        return False
    text = normalize_text(raw_text)
    if re.search(r'\bhors[-\s]?serie\b', text) or re.search(r'\bhs\b', text):
        return True
    return False

def parseName(extractedName):
    """Parse author name (handle Last, First format)"""
    name = extractedName.strip()
    if not AcceptGenericArtists and re.match(r'&lt;', extractedName):
        return ''

    nameRegex = LAST_FIRST_NAMES.search(extractedName)
    if nameRegex:
        name = nameRegex.group('firstname') + ' ' + nameRegex.group('name')

    return checkWebChar(name).strip()

# ========================================
# Validation Utilities
# ========================================

def isnumeric(nNum):
    """Check if value is numeric"""
    try:
        n = float(nNum)
    except ValueError:
        return False
    else:
        return True

def isPositiveInt(value):
    """Check if value is a positive integer"""
    try:
        return int(value) >= 0
    except:
        return False

# ========================================
# Logging Utilities
# ========================================

def debuglog(*args):
    """Log debug messages"""
    try:
        message = u' '.join(unicode(arg) for arg in args)

        if DBGONOFF:
            print(message)
        log_messages.append(message)
    except Exception as e:
        print(e)

def flush_debuglog():
    """Flush debug log to file"""
    try:
        logfile = os.path.join(os.path.dirname(__file__), "BDbase_debug_log.txt")

        with open(logfile, 'a') as log:
            log.write ("\n\n" + str(datetime.now().strftime("%A %d %B %Y %H:%M:%S")) + "\n")
            for message in log_messages:
                log.write(message.encode('utf-8') + "\n")

        del log_messages[:]

    except Exception as e:
        print(e)

def debuglogOnError():
    """Log error information with stack trace"""
    global bError

    traceback = sys.exc_info()[2]
    stackTrace = []

    logfile = (os.path.dirname(__file__) + "/BDbase_debug_log.txt")

    print("Writing Log to " + logfile)
    print('Caught ', sys.exc_info()[0].__name__, ': ', sstr(sys.exc_info()[1]))

    with open(logfile, 'a') as log:
        log.write("\n\n" + str(datetime.now().strftime("%A %d %B %Y %H:%M:%S")) + "\n")
        cError = sstr(sys.exc_info()[1])
        log.write("".join(['Caught ', sys.exc_info()[0].__name__, ': ', cError, '\n']).encode('utf-8'))

        while traceback is not None:
            frame = traceback.tb_frame
            lineno = traceback.tb_lineno
            code = frame.f_code
            filename = code.co_filename
            name = code.co_name
            stackTrace.append((filename, lineno, name))
            traceback = traceback.tb_next

        nL = 0
        for line in stackTrace:
            nL += 1
            print(nL, "-", line)
            log.write(",".join("%s" % tup for tup in line).encode('utf-8') + "\n")

    bError = True

    return cError

def log_BD(bdstr, bdstat, lTime):
    """Log book processing information"""
    bdlogfile = (os.path.dirname(__file__) + "/BDbase_Rename_Log.txt")

    if lTime == 1:
        cDT = str(datetime.now().strftime("%A %d %B %Y %H:%M:%S")) + " > "
    else:
        cDT = ""

    with open(bdlogfile, 'a') as bdlog:
        bdlog.write (cDT.encode('utf-8') + bdstr.encode('utf-8') + "   " + bdstat.encode('utf-8') + "\n")

# ========================================
# Text Formatting Utilities
# ========================================

def cleanARTICLES(s):
    """Remove articles from beginning of string"""
    ns = re.search(r"^(" + ARTICLES.replace(',','|') + ")\s*(?<=['\s])((?=[^/\r\n\(:\,!]*(?:\s[-–]\s))[^-–\r\n]*|.[^/\r\n\(:\,!]*)", s, re.IGNORECASE)
    if ns:
        s = ns.group(2).strip()
    ns2 = re.search(r"^[#]*(.(?=[^/\r\n\(:\,!]*(?:\s[-–]\s))[^-–\r\n]*|.[^/\r\n\(:\,!]*)", s, re.IGNORECASE)
    if ns2:
        s = ns2.group(1).strip()

    return s

def formatARTICLES(s):
    """Format string with articles in parentheses"""
    ns = re.sub(r"^(" + ARTICLES.replace(',','|') + ")\s*(?<=['\s])((?=[^(]*(?:\s[-–:]\s))[^-–:\r\n]*|[^\(/\r\n]*)(?![-–:/\(])\s*([^\r\n]*)", r"\2 (\1) \3", s, re.IGNORECASE)
    if ns:
        s = Capitalize(ns.strip())

    return s

def titlize(s, formatArticles = False):
    """Title case a string with optional article formatting"""
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
        return NewString
    else:
        return s

def Capitalize(s):
    """Capitalize first character of string"""
    ns = s[0:1].upper() + s[1:]
    return ns

# ========================================
# Helper Functions
# ========================================

def if_else(condition, trueVal, falseVal):
    """Ternary operator helper"""
    if condition:
        return trueVal
    else:
        return falseVal

def thread_proc():
    """Thread procedure placeholder"""
    pass

    def handle(w, a):
        pass
