# -*- coding: utf-8 -*-
"""
Scraper module for BDbase Scraper
Contains all the scraping logic for retrieving BD metadata from bdbase.fr
"""
from __future__ import unicode_literals
import re
from datetime import datetime, timedelta
from time import perf_counter as clock
from urllib import quote
from System.Windows.Forms import (
    MessageBox, MessageBoxButtons, MessageBoxIcon, MessageBoxDefaultButton,
    DialogResult, Application
)
from System.IO import FileInfo, File
from System.Diagnostics.Process import Start
from System.Threading import Thread, ThreadStart
from System.Net import HttpWebRequest, Cookie, DecompressionMethods
from System import Math
from System.Drawing import Image
# Import from our modules
import config
from config import *
from utils import *
import settings
from settings import LoadSetting, Trans, Translate
from ui_forms import ProgressBarDialog, SeriesForm, FormType
# Import ComicRack if available
try:
    from cYo.Projects.ComicRack.Engine import ComicRack
except:
    ComicRack = None

# ========================================
# Global Variables (runtime state)

# ========================================
# Book information
dlgName = ""
dlgNumber = ""
dlgAltNumber = ""
AlbumNumNum = False
Shadow1 = False
Shadow2 = False
# Control flags
bStopit = False
SkipAlbum = False
TimerExpired = False
RenameSeries = False
# Results
NewLink = ""
NewSeries = ""
Serie_Resume = ""
# Statistics
nRenamed = 0
nIgnored = 0
# Link storage
LinkBDbase = ""
Numero = ""

# ========================================
# Main Entry Point

# ========================================

def BD_start(books):

    global nRenamed, nIgnored

    settings.aWord = Translate()

    if not LoadSetting():
        return

    bdlogfile = ""
    debuglogfile = ""

    if not books:
        Result = MessageBox.Show(ComicRack.MainWindow, Trans(1),Trans(2), MessageBoxButtons.OK, MessageBoxIcon.Warning, MessageBoxDefaultButton.Button1)
        return

    bdlogfile = (__file__[:-len('BDbaseScraper.py')] + "BDbase_Rename_Log.txt")
    if FileInfo(bdlogfile).Exists and FileInfo(bdlogfile).Length > RENLOGMAX:
        Result = MessageBox.Show(ComicRack.MainWindow, Trans(3), Trans(4), MessageBoxButtons.YesNo, MessageBoxIcon.Question, MessageBoxDefaultButton.Button1)
        if Result == DialogResult.Yes:
            File.Delete(bdlogfile)

    debuglogfile = (__file__[:-len('BDbaseScraper.py')] + "BDbase_debug_log.txt")
    if FileInfo(debuglogfile).Exists and FileInfo(debuglogfile).Length > DBGLOGMAX:
        Result = MessageBox.Show(ComicRack.MainWindow, Trans(5), Trans(6), MessageBoxButtons.YesNo, MessageBoxIcon.Question, MessageBoxDefaultButton.Button1)
        if Result == DialogResult.Yes:
            File.Delete(debuglogfile)

    nRenamed = 0
    nIgnored = 0
    
    if CBRescrape:
        Result = MessageBox.Show(ComicRack.MainWindow, Trans(139), Trans(138), MessageBoxButtons.YesNo, MessageBoxIcon.Question, MessageBoxDefaultButton.Button1)
        if Result == DialogResult.No:
            return

    if books:
        WorkerThread(books)

    else:
        if DBGONOFF:
            print(Trans(15) + "\n")
        log_BD(Trans(15), "", 1)

