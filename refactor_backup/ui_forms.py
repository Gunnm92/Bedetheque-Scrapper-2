# -*- coding: utf-8 -*-
"""
UI Forms module for BDbase Scraper
Contains all Windows Forms dialogs and UI components
"""

from __future__ import unicode_literals
import os
import System
from System.Windows.Forms import (
    Form, Button, Label, TextBox, CheckBox, RadioButton, ListBox,
    TabControl, TabPage, GroupBox, PictureBox, CheckedListBox,
    DialogResult, MessageBox, MessageBoxButtons, MessageBoxIcon,
    AnchorStyles, FormBorderStyle, FormStartPosition, SizeGripStyle,
    CheckState, HorizontalAlignment, PictureBoxSizeMode
)
from System.Windows.Forms import ButtonBase
from System.Drawing import Font, FontStyle, GraphicsUnit, Point, Size, Color, Bitmap
from System.Drawing import Rectangle, Graphics
from System.Drawing.Drawing2D import InterpolationMode
import collections

# Import from our modules
import scraper
import config
from utils import if_else, debuglog, debuglogOnError, log_BD, Capitalize
from settings import LoadSetting, SaveSetting, Trans, get_plugin_path

# Import ComicRack
try:
    from cYo.Projects.ComicRack.Engine import ComicRack
except:
    ComicRack = None

# ========================================
# Theme Helper
# ========================================

def ThemeMe(control):
    """Apply ComicRack theme to a control"""
    if ComicRack and ComicRack.App.ProductVersion >= '0.9.182':
        ComicRack.Theme.ApplyTheme(control)

# ========================================
# Form Type Enum
# ========================================

class FormType(object):
    """Enum for different form types"""
    SERIE = 1
    ALBUM = 2
    EDITION = 3

# ========================================
# Progress Bar Dialog
# ========================================

class ProgressBarDialog(Form):
    """
    Progress bar dialog shown during scraping operations
    """

    def __init__(self, total_count):
        """
        Initialize progress dialog

        Args:
            total_count: Total number of items to process
        """
        self.total_count = total_count
        self.current = 0

        # TODO: Implement full ProgressBarDialog UI from original file
        # Components needed:
        # - Progress bar
        # - Label for current item
        # - Label for status
        # - Cancel button
        # - Book cover thumbnail

        self.InitializeComponent()
        ThemeMe(self)

    def InitializeComponent(self):
        """Initialize form components"""
        self.Text = "BDbase Scraper - " + Trans(98)
        self.Size = Size(600, 200)
        self.StartPosition = FormStartPosition.CenterScreen
        self.FormBorderStyle = FormBorderStyle.FixedDialog
        self.MaximizeBox = False
        self.MinimizeBox = False

        # TODO: Add all components (progress bar, labels, etc.)

    def Update(self, message, increment, book):
        """
        Update progress

        Args:
            message: Status message to display
            increment: Amount to increment progress
            book: Current book being processed
        """
        self.current += increment
        # TODO: Update UI components
        debuglog("Progress:", self.current, "/", self.total_count, "-", message)

    def Refresh(self):
        """Refresh the dialog"""
        if hasattr(Form, 'Refresh'):
            Form.Refresh(self)

# ========================================
# Configuration Form
# ========================================

