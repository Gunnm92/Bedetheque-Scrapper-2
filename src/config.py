# -*- coding: utf-8 -*-
"""
Configuration module for BDbase Scraper
Contains all global constants, regex patterns, and configuration variables
"""

from __future__ import unicode_literals
import re
import System

# Version
VERSION = "1.00"

# Cookie Container (shared global state)
CookieContainer = System.Net.CookieContainer()

# Basic XML template
BasicXml = "<?xml version=\"1.0\" encoding=\"UTF-8\"?><configuration></configuration>"

# ========================================
# Logging and Debug Configuration
# ========================================
SHOWRENLOG = False
SHOWDBGLOG = False
DBGONOFF = False
DBGLOGMAX = 10000
RENLOGMAX = 10000
log_messages = []

# ========================================
# Language and Localization
# ========================================
LANGENFR = "FR"
ARTICLES = "Le,La,Les,L',The"
FORMATARTICLES = True

# ========================================
# Feature Flags / Checkboxes
# ========================================
CBCover = True
CBStatus = True
CBGenre = True
CBNotes = True
CBWeb = True
ShortWebLink = False
CBCount = True
CBSynopsys = True
CBImprint = True
CBLetterer = True
CBPrinted = True
CBRating = True
CBISBN = True
CBLanguage = True
CBEditor = True
CBFormat = True
CBColorist = True
CBPenciller = True
CBInker = True
CBWriter = True
CBTitle = True
CBSeries = True
CBDefault = False
CBRescrape = False
CBCouverture = True

# ========================================
# Behavior Settings
# ========================================
AllowUserChoice = "2"
PopUpEditionForm = False
SUBPATT = " - - "
COUNTOF = True
COUNTFINIE = True
TITLEIT = True
SerieResumeEverywhere = True
AcceptGenericArtists = True
ONESHOTFORMAT = False
AlwaysChooseSerie = False

# ========================================
# Timing and Timeout
# ========================================
TIMEOUT = "1000"
TIMEOUTS = "7"
TIMEPOPUP = "30"

# ========================================
# Formatting
# ========================================
PadNumber = "0"

# ========================================
# Runtime State Variables
# ========================================
bStopit = False
TimerExpired = False
SkipAlbum = False
Serie_Resume = ""

# ========================================
# BDbase Site Configuration
# ========================================
BASE_DOMAIN = "www.bdbase.fr"
BASE_URL = "https://www.bdbase.fr"
BDBASE_DISABLE_COVER = True

# ========================================
# Regular Expression Patterns
# ========================================

# Nombres auteurs (Author names)
LAST_FIRST_NAMES_PATTERN = r'(?P<name>[^,]*?), (?P<firstname>[^,]*?)$'
LAST_FIRST_NAMES = re.compile(LAST_FIRST_NAMES_PATTERN)

# Info Serie (BDbase)
SERIE_LIST_PATTERN = r'<a\s+href="(/bd/[^"]+)"[^>]*class="card-link"[^>]*>.*?<div\s+class="card-title">(.*?)</div>'

SERIE_URL_PATTERN = r'<a\s+href="(/bd/[^"]+)"[^>]*class="card-link"[^>]*>.*?<div\s+class="card-title">%s\s*?</div>'

SERIE_LANGUE_PATTERN = r'class="flag"/>(.*?)</span>'
SERIE_LANGUE = re.compile(SERIE_LANGUE_PATTERN, re.IGNORECASE)

SERIE_GENRE_PATTERN = r'<span\s+class="serie-genres">(.*?)</span>'
SERIE_GENRE = re.compile(SERIE_GENRE_PATTERN, re.IGNORECASE | re.MULTILINE | re.DOTALL)

SERIE_RESUME_PATTERN = r'<div\s+class="serie-resume">(.+?)</div>'
SERIE_RESUME = re.compile(SERIE_RESUME_PATTERN, re.IGNORECASE | re.MULTILINE | re.DOTALL)

SERIE_STATUS_PATTERN = r'<span\s+class="serie-status[^"]*">(.*?)</span>'
SERIE_STATUS = re.compile(SERIE_STATUS_PATTERN, re.IGNORECASE | re.MULTILINE | re.DOTALL)

SERIE_NOTE_PATTERN = r'<p\sclass="static">Note:\s<strong>\s(?P<note>[^<]*?)</strong>'
SERIE_NOTE = re.compile(SERIE_NOTE_PATTERN, re.IGNORECASE | re.MULTILINE | re.DOTALL)

SERIE_COUNT_PATTERN = r'<div\s+class="group-info">\s*<span>(\d+)\s+albums</span>'
SERIE_COUNT = re.compile(SERIE_COUNT_PATTERN, re.IGNORECASE | re.MULTILINE | re.DOTALL)

SERIE_COUNT_REAL_PATTERN = r'<div\s+class="group-info">(.+?)</div>'
SERIE_COUNT_REAL = re.compile(SERIE_COUNT_REAL_PATTERN, re.IGNORECASE | re.MULTILINE | re.DOTALL)