def WorkerThread(books):

    global AlbumNumNum, dlgNumber, dlgName, dlgNameClean, nRenamed, nIgnored, dlgAltNumber, bError
    global PickSeries, serie_rech_prev, Shadow1, Shadow2, log_messages

    t = Thread(ThreadStart(thread_proc))

    bError = False
    log_messages = []

    Shadow1 = False
    Shadow2 = False

    TimeStart = clock()

    try:

        f = ProgressBarDialog(books.Count)
        f.Show(ComicRack.MainWindow)

        serieUrl = None
        nOrigBooks = books.Count

        log_BD(Trans(7) + str(nOrigBooks) +  Trans(8), "\n============ " + str(datetime.now().strftime("%A %d %B %Y %H:%M:%S")) + " ===========", 0)

        i = 0

        debuglog(chr(10) + "=" * 25 + "- Begin! -" + "=" * 25 + chr(10))

        nTIMEDOUT = 0
        
        nBooks = len(books)
        PickSeries = False
        serie_rech_prev = None

        for book in books:

            TimeBookStart = clock()
            debuglog("v" * 60)

            if bStopit or (nTIMEDOUT == int(TIMEOUT)):
                if bStopit: debuglog("Cancelled from WorkerThread Start")
                return

            nTIMEDOUT += 1

            if book.Number:
                dlgNumber = book.Number
            else:
                dlgNumber = book.ShadowNumber
                Shadow2 = True

            if book.Series:
                dlgName = titlize(book.Series)
            else:
                dlgName = book.ShadowSeries
                Shadow1 = True

            if book.AlternateNumber:
                dlgAltNumber = book.AlternateNumber
            else:
                dlgAltNumber = ""

            dlgNameClean = cleanARTICLES(dlgName)
            dlgName = formatARTICLES(dlgName)

            findCara = dlgName.find(SUBPATT)
            if findCara > 0 :
                lenDlgName = len(dlgName)
                totalchar = lenDlgName - findCara
                dlgName = dlgName[:-totalchar]

            mPos = re.search(r'([.,\\/])', dlgNumber)
            if not isnumeric(dlgNumber):
                albumNum = dlgNumber
                AlbumNumNum = False
            elif isnumeric(dlgNumber) and not re.search(r'[.,\\/]', dlgNumber):
                dlgNumber = str(int(dlgNumber))
                albumNum = str(int(dlgNumber))
                AlbumNumNum = True
            elif mPos:
                nPos = mPos.start(1)
                albumNum = dlgNumber[:nPos]
                dlgAltNumber = dlgNumber[nPos:]
                dlgNumber = albumNum
                AlbumNumNum = True

            f.Update("[" + str(i + 1) + "/" + str(len(books)) + "] : " + dlgName + " - " + dlgNumber + if_else(dlgAltNumber == '', '', ' AltNo.[' + dlgAltNumber + ']') + " - " + titlize(book.Title), 1, book)
            f.Refresh()
            Application.DoEvents()

            if bStopit:
                debuglog("Cancelled from WorkerThread after Update")
                return

            RetAlb = False
            if CBRescrape:
                if book.Web:
                    RetAlb = QuickScrapeBDbase(books, book, book.Web)

            if not CBRescrape:
                debuglog(Trans(9) + dlgName + "\tNo = [" + albumNum + "]" + if_else(dlgAltNumber == '', '', '\tAltNo. = [' + dlgAltNumber + ']'))
                serieUrl = None
                debuglog(Trans(10), dlgName)
                
                RetAlb = False
                serieUrl = GetFullURL(SetSerieId(book, dlgName, albumNum, nBooks))

                if bStopit:
                    debuglog("Cancelled from WorkerThread after SetSerieId return")
                    return

                if serieUrl:
                    RetAlb = True
                    if not '/revue-' in serieUrl: 
                        LongSerie= serieUrl.lower().replace(".html", u'__10000.html')
                        serieUrl = LongSerie
                        
                    if AlbumNumNum:
                        debuglog(Trans(11), albumNum + "]", if_else(dlgAltNumber == '', '', ' - AltNo.: ' + dlgAltNumber))
                    else:
                        debuglog(Trans(12) + albumNum + "]", if_else(dlgAltNumber == '', '', ' - AltNo. [' + dlgAltNumber + ']'))

                    RetAlb = SetAlbumInformation(book, serieUrl, dlgName, albumNum)

                    #SkipAlbum utlisez lorsque l'on appuye sur Annuler (ou AllowUserChoice == 0) dans la fenetre pour choisir l'album ParseSerieInfo
                    if not SkipAlbum and not RetAlb and not '/revue-' in serieUrl:
                        # Only parse when the URL looks like an album page, to avoid mapping series pages
                        if is_probable_album_url(serieUrl):
                            RetAlb = parseAlbumInfo(book, serieUrl, albumNum)
            
            if RetAlb:
                nRenamed += 1
                log_BD("[" + dlgName + "] " + dlgNumber + if_else(dlgAltNumber == '', '', ' AltNo.[' + dlgAltNumber + ']') + " - " + titlize(book.Title), Trans(13), 1)
            else:
                nIgnored += 1
                log_BD("[" + dlgName + "] " + dlgNumber + if_else(dlgAltNumber == '', '', ' AltNo. [' + dlgAltNumber + ']') + " - " + titlize(book.Title), Trans(14) + "\n", 1)

            i += 1

            TimeBookEnd = clock()
            nSec = int(TimeBookEnd - TimeBookStart)
            debuglog(Trans(125), str(timedelta(seconds=nSec)) + chr(10))
            debuglog("^" * 60)

            # timeout in seconds before next scrape
            if TIMEOUTS and nOrigBooks > nIgnored + nRenamed:
                cPause = Trans(140).replace("%%", str(TIMEOUTS))
                f.Update(cPause, 0, False)
                f.Refresh()
                for ii in range(20*int(TIMEOUTS)):
                    t.CurrentThread.Join(50)
                    Application.DoEvents()
                    if bStopit:
                        debuglog("Cancelled from WorkerThread TIMEOUT Loop")
                        return
            if bStopit:
                debuglog("Cancelled from WorkerThread End")
                return

    except:
        cError = debuglogOnError()
        log_BD("   [" + dlgName + "] " + dlgNumber + " - " + titlize(book.Title), cError, 1)
        if f:
            f.Close()
            t.Abort()
        return

    finally:
        f.Update(Trans(16), 1, book)
        f.Refresh()
        #Application.DoEvents()
        f.Close()

        log_BD("\n" + Trans(17) + str(nRenamed) , "", 0)
        log_BD(Trans(18) + str(nIgnored), "", 0)
        log_BD("============= " + str(datetime.now().strftime("%A %d %B %Y %H:%M:%S")) + " =============", "\n\n", 0)

        TimeEnd = clock()
        nSec = int(TimeEnd - TimeStart)
        debuglog(Trans(124), str(timedelta(seconds=nSec)) )
        debuglog("=" * 25 + "- End! -" + "=" * 25 + chr(10))
        flush_debuglog()

        if bError and SHOWDBGLOG:
            rdlg = MessageBox.Show(ComicRack.MainWindow, Trans(17) + str(nRenamed) + ", " + Trans(18) + str(nIgnored) + ", (" + Trans(108) + str(nOrigBooks) + ")\n\n" + Trans(19), Trans(20), MessageBoxButtons.YesNo, MessageBoxIcon.Warning, MessageBoxDefaultButton.Button1)
            if rdlg == DialogResult.Yes:
                # open debug log automatically
                if FileInfo(__file__[:-len('BDbaseScraper.py')] + "BDbase_debug_log.txt"):
                    Start(__file__[:-len('BDbaseScraper.py')] + "BDbase_debug_log.txt")
        elif SHOWRENLOG:
            rdlg = MessageBox.Show(ComicRack.MainWindow, Trans(17) + str(nRenamed) + ", " + Trans(18) + str(nIgnored) + ", (" + Trans(108) + str(nOrigBooks) + ")\n\n" + Trans(21), Trans(22), MessageBoxButtons.YesNo, MessageBoxIcon.Question, MessageBoxDefaultButton.Button1)
            if rdlg == DialogResult.Yes:
                # open rename log automatically
                if FileInfo(__file__[:-len('BDbaseScraper.py')] + "BDbase_Rename_Log.txt"):
                    Start(__file__[:-len('BDbaseScraper.py')] + "BDbase_Rename_Log.txt")
        else:

            rdlg = MessageBox.Show(ComicRack.MainWindow, Trans(17) + str(nRenamed) + ", " + Trans(18) + str(nIgnored) + " (" + Trans(108) + str(nOrigBooks) + ")" , Trans(22), MessageBoxButtons.OK, MessageBoxIcon.Exclamation, MessageBoxDefaultButton.Button1)            

        t.Abort()

        return

# ========================================
# Serie Information Functions

# ========================================