class BDConfigForm(Form):
    """
    Main configuration dialog for BDbase Scraper
    """

    def __init__(self):
        """Initialize configuration form"""
        self.Name = "BDConfigForm"
        self.Text = "BDbase Scraper"

        # Set icon
        icon_path = os.path.join(get_plugin_path(), "assets", "BDbase.ico")
        if os.path.exists(icon_path):
            self.Icon = System.Drawing.Icon(icon_path)

        self.HelpButton = False
        self.MaximizeBox = False
        self.MinimizeBox = False
        self.SizeGripStyle = SizeGripStyle.Hide
        self.StartPosition = FormStartPosition.CenterScreen
        self.FormBorderStyle = FormBorderStyle.FixedDialog

        # TODO: Implement full BDConfigForm UI from original file (lines 2026-2856)
        # This is a large form with 3 tabs:
        # - Tab 1: General settings
        # - Tab 2: Data fields to scrape
        # - Tab 3: Debug/logging options

        self.InitializeComponents()
        ThemeMe(self)

    def InitializeComponents(self):
        """Initialize all form components"""
        self.ClientSize = Size(612, 412)

        # Create tab control
        self._TabData = TabControl()
        self._TabData.Size = Size(612, 362)
        self._TabData.Location = Point(0, 0)

        # Create tabs
        self._tabPage1 = TabPage()  # General settings
        self._tabPage1.Text = Trans(95)

        self._tabPage2 = TabPage()  # Data fields
        self._tabPage2.Text = Trans(96)

        self._tabPage3 = TabPage()  # Debug
        self._tabPage3.Text = Trans(47)

        self._TabData.Controls.Add(self._tabPage1)
        self._TabData.Controls.Add(self._tabPage2)
        self._TabData.Controls.Add(self._tabPage3)

        # Create OK and Cancel buttons
        self._OKButton = Button()
        self._OKButton.Text = Trans(92)
        self._OKButton.Location = Point(16, 370)
        self._OKButton.Size = Size(75, 32)
        self._OKButton.BackColor = Color.FromArgb(128, 255, 128)
        self._OKButton.Font = Font("Microsoft Sans Serif", 9, FontStyle.Bold, GraphicsUnit.Point, 0)
        self._OKButton.DialogResult = DialogResult.OK
        self._OKButton.Click += self.button_Click

        self._CancelButton = Button()
        self._CancelButton.Text = Trans(93)
        self._CancelButton.Location = Point(520, 370)
        self._CancelButton.Size = Size(75, 32)
        self._CancelButton.BackColor = Color.Red
        self._CancelButton.Font = Font("Microsoft Sans Serif", 9, FontStyle.Bold, GraphicsUnit.Point, 0)
        self._CancelButton.DialogResult = DialogResult.Cancel

        # Version label
        self._labelVersion = Label()
        self._labelVersion.Text = "Version " + config.VERSION + " (c) 2021 kiwi13 && maforget"
        self._labelVersion.Font = Font("Microsoft Sans Serif", 6.75, FontStyle.Italic, GraphicsUnit.Point, 0)
        self._labelVersion.Location = Point(162, 380)
        self._labelVersion.Size = Size(264, 16)
        self._labelVersion.TextAlign = System.Drawing.ContentAlignment.BottomCenter

        # Add controls to form
        self.Controls.Add(self._TabData)
        self.Controls.Add(self._OKButton)
        self.Controls.Add(self._CancelButton)
        self.Controls.Add(self._labelVersion)

        self.AcceptButton = self._OKButton
        self.CancelButton = self._CancelButton

        # TODO: Add all tab content (checkboxes, textboxes, radio buttons, etc.)
        # This is a very large form with ~50 controls

        HighDpiHelper.AdjustControlImagesDpiScale(self)

    def button_Click(self, sender, e):
        """Handle button clicks"""
        if sender.Name == self._OKButton.Name:
            debuglog("Config form OK clicked - saving settings")
            SaveSetting()
        else:
            debuglog("Config form cancelled")

# ========================================
# Series Selection Form
# ========================================