SERIE_COUNTOF_PATTERN = r'(\d+)\s+albums'
SERIE_COUNTOF = re.compile(SERIE_COUNTOF_PATTERN, re.IGNORECASE | re.MULTILINE | re.DOTALL)

SERIE_HEADER2_PATTERN = r'<h3(.+?)</p'
SERIE_HEADER2 = re.compile(SERIE_HEADER2_PATTERN, re.IGNORECASE | re.MULTILINE | re.DOTALL)

# Info Serie for Quickscrape
SERIE_QSERIE_PATTERN = r'<h1>\s*([^<]+?)\s*</h1>'

# Info Album from Album
ALBUM_TITLE_PATTERN = r'<span\s+class="title-main">(.*?)</span>'

BDBASE_ALBUM_SERIE_PATTERN = r'<label>Série</label>\s*<div>\s*<a\s+href="(/bd/[^"]+)">(.*?)</a>'
BDBASE_ALBUM_SERIE = re.compile(BDBASE_ALBUM_SERIE_PATTERN, re.IGNORECASE | re.DOTALL)

BDBASE_ALBUM_PUBLISHER_PATTERN = r'<label>Éditeur</label>\s*<div>\s*(?:<a[^>]*>)?(.*?)(?:</a>)?\s*</div>'
BDBASE_ALBUM_PUBLISHER = re.compile(BDBASE_ALBUM_PUBLISHER_PATTERN, re.IGNORECASE | re.DOTALL)

BDBASE_ALBUM_COLLECTION_PATTERN = r'<label>Collection</label>\s*<div>\s*(?:<a[^>]*>)?(.*?)(?:</a>)?\s*</div>'
BDBASE_ALBUM_COLLECTION = re.compile(BDBASE_ALBUM_COLLECTION_PATTERN, re.IGNORECASE | re.DOTALL)

BDBASE_ALBUM_RESUME_PATTERN = r'<div\s+class="pre">(.*?)</div>'
BDBASE_ALBUM_RESUME = re.compile(BDBASE_ALBUM_RESUME_PATTERN, re.IGNORECASE | re.DOTALL)

BDBASE_ALBUM_DETAILS_ITEM_PATTERN = r'<li>\s*<label>([^<]+)</label>\s*<div>(.*?)</div>\s*</li>'
BDBASE_ALBUM_DETAILS_ITEM = re.compile(BDBASE_ALBUM_DETAILS_ITEM_PATTERN, re.IGNORECASE | re.DOTALL)

BDBASE_ALBUM_AUTHOR_PATTERN = r'<div\s+class="card-title">\s*<a\s+href="[^"]+"\s+class="card-link">(.*?)</a>\s*</div>\s*<div\s+class="card-text">(.*?)</div>'
BDBASE_ALBUM_AUTHOR = re.compile(BDBASE_ALBUM_AUTHOR_PATTERN, re.IGNORECASE | re.DOTALL)

BDBASE_ALBUM_LIST_PATTERN = r'<a\s+href="(/bd/[^"]+)"[^>]*class="card-link"[^>]*>\s*<div\s+class="card-title">(.*?)</div>(?:\s*<div\s+class="card-text">(.*?)</div>)?'
BDBASE_ALBUM_LIST = re.compile(BDBASE_ALBUM_LIST_PATTERN, re.IGNORECASE | re.DOTALL)

# Info Revues
REVUE_CALC_PATTERN = r'<option\svalue="(.{1,160}?)">%s</'

REVUE_HEADER_PATTERN = r'class="couv"(.{1,100}?couvertures"\shref="(https.{1,150}?)">.{1,600}?class="titre".{1,100}?#(%s)\..+?class="autres".+?)</li>'
REVUE_HEADER_PATTERN_ALT = r'<a name="%s">.+?class="couv"(.{1,100}?couvertures"\shref="(https.{1,150}?)">.+?class="titre".{1,100}?#(.+?)\..+?class="autres".+?)</li>'

REVUE_RESUME_PATTERN = r'<em>Sommaire.*?</em>(.*?)</p'
REVUE_RESUME = re.compile(REVUE_RESUME_PATTERN, re.IGNORECASE | re.MULTILINE | re.DOTALL)

REVUE_PLANCHES_PATTERN = r'>Nb\sPages\s:\s??</label>(.*?)<'
REVUE_PLANCHES = re.compile(REVUE_PLANCHES_PATTERN, re.IGNORECASE | re.MULTILINE | re.DOTALL)

REVUE_DEPOT_PATTERN = r'<label>Parution\s:s??</label>(.*?)</'
REVUE_DEPOT = re.compile(REVUE_DEPOT_PATTERN, re.IGNORECASE | re.MULTILINE | re.DOTALL)

REVUE_PERIOD_PATTERN = r'<label>P.riodicit.\s:\s??</label>(.*?)</'
REVUE_PERIOD = re.compile(REVUE_PERIOD_PATTERN, re.IGNORECASE | re.MULTILINE | re.DOTALL)