def parseSerieInfo(book, serieUrl, lDirect=False):
    """
    Parse series information from bdbase.fr
    Args:
        book: ComicRack book object
        serieUrl: URL of the series page
        lDirect: If True, direct scrape mode
    Returns:
        str: URL for next step, or False on error
    """
    global Serie_Resume, SkipAlbum
    debuglog("=" * 60)
    debuglog("parseSerieInfo", "a)", serieUrl, "b)", lDirect)
    debuglog("=" * 60)
    SERIE_QSERIE = re.compile(SERIE_QSERIE_PATTERN, re.IGNORECASE | re.MULTILINE | re.DOTALL)
    SkipAlbum = False
    albumURL = ''
    if bStopit:
        debuglog("Cancelled from parseSerieInfo Start")
        return False
    try:
        request = _read_url(serieUrl, lDirect)
    except:
        cError = debuglogOnError()
        log_BD("   " + serieUrl + " " + Trans(43), "", 1)
        return False
    if bStopit:
        debuglog("Cancelled from parseSerieInfo after _read_url return")
        return False
    if '/revue-' in serieUrl:
        i = 1
        ListAlbum = list()
        REVUE_LIST_ALL = re.findall(r"<option\svalue=\"(https://www\.bdbase\.fr/revue-[^>]+?)\">(.+?)</option>", request, re.IGNORECASE | re.DOTALL | re.MULTILINE)
        # When only 1 page
        if not REVUE_LIST_ALL or len(REVUE_LIST_ALL) == 0:
            REVUE_LIST_ALL_ALT = re.findall(r'<a name="(.+?)">.+?class="titre".{1,100}?#(.+?)\..+?', request, re.IGNORECASE | re.DOTALL | re.MULTILINE)
            for revueNum in REVUE_LIST_ALL_ALT:
                full_url = serieUrl + "#" + revueNum[0] if BASE_DOMAIN in serieUrl.lower() else BASE_URL + "/" + serieUrl.lstrip("/") + "#" + revueNum[0]
                ListAlbum.append([full_url, "Num: " + revueNum[1].strip(), str(i).zfill(5)])
                i = i + 1
        else:
            for albumPick in REVUE_LIST_ALL:
                ListAlbum.append([albumPick[0], "Num: " + albumPick[1].strip(), str(i).zfill(5)])
                i = i + 1
        matchedAlbum = next((x for x in ListAlbum if x[1] == "Num: " + dlgNumber), None)  # find num in list
        if matchedAlbum is not None and not lDirect:
            albumURL = matchedAlbum[0]
        elif lDirect and '#' in serieUrl:
            albumURL = serieUrl
        else:
            albumURL = AlbumChooser(ListAlbum)
        if not albumURL:
            return ""
        request = _read_url(albumURL, False)
        ID = albumURL.split('#')[1] if '#' in albumURL else ''
        if ID:
            REVUE_HEADER = re.compile(REVUE_HEADER_PATTERN_ALT % ID, re.IGNORECASE | re.MULTILINE | re.DOTALL)
        else:
            REVUE_HEADER = re.compile(REVUE_HEADER_PATTERN % dlgNumber, re.IGNORECASE | re.MULTILINE | re.DOTALL)
        SerieInfoRegex = REVUE_HEADER.search(request)
        if SerieInfoRegex:
            RetVal = parseRevueInfo(book, SerieInfoRegex, albumURL)
            return RetVal
        else:
            return ""
    else:
        if request:
            Entete = request
            if RenameSeries:
                if CBSeries:
                    book.Series = titlize(RenameSeries)
            # Series if Quickscrape
            if lDirect and CBSeries:
                nameRegex = SERIE_QSERIE.search(Entete)
                if nameRegex:
                    qserie = checkWebChar(nameRegex.group(1).strip())
                    book.Series = titlize(qserie)
                    debuglog(Trans(9), qserie)
                else:
                    albumURL = False
                    return ""
            # genre
            if CBGenre:
                genres = []
                for gblock in SERIE_GENRE.findall(Entete):
                    for g in re.findall(r'<a[^>]*>(.*?)</a>', gblock, re.IGNORECASE | re.DOTALL):
                        gname = checkWebChar(strip_tags(g)).strip()
                        if gname and gname not in genres:
                            genres.append(gname)
                if genres:
                    book.Genre = ", ".join(genres)
                    # Flag Erotique/Érotique genre as PG
                    if 'rotique' in book.Genre.lower():
                        book.AgeRating = "PG"
                debuglog(Trans(51), book.Genre)
            # Resume (series summary may be missing on BDbase)
            if CBSynopsys:
                nameRegex = SERIE_RESUME.search(checkWebChar(Entete.replace("\r\n","")), 0)
                if nameRegex:
                    resume = strip_tags(nameRegex.group(1)).strip()
                else:
                    resume = ""
                Serie_Resume = (checkWebChar(resume)).strip()
                cResume = if_else(resume, Trans(52), Trans(53))
                debuglog(cResume)
            # fini
            if CBStatus:
                SerieState = ""
                nameRegex = SERIE_STATUS.search(Entete)
                if nameRegex:
                    fin = checkWebChar(strip_tags(nameRegex.group(1)).strip())
                    log_BD(fin, Trans(25), 1)
                else:
                    fin = ""
                fin_norm = normalize_text(fin)
                if ("complete" in fin_norm) or ("termine" in fin_norm) or (dlgNumber.lower() == "one shot"):
                    book.SeriesComplete = YesNo.Yes
                    SerieState = Trans(54)
                elif ("one shot" in fin_norm) and (dlgNumber.lower() != "one shot"):
                    book.SeriesComplete = YesNo.Yes
                    if ONESHOTFORMAT and not CBFormat:
                        book.Format = "One Shot"
                    SerieState = Trans(54)
                elif ("cours" in fin_norm):
                    book.SeriesComplete = YesNo.No
                    SerieState = Trans(55)
                else:
                    book.SeriesComplete = YesNo.Unknown
                    SerieState = Trans(56)
                debuglog(Trans(57) + SerieState + if_else(dlgNumber.lower() == "one shot", " (One Shot)", ""))
            # Language
            if CBLanguage and not book.LanguageISO:
                book.LanguageISO = "fr"
            # Default Values
            if not CBDefault:
                book.EnableProposed = YesNo.No
                debuglog(Trans(136), "No")
            # Number of...
            if CBCount and not lDirect:
                count = 0
                cCountText = ""
                if COUNTFINIE and book.SeriesComplete == YesNo.No:
                    book.Count = -1
                    cCountText = "---"
                elif not COUNTOF:
                    nameRegex = SERIE_COUNT.search(Entete)
                    if nameRegex and AlbumNumNum:
                        count = checkWebChar(nameRegex.group(1))
                        book.Count = int(count)
                        cCountText = str(int(count))
                    else:
                        book.Count = -1
                        cCountText = "---"
                else:
                    nameRegex = SERIE_COUNT_REAL.search(request)
                    if nameRegex:
                        for numof in SERIE_COUNTOF.finditer(nameRegex.group(1)):
                            if isnumeric(numof.group(1)) and int(numof.group(1)) > count:
                                count = int(numof.group(1))
                        if count > 0 and AlbumNumNum:
                            book.Count = int(count)
                            cCountText = str(int(count))
                        elif not AlbumNumNum:
                            book.Count = -1
                    else:
                        book.Count = -1
                        cCountText = "---"
                debuglog(Trans(59) + if_else(dlgNumber.lower() == "one shot", "1", cCountText))
            i = 0
            ListAlbumAll = list()
            for r in BDBASE_ALBUM_LIST.finditer(request):
                url = r.group(1)
                title_main = checkWebChar(strip_tags(r.group(2))).strip()
                title_sub = checkWebChar(strip_tags(r.group(3))).strip() if r.group(3) else ""
                num = extract_number_from_title(title_main)
                if not num and title_sub:
                    num = extract_number_from_title(title_sub)
                if not num and url:
                    mnum = re.search(r'-([0-9]{1,3})(?:|-)', url)
                    if mnum:
                        num = mnum.group(1)
                label = title_main + if_else(title_sub, " - " + title_sub, "")
                ListAlbumAll.append([url, label, str(i).zfill(3), num, title_main, title_sub])
                i = i + 1
            if len(ListAlbumAll) == 0:
                return ""
            matched = None
            if dlgNumber != "" and not lDirect:
                num_norm = dlgNumber.lstrip("0")
                for a in ListAlbumAll:
                    if a[3] and a[3].lstrip("0") == num_norm:
                        matched = a
                        break
            if not matched and book.Title:
                t_norm = normalize_text(book.Title)
                for a in ListAlbumAll:
                    if normalize_text(a[4]) == t_norm or normalize_text(a[5]) == t_norm:
                        matched = a
                        break
            if matched:
                albumURL = matched[0]
            else:
                ListAlbum = [[a[0], a[1], a[2]] for a in ListAlbumAll]
                albumURL = AlbumChooser(ListAlbum)
                if not albumURL and not SkipAlbum and ListAlbumAll:
                    albumURL = ListAlbumAll[0][0]
    return albumURL

