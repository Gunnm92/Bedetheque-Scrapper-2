# -*- coding: utf-8 -*-
#@Name BDbase Scraper
#@Key BDbaseScraper
#@Hook    Books, Editor
#@Image BDbase.png
#@Description Search on www.bdbase.fr informations about the selected eComics

from __future__ import unicode_literals
import clr
import os

from System.Windows.Forms import DialogResult

clr.AddReference('System')
clr.AddReference('System.Drawing')
clr.AddReference('System.Windows.Forms')

try:
    from cYo.Projects.ComicRack.Engine import ComicRack
except:
    ComicRack = None

from bdbase_scraper import scraper, settings
from bdbase_scraper import ui_forms

#@Key BDbaseScraper
#@Hook ConfigScript
#@Name Configurer BDbase
def ConfigureBDbaseQuick():
    _show_config()

#@Name Configurer BDbase
#@Image BDbase.png
#@Hook Library
#@Key ConfigureBDbase
def ConfigureBDbase(self):
    _show_config()

#@Name QuickScrape BDbase
#@Image BDbaseQ.png
#@Hook Books
#@Key QuickScrapeBDbase
def QuickScrapeBDbase(books, book = "", cLink = False):
    return scraper.QuickScrapeBDbase(books, book, cLink)


def _show_config():
    if not settings.LoadSetting():
        return

    form = ui_forms.BDConfigForm()
    result = form.ShowDialog()
    if result == DialogResult.OK:
        settings.SaveSetting()