class SeriesForm(Form):
    """
    Dialog for selecting series, album, or edition from a list
    """

    def __init__(self, serie, listItems, formType=FormType.SERIE):
        """
        Initialize series selection form

        Args:
            serie: Series name for title
            listItems: List of items to display
            formType: Type of selection (SERIE, ALBUM, or EDITION)
        """
        self.List = listItems
        self.list_filtered_index = []
        self.formType = formType
        self.InitializeComponent(serie)
        ThemeMe(self)

    def InitializeComponent(self, serie):
        """Initialize form components"""
        global TimerExpired

        self.Load += self.MainForm_Load

        # Create components
        self._ListSeries = ListBox()
        self._ListSeries.Font = Font("Microsoft Sans Serif", 9, FontStyle.Regular, GraphicsUnit.Point, 0)
        self._ListSeries.Anchor = AnchorStyles.Top | AnchorStyles.Left | AnchorStyles.Right | AnchorStyles.Bottom
        self._ListSeries.FormattingEnabled = True
        self._ListSeries.ItemHeight = 15
        self._ListSeries.Location = Point(8, 30)
        self._ListSeries.Size = Size(374, 258)
        self._ListSeries.Sorted = True
        self._ListSeries.TabIndex = 3
        self._ListSeries.DoubleClick += self.DoubleClick

        # Filter textbox
        self._Filter = TextBox()
        self._Filter.Anchor = AnchorStyles.Top | AnchorStyles.Left | AnchorStyles.Right
        self._Filter.Font = Font("Microsoft Sans Serif", 9, FontStyle.Regular, GraphicsUnit.Point, 0)
        self._Filter.Location = Point(30, 8)
        self._Filter.Size = Size(352, 20)
        self._Filter.TabIndex = 1
        self._Filter.TextChanged += self.onTextChanged

        # Clear button
        self._ClearButton = Button()
        self._ClearButton.Text = "X"
        self._ClearButton.Font = Font("Microsoft Sans Serif", 8, FontStyle.Bold, GraphicsUnit.Point, 0)
        self._ClearButton.Location = Point(8, 8)
        self._ClearButton.Size = Size(20, 20)
        self._ClearButton.TabIndex = 2
        self._ClearButton.Click += self.ClearButton_Click

        # OK button
        self._OKButton = Button()
        self._OKButton.Text = Trans(92)
        self._OKButton.BackColor = Color.FromArgb(128, 255, 128)
        self._OKButton.Font = Font("Microsoft Sans Serif", 9, FontStyle.Bold, GraphicsUnit.Point, 0)
        self._OKButton.Location = Point(8, 290)
        self._OKButton.Size = Size(75, 30)
        self._OKButton.DialogResult = DialogResult.OK
        self._OKButton.Click += self.button_Click

        # Cancel button
        self._CancelButton = Button()
        self._CancelButton.Text = Trans(93)
        self._CancelButton.BackColor = Color.Red
        self._CancelButton.Font = Font("Microsoft Sans Serif", 9, FontStyle.Bold, GraphicsUnit.Point, 0)
        self._CancelButton.Location = Point(301, 290)
        self._CancelButton.Size = Size(75, 30)
        self._CancelButton.DialogResult = DialogResult.Cancel

        # Form settings
        self.ClientSize = Size(390, 325)
        self.MinimumSize = Size(180, 180)
        self.MaximizeBox = False
        self.MinimizeBox = False
        self.SizeGripStyle = SizeGripStyle.Hide
        self.StartPosition = FormStartPosition.CenterScreen

        # Set title based on form type
        if self.formType == FormType.SERIE:
            self.Text = Trans(132) + serie
        elif self.formType == FormType.EDITION:
            self.Text = Trans(145) + serie
        elif self.formType == FormType.ALBUM:
            self.Text = Trans(146) + serie

        # Add controls
        self.Controls.Add(self._Filter)
        self.Controls.Add(self._ListSeries)
        self.Controls.Add(self._OKButton)
        self.Controls.Add(self._CancelButton)
        self.Controls.Add(self._ClearButton)

        self.AcceptButton = self._OKButton
        self.CancelButton = self._CancelButton
        self.KeyPreview = True

        self.fillList()

        HighDpiHelper.AdjustControlImagesDpiScale(self)

        # Setup timer if needed
        if config.AllowUserChoice == "2":
            TimerExpired = False
            self._timer1 = System.Windows.Forms.Timer()
            self._timer1.Interval = int(config.TIMEPOPUP) * 1000
            self._timer1.Enabled = True
            self._timer1.Tick += self.CloseForm
            self._timer1.Start()

    def fillList(self):
        """Fill list with items"""
        self._ListSeries.Items.Clear()
        del self.list_filtered_index[:]
        filter_text = self._Filter.Text.strip().lower()

        for x in range(len(self.List)):
            if self.List[x]:
                # Get title based on form type
                if self.formType == FormType.EDITION:
                    title = self.List[x][1].Title
                else:
                    title = self.List[x][1]

                # Format display string
                display = "(" + self.List[x][2] + ") - " + title
                if self.List[x][0]:
                    display += "   (" + self.List[x][0] + ")"

                # Apply filter
                if filter_text and filter_text not in display.lower():
                    continue

                self._ListSeries.Items.Add(display)
                self.list_filtered_index.append(x)

    def onTextChanged(self, sender, e):
        """Handle filter text change"""
        self.fillList()

    def button_Click(self, sender, e):
        """Handle OK button click"""
        global NewLink, NewSeries

        if self._ListSeries.SelectedIndex < 0:
            return

        sel = self.list_filtered_index[self._ListSeries.SelectedIndex]
        if sender.Name == self._OKButton.Name and self.List[sel][1]:
            scraper.NewLink = self.List[sel][0]
            scraper.NewSeries = self.List[sel][1]
            self.Hide()

    def ClearButton_Click(self, sender, e):
        """Clear filter"""
        self._Filter.Text = ""
        self.fillList()
        self._Filter.Focus()

    def CloseForm(self, sender, e):
        """Handle timer expiration"""
        global TimerExpired
        debuglog("Timer Expired")
        TimerExpired = True
        self._timer1.Stop()
        self.Hide()

    def DoubleClick(self, sender, e):
        """Handle double-click on item"""
        global NewLink, NewSeries

        if self._ListSeries.SelectedIndex < 0:
            return

        sel = self.list_filtered_index[self._ListSeries.SelectedIndex]

        # Get title and link based on form type
        if self.formType == FormType.SERIE:
            title = self.List[sel][1]
            link = config.BASE_URL + "/" + self.List[sel][0].lstrip("/")
        elif self.formType == FormType.EDITION:
            title = self.List[sel][1].Title + " (" + self.List[sel][1].A + ")"
            link = self.List[sel][1].URL
        elif self.formType == FormType.ALBUM:
            title = self.List[sel][1]
            link = self.List[sel][0]
        else:
            return

        if title:
            scraper.NewLink = link
            scraper.NewSeries = self.List[sel][1]
            self.Hide()

    def MainForm_Load(self, sender, e):
        """Handle form load"""
        self.Left += 365