def SetSerieId(book, serie, num, nBooksIn):

    global ListSeries, NewLink, NewSeries, RenameSeries, PickSeries, PickSeriesLink, serie_rech_prev
    
    if not serie:
        return ""

    RenameSeries = False

    try:
        serie_rech = remove_accents(serie.lower())
        if serie_rech == serie_rech_prev and PickSeries != False:
            serie_rech_prev = serie_rech
            RenameSeries = PickSeries
            return PickSeriesLink
        else:
            serie_rech_prev = serie_rech
            PickSeries = False

        ListSeries = list()
        debuglog("Nom de Série pour recherche = " + dlgNameClean)
        query = quote(remove_accents(dlgNameClean.lower().strip()).encode('utf-8'))
        urlN = '/recherche-series?type=bd&sch=' + query

        debuglog(Trans(113), BASE_DOMAIN + urlN)

        request = _read_url(urlN.encode('utf-8'), False)

        if bStopit:
            debuglog("Cancelled from SetSerieId after Search return")
            return ''

        if not request:
            return ''

        i = 1
        RegCompile = re.compile(SERIE_LIST_PATTERN, re.IGNORECASE | re.DOTALL)
        for seriepick in RegCompile.finditer(request):
            ListSeries.append([seriepick.group(1), checkWebChar(strip_tags(seriepick.group(2))), str(i).zfill(3)])
            i = i + 1

        ListSeries.sort(key=operator.itemgetter(2))

        if len(ListSeries) == 1 and not AlwaysChooseSerie:
            debuglog(Trans(24) + checkWebChar(serie) + "]" )
            debuglog(Trans(111) + (ListSeries[0][1]))
            log_BD("** [" + serie + "] " + num + if_else(dlgAltNumber == '', '', ' AltNo. ' + dlgAltNumber) + " - " + titlize(book.Title) + " (" + BASE_DOMAIN + ListSeries[0][0] + ")", Trans(25), 1)
            log_BD(Trans(111), "[" + ListSeries[0][1] + "] " + num + if_else(dlgAltNumber == '', '', ' AltNo. ' + dlgAltNumber) + " - " + titlize(book.Title) + " (" + BASE_DOMAIN + ListSeries[0][0] + ")", 1)
            RenameSeries = ListSeries[0][1]
            return ListSeries[0][0]

        elif len(ListSeries) > 1 or (AlwaysChooseSerie and len(ListSeries) >= 1) :
            if AllowUserChoice or nBooksIn == 1:
                lUnique = False
                for i in range(len(ListSeries)):
                    if remove_accents(ListSeries[i][1].lower()) == remove_accents(dlgName.lower().strip()):
                        lUnique = True
                        nItem = i
                    if remove_accents(ListSeries[i][1].lower()) == remove_accents(dlgName.lower().strip()) and re.search(r'\(.{4,}?\)', ListSeries[i][1].lower()):
                        lUnique = False
                    if AlwaysChooseSerie:
                        lUnique = False
                if lUnique:
                    debuglog(Trans(24) + checkWebChar(serie) + "]" )
                    debuglog(Trans(111) + (ListSeries[nItem][1]))
                    log_BD("** [" + serie + "] " + num + if_else(dlgAltNumber == '', '', ' AltNo. ' + dlgAltNumber) + " - " + titlize(book.Title) + " (" + BASE_DOMAIN + ListSeries[nItem][0] + ")", Trans(25), 1)
                    log_BD(Trans(111), "[" + ListSeries[nItem][1] + "] " + num + if_else(dlgAltNumber == '', '', ' AltNo. ' + dlgAltNumber) + " - " + titlize(book.Title) + " (" + BASE_DOMAIN + ListSeries[nItem][0] + ")", 1)
                    RenameSeries = ListSeries[nItem][1]
                    return ListSeries[nItem][0]
                # Pick a series
                NewLink = ''
                NewSeries = ''
                a = ListSeries
                pickAseries = SeriesForm(serie, ListSeries, FormType.SERIE)
                result = pickAseries.ShowDialog()

                if result == DialogResult.Cancel:
                    debuglog(Trans(24) + checkWebChar(serie) + "]")
                    log_BD("** [" + serie + "] " + num + if_else(dlgAltNumber == '', '', ' AltNo. ' + dlgAltNumber) + " - " + titlize(book.Title) + " (" + BASE_DOMAIN + ")", Trans(25), 1)
                    return ''
                else:
                    debuglog(Trans(24) + checkWebChar(serie) + "]")
                    debuglog(Trans(111) + (NewSeries))
                    log_BD("** [" + serie + "] " + num + if_else(dlgAltNumber == '', '', ' AltNo. ' + dlgAltNumber) + " - " + titlize(book.Title) + " (" + BASE_DOMAIN + ")", Trans(25), 1)
                    log_BD(Trans(111), "[" + NewSeries + "] " + num + if_else(dlgAltNumber == '', '', ' AltNo. ' + dlgAltNumber) + " - " + titlize(book.Title) + " (" + BASE_DOMAIN + NewLink + ")", 1)
                    RenameSeries = NewSeries
                    PickSeries = RenameSeries
                    PickSeriesLink = NewLink
                    return NewLink
            else:
                debuglog(Trans(142) + checkWebChar(serie) + "]")
                log_BD("** [" + serie + "] " + num + if_else(dlgAltNumber == '', '', ' AltNo. ' + dlgAltNumber) + " - " + titlize(book.Title) + " (" + BASE_DOMAIN + ")", Trans(25), 1)
                return ''

    except:

        cError = debuglogOnError()
        log_BD("** Error [" + serie + "] " + num + " - " + titlize(book.Title), cError, 1)

    return serieUrl

# ========================================
# Album Information Functions

# ========================================

def parseAlbumInfo(book, pageUrl, num, lDirect=False):
    """
    Parse album information from bdbase.fr
    Args:
        book: ComicRack book object
        pageUrl: URL of the album page
        num: Album number
        lDirect: If True, direct scrape mode
    Returns:
        bool: True if successful
    """
    global CBelid, NewLink, NewSeries
    debuglog("=" * 60)
    debuglog("parseAlbumInfo", "a)", pageUrl, "b)", num, "c)", lDirect)
    debuglog("=" * 60)
    if bStopit:
        debuglog("Cancelled from parseAlbumInfo Start")
        return False
    albumHTML = _read_url(pageUrl, False)
    if bStopit:
        debuglog("Cancelled from parseAlbumInfo after _read_url return")
        return False
    if BASE_DOMAIN in pageUrl.lower() or 'class="book-details-container"' in albumHTML:
        return parseAlbumInfo_bdbase(book, pageUrl, num, albumHTML)
    debuglog("Unsupported album page format: " + pageUrl)
    return False

