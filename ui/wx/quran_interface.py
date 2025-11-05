"""wxPython implementation of the main Albayan interface."""

from __future__ import annotations

import os
from typing import Optional

import wx

from core_functions.quran_class import quran_mgr
from core_functions.tafaseer import Category
from core_functions.info import E3rab, TanzilAyah, AyaInfo
from core_functions.bookmark import BookmarkManager
from ui.wx.dialogs.quick_access import QuickAccessDialog
from ui.wx.dialogs.search_dialog import SearchDialog
from ui.wx.dialogs.tafaseer_dialog import TafaseerDialog
from ui.wx.dialogs.info_dialog import InfoDialog
from utils.settings import SettingsManager
from utils.universal_speech import UniversalSpeech
from utils.user_data import UserDataManager
from utils.const import program_name, program_icon, user_db_path, Globals
from utils.audio_player import SoundEffectPlayer


class QuranInterface(wx.Frame):
    """Main application frame implemented with wxPython."""

    def __init__(self, parent: Optional[wx.Window], title: str) -> None:
        super().__init__(parent, title=title, size=(1100, 800))
        if os.path.exists(program_icon):
            self.SetIcon(wx.Icon(program_icon))
        self.SetBackgroundColour(wx.Colour(20, 20, 20))
        self.quran = quran_mgr()
        self.quran.load_quran(SettingsManager.current_settings["reading"]["font_type"])
        self.user_data_manager = UserDataManager(user_db_path)
        Globals.effects_manager = SoundEffectPlayer("Audio/sounds")

        self._create_ui()
        self._create_bindings()
        self.Centre()
        self.set_text()

    def _create_ui(self) -> None:
        panel = wx.Panel(self)
        panel.SetBackgroundColour(wx.Colour(20, 20, 20))
        sizer = wx.BoxSizer(wx.VERTICAL)

        self.quran_title = wx.StaticText(panel, label="")
        title_font = self.quran_title.GetFont()
        title_font.SetPointSize(18)
        title_font.SetWeight(wx.FONTWEIGHT_BOLD)
        self.quran_title.SetFont(title_font)
        self.quran_title.SetForegroundColour(wx.Colour(255, 255, 255))
        self.quran_title.SetWindowStyleFlag(wx.ALIGN_CENTER_HORIZONTAL)
        sizer.Add(self.quran_title, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 10)

        self.quran_view = wx.TextCtrl(
            panel,
            style=wx.TE_MULTILINE | wx.TE_RICH2 | wx.TE_READONLY | wx.TE_NO_VSCROLL,
        )
        self.quran_view.SetForegroundColour(wx.Colour(230, 230, 230))
        self.quran_view.SetBackgroundColour(wx.Colour(35, 35, 35))
        font = self.quran_view.GetFont()
        font.SetPointSize(16)
        self.quran_view.SetFont(font)
        sizer.Add(self.quran_view, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        button_panel = wx.Panel(panel)
        button_panel.SetBackgroundColour(wx.Colour(20, 20, 20))
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_panel.SetSizer(button_sizer)
        sizer.Add(button_panel, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 10)

        self.next_button = wx.Button(button_panel, label="التالي")
        self.back_button = wx.Button(button_panel, label="السابق")
        self.interpretation_button = wx.Button(button_panel, label="تفسير الآية")
        self.quick_access_button = wx.Button(button_panel, label="الوصول السريع")
        self.search_button = wx.Button(button_panel, label="بحث")
        self.save_position_button = wx.Button(button_panel, label="حفظ الموضع الحالي")

        for button in (
            self.next_button,
            self.back_button,
            self.interpretation_button,
            self.quick_access_button,
            self.search_button,
            self.save_position_button,
        ):
            button_sizer.Add(button, 0, wx.LEFT, 5)

        panel.SetSizer(sizer)
        self.SetSizerAndFit(sizer)

        self.CreateStatusBar()
        self.SetStatusText(program_name)

        menu_bar = wx.MenuBar()
        navigation_menu = wx.Menu()
        self.menu_next = navigation_menu.Append(wx.ID_FORWARD, "التالي")
        self.menu_previous = navigation_menu.Append(wx.ID_BACKWARD, "السابق")
        menu_bar.Append(navigation_menu, "التنقل")

        actions_menu = wx.Menu()
        self.menu_save_position = actions_menu.Append(wx.ID_SAVE, "حفظ الموضع")
        self.menu_bookmark = actions_menu.Append(wx.ID_ADD, "حفظ علامة")
        self.menu_interpret = actions_menu.Append(wx.ID_ANY, "تفسير الآية")
        menu_bar.Append(actions_menu, "إجراءات")

        self.SetMenuBar(menu_bar)

    def _create_bindings(self) -> None:
        self.next_button.Bind(wx.EVT_BUTTON, lambda _: self.OnNext())
        self.back_button.Bind(wx.EVT_BUTTON, lambda _: self.OnBack())
        self.interpretation_button.Bind(wx.EVT_BUTTON, self.OnInterpretation)
        self.quick_access_button.Bind(wx.EVT_BUTTON, self.OnQuickAccess)
        self.search_button.Bind(wx.EVT_BUTTON, self.OnSearch)
        self.save_position_button.Bind(wx.EVT_BUTTON, lambda _: self.OnSaveCurrentPosition())

        self.Bind(wx.EVT_MENU, lambda _: self.OnNext(), self.menu_next)
        self.Bind(wx.EVT_MENU, lambda _: self.OnBack(), self.menu_previous)
        self.Bind(wx.EVT_MENU, lambda _: self.OnSaveCurrentPosition(), self.menu_save_position)
        self.Bind(wx.EVT_MENU, self.OnSaveBookmark, self.menu_bookmark)
        self.Bind(wx.EVT_MENU, self.OnInterpretation, self.menu_interpret)

        self.quran_view.Bind(wx.EVT_CONTEXT_MENU, self.on_context_menu)
        self.quran_view.Bind(wx.EVT_LEFT_DCLICK, lambda evt: self.say_current_ayah())

    # Public helpers -------------------------------------------------
    def focus_quran_view(self) -> None:
        self.quran_view.SetFocus()

    # Internal helpers -----------------------------------------------
    def set_text(self) -> None:
        position_data = self.user_data_manager.get_last_position()
        ayah_number = position_data.get("ayah_number", 1)
        current_position = position_data.get("position", 1)
        self.quran.type = position_data.get("criteria_number", 0)

        text = self.quran.goto(current_position)
        self.quran_view.SetValue(text)
        self.set_text_label()
        self.set_focus_to_ayah(ayah_number)

    def set_focus_to_ayah(self, ayah_number: int) -> None:
        if ayah_number == -1:
            text_position = len(self.quran_view.GetValue())
        else:
            text_position = self.quran.ayah_data.get_position(ayah_number)
        self.quran_view.SetInsertionPoint(text_position)
        self.quran_view.ShowPosition(text_position)

    def OnNext(self) -> None:
        self.quran_view.SetValue(self.quran.next())
        self.set_text_label()
        Globals.effects_manager.play("next")

    def OnBack(self, is_auto_call: bool = False) -> None:
        self.quran_view.SetValue(self.quran.back())
        self.set_text_label()
        Globals.effects_manager.play("previous")
        if SettingsManager.current_settings["reading"].get("auto_page_turn") and is_auto_call:
            self.set_focus_to_ayah(-1)

    def set_text_label(self) -> None:
        label = ""
        if self.quran.type == 0:
            label = f"الصفحة {self.quran.current_pos}"
            self.next_button.SetLabel("الصفحة التالية")
            self.back_button.SetLabel("الصفحة السابقة")
            self.menu_next.SetItemLabel("الصفحة التالية")
            self.menu_previous.SetItemLabel("الصفحة السابقة")
        elif self.quran.type == 1:
            label = self.quran.data_list[-1][2]
            self.next_button.SetLabel("السورة التالية")
            self.back_button.SetLabel("السورة السابقة")
            self.menu_next.SetItemLabel("السورة التالية")
            self.menu_previous.SetItemLabel("السورة السابقة")
        elif self.quran.type == 2:
            label = f"الربع {self.quran.current_pos}"
            self.next_button.SetLabel("الربع التالي")
            self.back_button.SetLabel("الربع السابق")
            self.menu_next.SetItemLabel("الربع التالي")
            self.menu_previous.SetItemLabel("الربع السابق")
        elif self.quran.type == 3:
            label = f"الحزب {self.quran.current_pos}"
            self.next_button.SetLabel("الحزب التالي")
            self.back_button.SetLabel("الحزب السابق")
            self.menu_next.SetItemLabel("الحزب التالي")
            self.menu_previous.SetItemLabel("الحزب السابق")
        elif self.quran.type == 4:
            label = f"الجزء {self.quran.current_pos}"
            self.next_button.SetLabel("الجزء التالي")
            self.back_button.SetLabel("الجزء السابق")
            self.menu_next.SetItemLabel("الجزء التالي")
            self.menu_previous.SetItemLabel("الجزء السابق")

        self.quran_title.SetLabel(label)
        self.quran_view.SetName(label)
        if self.IsActive():
            UniversalSpeech.say(label)

        next_status = self.quran.current_pos < self.quran.max_pos
        back_status = self.quran.current_pos > 1
        self.next_button.Enable(next_status)
        self.menu_next.Enable(next_status)
        self.back_button.Enable(back_status)
        self.menu_previous.Enable(back_status)

    def OnQuickAccess(self, event: wx.CommandEvent) -> None:
        dialog = QuickAccessDialog(self)
        if dialog.ShowModal() == wx.ID_OK:
            result = dialog.get_selected_text()
            if result:
                self.quran_view.SetValue(result)
                self.set_text_label()
                self.quran_view.SetFocus()
        dialog.Destroy()

    def OnSearch(self, event: wx.CommandEvent) -> None:
        dialog = SearchDialog(self)
        if dialog.ShowModal() == wx.ID_OK:
            ayah_number = dialog.get_selected_ayah()
            if ayah_number:
                ayah_result = self.quran.get_by_ayah_number(ayah_number)
                self.quran_view.SetValue(ayah_result["full_text"])
                self.set_focus_to_ayah(ayah_number)
                self.set_text_label()
        dialog.Destroy()

    def get_current_ayah_info(self) -> list:
        position = self.quran_view.GetInsertionPoint()
        return self.quran.get_ayah_info(position)

    def OnInterpretation(self, event: wx.CommandEvent) -> None:
        ayah_info = self.get_current_ayah_info()
        if not ayah_info:
            return
        selected_category = Category.get_categories_in_arabic()[0]
        dialog = TafaseerDialog(self, ayah_info, selected_category)
        dialog.ShowModal()
        dialog.Destroy()

    def on_context_menu(self, event: wx.ContextMenuEvent) -> None:
        menu = wx.Menu()
        save_position = menu.Append(wx.ID_SAVE, "حفظ الموضع الحالي")
        save_bookmark = menu.Append(wx.ID_ADD, "حفظ علامة")
        menu.AppendSeparator()
        interpretation_menu = wx.Menu()
        for category in Category.get_categories_in_arabic():
            item_id = wx.NewIdRef()
            interpretation_menu.Append(item_id, category)
            interpretation_menu.Bind(wx.EVT_MENU, lambda evt, cat=category: self.show_interpretation(cat), id=item_id)
        menu.AppendSubMenu(interpretation_menu, "التفسير")
        ayah_info_item = menu.Append(wx.ID_ANY, "معلومات الآية")
        syntax_item = menu.Append(wx.ID_ANY, "إعراب الآية")
        reasons_item = menu.Append(wx.ID_ANY, "أسباب نزول الآية")
        copy_item = menu.Append(wx.ID_COPY, "نسخ الآية")

        menu.Bind(wx.EVT_MENU, lambda evt: self.OnSaveCurrentPosition(), save_position)
        menu.Bind(wx.EVT_MENU, self.OnSaveBookmark, save_bookmark)
        menu.Bind(wx.EVT_MENU, self.OnAyahInfo, ayah_info_item)
        menu.Bind(wx.EVT_MENU, self.OnSyntax, syntax_item)
        menu.Bind(wx.EVT_MENU, self.OnVerseReasons, reasons_item)
        menu.Bind(wx.EVT_MENU, lambda evt: self.on_copy_verse(), copy_item)

        self.PopupMenu(menu)
        menu.Destroy()

    def show_interpretation(self, category: str) -> None:
        ayah_info = self.get_current_ayah_info()
        if not ayah_info:
            return
        dialog = TafaseerDialog(self, ayah_info, category)
        dialog.ShowModal()
        dialog.Destroy()

    def on_copy_verse(self) -> None:
        text = self.quran_view.GetValue()
        pos = self.quran_view.GetInsertionPoint()
        start = text.rfind("\n", 0, pos) + 1
        end = text.find("\n", pos)
        if end == -1:
            end = len(text)
        current_line = text[start:end].strip()
        if not current_line:
            return
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(wx.TextDataObject(current_line))
            wx.TheClipboard.Close()
        UniversalSpeech.say("تم نسخ الآية.")
        Globals.effects_manager.play("copy")

    def OnSyntax(self, event: wx.CommandEvent) -> None:
        ayah_info = self.get_current_ayah_info()
        if not ayah_info:
            return
        text = E3rab(ayah_info[0], ayah_info[1]).text
        dialog = InfoDialog(self, f"إعراب آية رقم {ayah_info[3]} من {ayah_info[2]}", "الإعراب", text)
        dialog.ShowModal()
        dialog.Destroy()

    def OnVerseReasons(self, event: wx.CommandEvent) -> None:
        ayah_info = self.get_current_ayah_info()
        if not ayah_info:
            return
        text = TanzilAyah(ayah_info[1]).text
        if text:
            dialog = InfoDialog(
                self,
                f"أسباب نزول آية رقم {ayah_info[3]} من {ayah_info[2]}",
                "الأسباب",
                text,
            )
            dialog.ShowModal()
            dialog.Destroy()
        else:
            wx.MessageBox("للأسف لا يتوفر في الوقت الحالي معلومات لهذه الآية.", "لا يتوفر معلومات للآية")

    def OnAyahInfo(self, event: wx.CommandEvent) -> None:
        ayah_info = self.get_current_ayah_info()
        if not ayah_info:
            return
        text = AyaInfo(ayah_info[1]).text
        dialog = InfoDialog(
            self,
            f"معلومات آية رقم {ayah_info[3]} من {ayah_info[2]}",
            "معلومات الآية",
            text,
            is_html=False,
        )
        dialog.ShowModal()
        dialog.Destroy()

    def say_current_ayah(self) -> None:
        ayah_info = self.get_current_ayah_info()
        if not ayah_info:
            return
        text = f"آية {ayah_info[3]} من {ayah_info[2]}."
        UniversalSpeech.say(text)

    def OnSaveBookmark(self, event: wx.CommandEvent) -> None:
        ayah_info = self.get_current_ayah_info()
        if not ayah_info:
            return
        bookmark_manager = BookmarkManager()
        if bookmark_manager.is_exist(ayah_info[1]):
            wx.MessageBox("تم حفظ العلامة المرجعية مسبقًا.", "خطأ", style=wx.ICON_ERROR)
            return
        dialog = wx.TextEntryDialog(self, "أدخل اسم العلامة:", "اسم العلامة")
        if dialog.ShowModal() == wx.ID_OK:
            name = dialog.GetValue()
            if name:
                bookmark_manager.insert_bookmark(
                    name,
                    ayah_info[1],
                    ayah_info[3],
                    ayah_info[0],
                    ayah_info[2],
                    self.quran.type,
                )
                self.quran_view.SetFocus()
        dialog.Destroy()

    def OnSaveCurrentPosition(self) -> None:
        ayah_info = self.get_current_ayah_info()
        if not ayah_info:
            return
        self.user_data_manager.save_position(
            ayah_info[1],
            self.quran.type,
            self.quran.current_pos,
        )
        self.OnSave_alert()

    def OnSave_alert(self) -> None:
        UniversalSpeech.say("تم حفظ الموضع الحالي.")
        Globals.effects_manager.play("save")

    def OnChangeNavigationMode(self, mode: int) -> None:
        ayah_info = self.get_current_ayah_info()
        if ayah_info:
            ayah_number = ayah_info[1]
            self.quran.type = mode
            result = self.quran.get_by_ayah_number(ayah_number)
            self.quran_view.SetValue(result["full_text"])
            self.set_focus_to_ayah(ayah_number)
            self.set_text_label()
            Globals.effects_manager.play("change")

    def OnClose(self, event: wx.CloseEvent) -> None:
        if SettingsManager.current_settings["general"].get("run_in_background_enabled"):
            self.Hide()
            UniversalSpeech.say("تم تصغير البرنامج إلى علبة النظام.")
            event.Veto()
        else:
            event.Skip()