# ========================================
# Direct Scrape Form (Quick Scrape)
# ========================================

class DirectScrape(Form):
    """
    Dialog for entering a direct URL to scrape
    """

    def __init__(self):
        """Initialize direct scrape form"""
        self.InitializeComponent()
        ThemeMe(self)

    def InitializeComponent(self):
        """Initialize form components"""
        try:
            # Text box for URL
            self._LinkBDbase = TextBox()
            self._LinkBDbase.Location = Point(8, 40)
            self._LinkBDbase.Size = Size(646, 20)
            self._LinkBDbase.TabIndex = 1

            # Label
            self._labelPasteLink = Label()
            self._labelPasteLink.Font = Font("Microsoft Sans Serif", 11.25, FontStyle.Italic, GraphicsUnit.Point, 0)
            self._labelPasteLink.Location = Point(104, 8)
            self._labelPasteLink.Size = Size(450, 20)
            self._labelPasteLink.Text = Trans(102)
            self._labelPasteLink.TextAlign = System.Drawing.ContentAlignment.MiddleCenter

            # OK button
            self._OKScrape = Button()
            self._OKScrape.BackColor = Color.FromArgb(128, 255, 128)
            self._OKScrape.Font = Font("Microsoft Sans Serif", 8.25, FontStyle.Bold, GraphicsUnit.Point, 0)
            self._OKScrape.Location = Point(48, 72)
            self._OKScrape.Size = Size(104, 30)
            self._OKScrape.Text = Trans(92)
            self._OKScrape.DialogResult = DialogResult.OK
            self._OKScrape.Click += self.button_Click

            # Cancel button
            self._CancScrape = Button()
            self._CancScrape.BackColor = Color.FromArgb(255, 128, 128)
            self._CancScrape.Font = Font("Microsoft Sans Serif", 8.25, FontStyle.Bold, GraphicsUnit.Point, 0)
            self._CancScrape.Location = Point(550, 72)
            self._CancScrape.Size = Size(104, 30)
            self._CancScrape.Text = Trans(93)
            self._CancScrape.DialogResult = DialogResult.Cancel
            self._CancScrape.Click += self.button_Click

            # Form settings
            self.ClientSize = Size(710, 108)
            self.ControlBox = False
            self.FormBorderStyle = FormBorderStyle.FixedDialog
            self.StartPosition = FormStartPosition.CenterScreen
            self.Text = Trans(103)

            # Set icon
            icon_path = os.path.join(get_plugin_path(), "assets", "BDbase.ico")
            if os.path.exists(icon_path):
                self.Icon = System.Drawing.Icon(icon_path)

            self.KeyPreview = True

            # Add controls
            self.Controls.Add(self._CancScrape)
            self.Controls.Add(self._OKScrape)
            self.Controls.Add(self._labelPasteLink)
            self.Controls.Add(self._LinkBDbase)

            HighDpiHelper.AdjustControlImagesDpiScale(self)

        except:
            debuglogOnError()

    def button_Click(self, sender, e):
        """Handle button click"""
        if sender.Name == self._OKScrape.Name:
            # Import here to avoid circular dependency
            import scraper
            if self._LinkBDbase.Text:
                scraper.LinkBDbase = self._LinkBDbase.Text
            else:
                scraper.LinkBDbase = ""
                self.Hide()