def parseAlbumInfo_bdbase(book, pageUrl, num, albumHTML):
    """
    Parse album information from BDbase HTML
    Args:
        book: ComicRack book object
        pageUrl: URL of the album page
        num: Album number
        albumHTML: HTML content of the page
    Returns:
        bool: True if successful
    """
    global Serie_Resume
    try:
        # Series
        serie_name = ""
        serie_match = BDBASE_ALBUM_SERIE.search(albumHTML)
        if serie_match:
            serie_name = checkWebChar(strip_tags(serie_match.group(2))).strip()
            if CBSeries:
                book.Series = titlize(serie_name)
                debuglog(Trans(9), book.Series)
        # Title
        raw_title_main = ""
        title_main = ""
        m_title = re.search(ALBUM_TITLE_PATTERN, albumHTML, re.IGNORECASE | re.DOTALL)
        if m_title:
            raw_title_main = checkWebChar(strip_tags(m_title.group(1))).strip()
        m_title_sub = re.search(r'<span\s+class="title">([^<]+)</span>', albumHTML, re.IGNORECASE | re.DOTALL)
        if m_title_sub:
            title_main = checkWebChar(strip_tags(m_title_sub.group(1))).strip()
        else:
            title_main = raw_title_main
            if serie_name and normalize_text(title_main).startswith(normalize_text(serie_name)):
                title_main = title_main[len(serie_name):].strip(" :-–")
        hs_flag = is_hors_serie_text(raw_title_main) or is_hors_serie_text(title_main) or is_hors_serie_text(pageUrl)
        if not hs_flag:
            # Drop leading volume markers to keep the true title
            title_main = re.sub(r'^(?:tome|vol(?:ume)?|t\.?|v\.?|int[ée]grale|coffret|hors[\s-]?s[ée]rie)\s*(?:[0-9]+|[ivxlcdm]+)?(?:\s*(?:a|à|au|&|et|\-|–|—)\s*(?:[0-9]+|[ivxlcdm]+))?\s*[:\-–—]?\s*', '', title_main, flags=re.IGNORECASE).strip()
        if CBTitle and title_main:
            if book.Series and title_main.lower() == book.Series.lower():
                book.Title = ""
            else:
                book.Title = titlize(title_main)
            debuglog(Trans(29), book.Title)
        # Numbers
        og_title = ""
        m_og = re.search(r'property="og:title"\s+content="([^"]+)"', albumHTML, re.IGNORECASE)
        if m_og:
            og_title = checkWebChar(strip_tags(m_og.group(1))).strip()
        num_from_title = extract_number_from_title(raw_title_main or og_title or title_main or book.Title)
        if hs_flag:
            book.Number = "HS"
            book.AlternateNumber = ""
        else:
            book.Number = num if num else num_from_title
            book.AlternateNumber = dlgAltNumber if dlgAltNumber else book.AlternateNumber
        debuglog("Num: ", book.Number)
        debuglog("Alt: ", book.AlternateNumber)
        # Web
        if CBWeb == True and not CBRescrape:
            book.Web = GetFullURL(pageUrl)
            debuglog(Trans(123), book.Web)
        # Publisher
        if CBEditor:
            m_pub = BDBASE_ALBUM_PUBLISHER.search(albumHTML)
            if m_pub:
                book.Publisher = checkWebChar(strip_tags(m_pub.group(1))).strip()
            else:
                book.Publisher = ""
            debuglog(Trans(35), book.Publisher)
        # Collection
        if CBImprint:
            m_col = BDBASE_ALBUM_COLLECTION.search(albumHTML)
            if m_col:
                book.Imprint = checkWebChar(strip_tags(m_col.group(1))).strip()
            else:
                book.Imprint = ""
            debuglog(Trans(41), book.Imprint)
        # Summary
        if CBSynopsys:
            m_resume = BDBASE_ALBUM_RESUME.search(albumHTML)
            if m_resume:
                resume = strip_tags(m_resume.group(1)).strip()
                summary = if_else(book.Title, '>' + book.Title + '< ' + chr(10), "") + resume
                if summary:
                    book.Summary = summary
                    debuglog(Trans(100))
            else:
                debuglog(Trans(101))
        # Details
        details = {}
        for d in BDBASE_ALBUM_DETAILS_ITEM.finditer(albumHTML):
            key = normalize_text(d.group(1))
            val = checkWebChar(strip_tags(d.group(2))).strip()
            if key:
                details[key] = val
        # Fallback: use details for publisher when available
        if CBEditor and not book.Publisher and details.get("editeur"):
            book.Publisher = details.get("editeur")
            debuglog(Trans(35), book.Publisher)
        if CBPrinted and details.get("date de parution"):
            month, year = parse_date_fr(details.get("date de parution"))
            if month and year:
                book.Month = int(month)
                book.Year = int(year)
                debuglog(Trans(34), str(book.Month) + "/" + str(book.Year))
            else:
                book.Month = -1
                book.Year = -1
        if CBISBN and details.get("isbn"):
            book.ISBN = details.get("isbn")
            debuglog("ISBN: ", book.ISBN)
        # LD+JSON fallback for missing details
        ld = extract_ld_json(albumHTML)
        if isinstance(ld, list):
            # find first WebPage with mainEntity
            for item in ld:
                if isinstance(item, dict) and item.get('@type') == 'WebPage' and item.get('mainEntity'):
                    ld = item
                    break
        book_data = None
        if isinstance(ld, dict):
            book_data = ld.get('mainEntity') if ld.get('@type') == 'WebPage' else ld
        if isinstance(book_data, dict):
            if CBPrinted and (book.Year == -1 or not book.Year):
                dp = book_data.get('datePublished')
                if dp and isinstance(dp, str) and '-' in dp:
                    parts = dp.split('-')
                    if len(parts) >= 2:
                        try:
                            book.Year = int(parts[0])
                            book.Month = int(parts[1])
                        except:
                            pass
            if CBCount and (not book.PageCount or book.PageCount == 0):
                pages = book_data.get('numberOfPages')
                if pages and str(pages).isdigit():
                    book.PageCount = int(pages)
            if CBEditor and not book.Publisher:
                pub = book_data.get('publisher')
                if isinstance(pub, dict):
                    pub = pub.get('name')
                if pub:
                    book.Publisher = checkWebChar(strip_tags(str(pub))).strip()
            if CBISBN and not book.ISBN:
                isbn = book_data.get('isbn') or book_data.get('isbn13')
                if isbn:
                    book.ISBN = checkWebChar(strip_tags(str(isbn))).strip()
        if CBFormat:
            fmt_parts = []
            if details.get("couverture"):
                fmt_parts.append(details.get("couverture"))
            if details.get("dimensions"):
                fmt_parts.append(details.get("dimensions"))
            book.Format = " - ".join(fmt_parts) if fmt_parts else ""
            debuglog(Trans(42), book.Format)
        if details.get("pages") and not book.FilePath:
            if details.get("pages").isdigit():
                book.PageCount = int(details.get("pages"))
            else:
                book.PageCount = 0
            debuglog(Trans(122), book.PageCount)
        illustrations = details.get("illustrations") or details.get("illustations")
        if CBColorist and illustrations:
            if 'n&b' in normalize_text(illustrations):
                book.BlackAndWhite = YesNo.Yes
            else:
                book.BlackAndWhite = YesNo.No
        # Authors
        authors = extract_authors_from_html(albumHTML)
        if CBWriter and authors["Writer"]:
            book.Writer = ", ".join(authors["Writer"])
            debuglog(Trans(30), book.Writer)
        if CBPenciller and authors["Penciller"]:
            book.Penciller = ", ".join(authors["Penciller"])
            debuglog(Trans(31), book.Penciller)
        if CBColorist and authors["Colorist"]:
            book.Colorist = ", ".join(authors["Colorist"])
            debuglog(Trans(33), book.Colorist)
        if CBInker and authors["Inker"]:
            book.Inker = ", ".join(authors["Inker"])
            debuglog(Trans(73), book.Inker)
        if CBCouverture and authors["CoverArtist"]:
            book.CoverArtist = ", ".join(authors["CoverArtist"])
            debuglog(Trans(121), book.CoverArtist)
        if CBLetterer and authors["Letterer"]:
            book.Letterer = ", ".join(authors["Letterer"])
            debuglog(Trans(38), book.Letterer)
        # Language
        if CBLanguage and not book.LanguageISO:
            book.LanguageISO = "fr"
        # Cover Image — extraire l'URL via og:image et télécharger
        if CBCover and not book.FilePath and not BDBASE_DISABLE_COVER:
            coverMatch = re.search(r'<meta\s+property="og:image"\s+content="([^"]+)"', albumHTML, re.IGNORECASE)
            if coverMatch:
                download_cover(book, coverMatch.group(1))
        if CBNotes:
            write_book_notes(book)
    except:
        cError = debuglogOnError()
        log_BD("   " + pageUrl + " " + Trans(43), "", 1)
        return False
    return True

def SetAlbumInformation(book, serieUrl, serie, num):
    """
    Set album information after successful scraping
    Args:
        book: ComicRack book object
        serieUrl: Series URL
        serie: Series name
        num: Album number
    Returns:
        bool: True if successful
    """
    albumUrl = parseSerieInfo(book, serieUrl, False)
    if bStopit:
        debuglog("Cancelled from SetAlbumInformation")
        return False
    if albumUrl and not '/revue-' in serieUrl:
        debuglog(Trans(26), albumUrl)
        if not parseAlbumInfo(book, albumUrl, num):
            return False
        return True
    elif '/revue-' in serieUrl:
        return albumUrl
    else:
        debuglog(Trans(26), Trans(25))
        debuglog(Trans(27) + serie + "] " + num + if_else(dlgAltNumber == '', '', ' AltNo.' + dlgAltNumber) + "\n")
        log_BD("   [" + serie + "] " + num + if_else(dlgAltNumber == '', '', ' AltNo.' + dlgAltNumber) + " - " + titlize(book.Title) + " (" + BASE_DOMAIN + serieUrl + ")", Trans(28), 1)
        return False

# ========================================
# Album Selection Functions

# ========================================

def AlbumChooser(ListAlbum):
    """
    Show dialog for user to choose an album from multiple matches
    Args:
        ListAlbum: List of album options
    Returns:
        Selected album URL or None
    """
    global NewLink, SkipAlbum
    albumURL = ""
    debuglog("Nbr. d'item dans la Liste Album est de: " + str(len(ListAlbum)))
    if len(ListAlbum) > 1:
        if AllowUserChoice:
            NewLink = ""
            NewSeries = ""
            pickAnAlbum = SeriesForm(dlgNumber, ListAlbum, FormType.ALBUM)
            result = pickAnAlbum.ShowDialog()
            if result == DialogResult.Cancel:
                if TIMEPOPUP != "0" and TimerExpired:
                    albumURL = ListAlbum[0][0]
                    debuglog("---> Le temps est expiré, choix du 1er item")
                else:
                    albumURL = False
                    SkipAlbum = True
                    debuglog("---> Appuyer sur Cancel, ignorons ce livre")
            else:
                albumURL = NewLink
        else:
            albumURL = False
            SkipAlbum = True
            debuglog("---> Plus d'un item mais l'option pause scrape est désactivé")
    elif len(ListAlbum) == 1:
        albumURL = ListAlbum[0][0]
        debuglog("---> Seulement 1 item dans la liste")
    return albumURL

# ========================================
# Revue (Magazine) Functions

# ========================================

def parseRevueInfo(book, SerieInfoRegex, serieUrl, Numero="", serie=""):
    """
    Parse magazine/revue information
    Args:
        book: ComicRack book object
        SerieInfoRegex: Regex match for series info
        serieUrl: Series URL
        Numero: Issue number
        serie: Series name
    Returns:
        bool: True if successful
    """
    debuglog("=" * 60)
    debuglog("parseRevueInfo", "a)", serieUrl, "b)", Numero)
    debuglog("=" * 60)
    try:
        Entete = SerieInfoRegex.group(1)
        Numero = SerieInfoRegex.group(3) if not Numero else Numero
        if RenameSeries:
            if CBSeries:
                book.Series = titlize(RenameSeries)
        else:
            if CBSeries:
                book.Series = titlize(book.Series)
        if Numero:
            try:
                book.Number = Numero
                debuglog(Trans(115), book.Number)
            except:
                book.Number = ""
        if serie:
            try:
                if serie.group(1):
                    if CBSeries:
                        book.Series = titlize(serie.group(1))
                        debuglog(Trans(9), titlize(book.Series))
            except:
                pass
        # Title
        if CBTitle:
            nameRegex = re.search(r'<h3 class="titre".+?</span>(.+?)</h3>', Entete, re.IGNORECASE | re.DOTALL | re.MULTILINE)
            if nameRegex:
                book.Title = titlize(nameRegex.group(1).strip())
            debuglog(Trans(29), book.Title)
        # genre
        if CBGenre:
            book.Genre = "Revue"
            debuglog(Trans(51), book.Genre)
        # Resume
        if CBSynopsys:
            nameRegex = REVUE_RESUME.search(Entete)
            if nameRegex:
                resume = strip_tags(nameRegex.group(1)).strip()
            else:
                resume = ""
            book.Summary = (checkWebChar(resume)).strip()
            cResume = if_else(resume, Trans(52), Trans(53))
            debuglog(cResume)
        # Notes-Rating
        if CBRating:
            nameRegex = SERIE_NOTE.search(Entete)
            if nameRegex:
                note = nameRegex.group('note')
            else:
                note = "0.0"
            book.CommunityRating = float(note)
            debuglog(Trans(58) + str(float(note)))
        # Couverture (fileless only)
        if CBCover and not book.FilePath and not BDBASE_DISABLE_COVER:
            CoverImg = SerieInfoRegex.group(2)
            request = HttpWebRequest.Create(CoverImg)
            response = request.GetResponse()
            response_stream = response.GetResponseStream()
            retval = Image.FromStream(response_stream)
            ComicRack.App.SetCustomBookThumbnail(book, retval)
            debuglog(Trans(105), CoverImg)
        # Parution
        if CBPrinted:
            nameRegex = REVUE_DEPOT.search(Entete, 0)
            if nameRegex:
                if nameRegex.group(1) != '-':
                    book.Month = int(nameRegex.group(1)[3:5])
                    book.Year = int(nameRegex.group(1)[6:10])
                    debuglog(Trans(34), str(book.Month) + "/" + str(book.Year))
                else:
                    book.Month = -1
                    book.Year = -1
            else:
                book.Month = -1
                book.Year = -1
        # Editeur
        if CBEditor:
            nameRegex = ALBUM_EDITEUR.search(Entete, 0)
            if nameRegex:
                editeur = parseName(nameRegex.group(1))
                book.Publisher = editeur
            else:
                book.Publisher = ""
            debuglog(Trans(35), book.Publisher)
        # Planches
        if not book.FilePath:
            nameRegex = REVUE_PLANCHES.search(Entete, 0)
            if nameRegex:
                pages = nameRegex.group(1).strip()
                book.PageCount = int(pages) if isnumeric(pages) else -1
                debuglog(Trans(122), pages)
        # Periodicité
        if CBFormat:
            nameRegex = REVUE_PERIOD.search(Entete, 0)
            if nameRegex:
                book.Format = nameRegex.group(1).strip()
                debuglog(Trans(131), nameRegex.group(1))
        # Always set Language to french
        if CBLanguage and not book.LanguageISO:
            book.LanguageISO = "fr"
        # web
        if CBWeb == True and not CBRescrape:
            book.Web = serieUrl
            debuglog(Trans(123), book.Web)
        if CBNotes:
            write_book_notes(book)
        return True
    except:
        return False