# ========================================
# High DPI Helper
# ========================================

class HighDpiHelper(object):
    """Helper class for high DPI display support"""

    @staticmethod
    def AdjustControlImagesDpiScale(container):
        """Adjust control images for DPI scaling"""
        dpiScale = HighDpiHelper.GetDpiScale(container)
        if HighDpiHelper.CloseToOne(dpiScale):
            return

        # DPI Scaling Aware
        container.AutoScaleDimensions = Size(96, 96)
        container.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Dpi

        HighDpiHelper.AdjustControlImagesDpiScale_Internal(container.Controls, dpiScale)

    @staticmethod
    def AdjustButtonImageDpiScale(button, dpiScale):
        """Adjust button image for DPI"""
        image = button.Image
        if image is None:
            return
        button.Image = HighDpiHelper.ScaleImage(image, dpiScale)

    @staticmethod
    def AdjustPictureBoxDpiScale(pictureBox, dpiScale):
        """Adjust picture box for DPI"""
        image = pictureBox.Image
        if image is None:
            return
        if pictureBox.SizeMode == PictureBoxSizeMode.CenterImage:
            pictureBox.Image = HighDpiHelper.ScaleImage(image, dpiScale)

    @staticmethod
    def AdjustControlImagesDpiScale_Internal(controls, dpiScale):
        """Recursively adjust controls for DPI"""
        for control in controls:
            if isinstance(control, ButtonBase):
                HighDpiHelper.AdjustButtonImageDpiScale(control, dpiScale)
            elif isinstance(control, PictureBox):
                HighDpiHelper.AdjustPictureBoxDpiScale(control, dpiScale)

            HighDpiHelper.AdjustControlImagesDpiScale_Internal(control.Controls, dpiScale)

    @staticmethod
    def CloseToOne(dpiScale):
        """Check if DPI scale is close to 1.0"""
        return System.Math.Abs(dpiScale - 1) < 0.001

    @staticmethod
    def GetDpiScale(control):
        """Get DPI scale for control"""
        try:
            graphics = control.CreateGraphics()
            if graphics:
                dpiX = graphics.DpiX
                graphics.Dispose()
                return dpiX / 96.0
        except:
            debuglogOnError()
        return 1.0

    @staticmethod
    def ScaleImage(image, dpiScale):
        """Scale image for DPI"""
        if HighDpiHelper.CloseToOne(dpiScale):
            return image

        newSize = HighDpiHelper.ScaleSize(image.Size, dpiScale)
        newBitmap = Bitmap(newSize.Width, newSize.Height)

        g = Graphics.FromImage(newBitmap)
        if dpiScale >= 2.0:
            g.InterpolationMode = InterpolationMode.NearestNeighbor
        else:
            g.InterpolationMode = InterpolationMode.HighQualityBicubic

        g.DrawImage(image, Rectangle(Point.Empty, newSize))
        g.Dispose()

        return newBitmap

    @staticmethod
    def ScaleSize(size, scale):
        """Scale size by factor"""
        return Size(int(size.Width * scale), int(size.Height * scale))

# ========================================
# Module Exports
# ========================================

__all__ = [
    'ThemeMe',
    'FormType',
    'ProgressBarDialog',
    'BDConfigForm',
    'SeriesForm',
    'DirectScrape',
    'HighDpiHelper'
]