# ========================================
# Cover Download Functions

# ========================================

def download_cover(book, cover_url):
    """
    Download and set book cover image
    Args:
        book: ComicRack book object
        cover_url: URL of the cover image
    Returns:
        bool: True if successful
    """
    if not config.CBCover or config.BDBASE_DISABLE_COVER:
        return False
    try:
        # TODO: Implement cover download logic
        # 1. Download image from URL
        # 2. Convert to appropriate format
        # 3. Set as book cover
        debuglog("Downloading cover from:", cover_url)
        return False
    except:
        debuglogOnError()
        return False

# ========================================
# Search and Matching Functions

# ========================================

def search_series(series_name):
    """
    Search BDbase for a series and return (url, title) tuples.
    """
    if not series_name:
        return []

    query = quote(remove_accents(series_name.lower().strip()).encode('utf-8'))
    urlN = '/recherche-series?type=bd&sch=' + query
    debuglog("Searching BDbase for series:", series_name)

    results = []
    html = _read_url(urlN.encode('utf-8'), False)
    if not html:
        return results



def find_best_match(series_name, search_results):
    if not search_results:
        return None

    target = normalize_text(series_name)
    for url, title in search_results:
        if normalize_text(title) == target:
            return (url, title)
    return search_results[0]


def extract_authors_from_html(html):
    role_map = {
        "scenario": "Writer",
        "storyboard": "Writer",
        "dessin": "Penciller",
        "couleurs": "Colorist",
        "colorisation": "Colorist",
        "encrage": "Inker",
        "couverture": "CoverArtist",
        "lettrage": "Letterer"
    }
    authors = {
        "Writer": [],
        "Penciller": [],
        "Colorist": [],
        "Inker": [],
        "CoverArtist": [],
        "Letterer": []
    }
    for match in BDBASE_ALBUM_AUTHOR.finditer(html):
        name = checkWebChar(strip_tags(match.group(1))).strip()
        role = normalize_text(match.group(2))
        if role in role_map and name:
            key = role_map[role]
            if name not in authors[key]:
                authors[key].append(name)
    return authors


def normalize_album_number(raw_number):
    if not raw_number:
        return ("", "")
    main = raw_number
    alt = ""
    mPos = re.search(r'([.,\/-])', raw_number)
    if mPos:
        nPos = mPos.start(1)
        main = raw_number[:nPos]
        alt = raw_number[nPos:]
    else:
        if isnumeric(raw_number):
            main = str(int(raw_number))
        else:
            main = raw_number
    return (main, alt)


def is_oneshot(album_data):
    if not album_data:
        return False
    fmt = (album_data.get("format") or "").lower()
    if "one shot" in fmt:
        return True
    if album_data.get("number", "").upper() == "HS":
        return True
    return False


def download_cover(book, cover_url):
    if not cover_url or config.BDBASE_DISABLE_COVER or book.FilePath:
        return False
    try:
        coverReq = HttpWebRequest.Create(cover_url)
        coverReq.UserAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        coverResp = coverReq.GetResponse()
        coverStream = coverResp.GetResponseStream()
        retval = Image.FromStream(coverStream)
        ComicRack.App.SetCustomBookThumbnail(book, retval)
        debuglog(Trans(105), cover_url)
        return True
    except:
        debuglog("Cover download failed for: " + cover_url)
        return False
    finally:
        if 'coverStream' in locals() and coverStream:
            coverStream.Close()
        if 'coverResp' in locals() and coverResp:
            coverResp.Close()
    for match in re.finditer(SERIE_LIST_PATTERN, html, re.IGNORECASE | re.DOTALL):
        series_url = match.group(1)
        title = checkWebChar(strip_tags(match.group(2))).strip()
        results.append((series_url, title))

    return results

def find_best_match(series_name, search_results):
    """
    Find the best matching series from search results
    Args:
        series_name: Original series name
        search_results: List of search results
    Returns:
        Best match or None
    """
    # TODO: Implement matching algorithm
    # 1. Normalize series name
    # 2. Compare with each result
    # 3. Return best match based on similarity
    if not search_results:
        return None
    # Placeholder: return first result
    return search_results[0] if search_results else None

# ========================================
# Helper Functions

# ========================================

def extract_authors_from_html(html):
    """
    Extract author information from HTML
    Args:
        html: HTML content
    Returns:
        dict: Dictionary with author roles (writer, penciller, etc.)
    """
    authors = {
        'writer': [],
        'penciller': [],
        'inker': [],
        'colorist': [],
        'letterer': [],
        'cover': []
    }
    # TODO: Implement author extraction using BDBASE_ALBUM_AUTHOR regex
    # Parse author cards and categorize by role
    return authors

def normalize_album_number(raw_number):
    """
    Normalize album number from various formats
    Args:
        raw_number: Raw number string
    Returns:
        tuple: (main_number, alt_number)
    """
    if not raw_number:
        return ("", "")
    # TODO: Implement number normalization logic
    # Handle formats like: "1", "1.5", "1a", "HS", etc.
    return (raw_number, "")

def is_oneshot(album_data):
    """
    Determine if an album is a one-shot
    Args:
        album_data: Album metadata dict
    Returns:
        bool: True if one-shot
    """
    # Check for one-shot indicators
    # - Count = 1
    # - Format contains "one-shot"
    # - Hors série
    return False

# ========================================
# QuickScrape Function (called from BDbaseScraper.py)

# ========================================

def QuickScrapeBDbase(books, book = "", cLink = False):

    global LinkBDbase, Numero, AlbumNumNum, dlgNumber, dlgName, nRenamed, nIgnored, dlgAltNumber, Shadow1, Shadow2, RenameSeries

    RetAlb = False

    if not cLink:
        if not LoadSetting():
            return False

    RenameSeries = False

    if not books:
        Result = MessageBox.Show(ComicRack.MainWindow, Trans(1),Trans(2), MessageBoxButtons.OK, MessageBoxIcon.Warning, MessageBoxDefaultButton.Button1)
        return False

    LinkBDbase = ""

    if not cLink:
        nRenamed = 0
        nIgnored = 0
    cError = False
    MyBooks = []
    f = None
    success = True

    try:

        if books:
            if cLink:
                MyBooks.append(book)
            else:
                MyBooks = books
                f = ProgressBarDialog(books.Count)
                if books.Count > 1:
                    f.Show(ComicRack.MainWindow)

            log_BD(Trans(7) + str(MyBooks.Count) +  Trans(8), "\n============ " + str(datetime.now().strftime("%A %d %B %Y %H:%M:%S")) + " ===========", 0)

            for MyBook in MyBooks:

                if cLink:
                    Numero = ""
                    serieUrl = cLink
                    LinkBDbase = serieUrl

                else:

                    if MyBook.Number:
                        dlgNumber = MyBook.Number
                        Shadow2 = False
                    else:
                        dlgNumber = MyBook.ShadowNumber
                        Shadow2 = True

                    if MyBook.Series:
                        dlgName = titlize(MyBook.Series)
                        Shadow1 = False
                    else:
                        dlgName = MyBook.ShadowSeries
                        Shadow1 = True

                    dlgAltNumber = ""
                    if MyBook.AlternateNumber:
                        dlgAltNumber = MyBook.AlternateNumber

                    albumNum = dlgNumber
                    mPos = re.search(r'([.,\\/-])', dlgNumber)

                    if not isnumeric(dlgNumber):
                        albumNum = dlgNumber
                        AlbumNumNum = False
                    elif isnumeric(dlgNumber) and not re.search(r'[.,\\/-]', dlgNumber):
                        dlgNumber = str(int(dlgNumber))
                        albumNum = str(int(dlgNumber))
                        AlbumNumNum = True
                    elif mPos:
                        nPos = mPos.start(1)
                        albumNum = dlgNumber[:nPos]
                        dlgAltNumber = dlgNumber[nPos:]
                        dlgNumber = albumNum
                        AlbumNumNum = True

                    f.Update(dlgName + if_else(dlgNumber != "", " - " + dlgNumber, " ") + if_else(dlgAltNumber == '', '', ' AltNo.[' + dlgAltNumber + ']') + " - " + titlize(MyBook.Title), 1, MyBook)
                    f.Refresh()

                    scrape = DirectScrape()
                    result = scrape.ShowDialog()

                    if result == DialogResult.Cancel or (LinkBDbase == ""):
                        success = False
                        break

                    if LinkBDbase:
                        serieUrl = GetFullURL(LinkBDbase)

                if LinkBDbase:
                    debuglog(Trans(104), LinkBDbase)

                RetVal = serieUrl
                if "/serie-" in serieUrl or '/revue-' in serieUrl: 
                    serieUrl = serieUrl if "__10000.html" in serieUrl or '/revue-' in serieUrl else serieUrl.lower().replace(".html", u'__10000.html')                   
                    RetVal = parseSerieInfo(MyBook, serieUrl, True)

                if RetVal and not '/revue-' in serieUrl:
                    if LinkBDbase:
                        RetVal = parseAlbumInfo(MyBook, RetVal, dlgNumber, True)

                if RetVal:
                    if not cLink:
                        nRenamed += 1
                    log_BD("[" + serieUrl + "]", Trans(13), 1)
                else:
                    if not cLink:
                        nIgnored += 1
                    log_BD("[" + serieUrl + "]", Trans(14) + "\n", 1)

        else:
            success = False
            debuglog(Trans(15) +"\n")
            log_BD(Trans(15), "", 1)

    except:
        cError = debuglogOnError()
        success = False
        try:
            log_BD("   [" + serieUrl + "]", cError, 1)
        except:
            log_BD("   [error]", cError, 1)

    finally:
        if not cLink and f:
            f.Update(Trans(16), 1, book)
            f.Refresh()
            f.Close()
        if not success:
            return False

    # Bilan final dans les logs
    log_BD("\n" + Trans(17) + str(nRenamed) , "", 0)
    log_BD(Trans(18) + str(nIgnored), "", 0)
    log_BD("============= " + str(datetime.now().strftime("%A %d %B %Y %H:%M:%S")) + " =============", "\n\n", 0)

    # Popups de bilan (uniquement en mode interactif, pas en rescrape via cLink)
    if not cLink:
        if cError and SHOWDBGLOG:
            rdlg = MessageBox.Show(ComicRack.MainWindow, Trans(17) + str(nRenamed) + "," + Trans(18) + str(nIgnored) + "\n\n" + Trans(19), Trans(20), MessageBoxButtons.YesNo, MessageBoxIcon.Warning, MessageBoxDefaultButton.Button1)
            if rdlg == DialogResult.Yes:
                if FileInfo(__file__[:-len('BDbaseScraper.py')] + "BDbase_debug_log.txt"):
                    Start(__file__[:-len('BDbaseScraper.py')] + "BDbase_debug_log.txt")
        elif SHOWRENLOG:
            rdlg = MessageBox.Show(ComicRack.MainWindow, Trans(17) + str(nRenamed) + "," + Trans(18) + str(nIgnored) + "\n\n" + Trans(21), Trans(22), MessageBoxButtons.YesNo, MessageBoxIcon.Question, MessageBoxDefaultButton.Button1)
            if rdlg == DialogResult.Yes:
                if FileInfo(__file__[:-len('BDbaseScraper.py')] + "BDbase_Rename_Log.txt"):
                    Start(__file__[:-len('BDbaseScraper.py')] + "BDbase_Rename_Log.txt")
        else:
            rdlg = MessageBox.Show(ComicRack.MainWindow, Trans(17) + str(nRenamed) + "," + Trans(18) + str(nIgnored) , Trans(22), MessageBoxButtons.OK, MessageBoxIcon.Exclamation, MessageBoxDefaultButton.Button1)

    return True
# ========================================
# Progress and UI Helper Functions

# ========================================

def update_progress(progress_dialog, message, current, total, book):
    """
    Update progress dialog
    Args:
        progress_dialog: Progress dialog instance
        message: Status message
        current: Current item number
        total: Total items
        book: Current book
    """
    if progress_dialog:
        try:
            progress_dialog.Update(message, current, book)
            progress_dialog.Refresh()
        except:
            pass

def check_user_cancel():
    """
    Check if user requested cancellation
    Returns:
        bool: True if should cancel
    """
    global bStopit
    return bStopit

# ========================================
# Module Exports

# ========================================
__all__ = [
    'BD_start',
    'parseSerieInfo',
    'parseAlbumInfo',
    'parseAlbumInfo_bdbase',
    'SetAlbumInformation',
    'AlbumChooser',
    'parseRevueInfo',
    'download_cover',
    'search_series',
    'find_best_match',
    'normalize_album_number',
    'is_oneshot',
    'extract_authors_from_html',
    'QuickScrapeBDbase'
]


def thread_proc():

    pass

    def handle(w, a): 
        pass
