"""Search dialog implemented with wxPython."""

from __future__ import annotations

import json
import os
from typing import Optional

import wx

from core_functions.search import SearchCriteria, QuranSearchManager
from utils.settings import SettingsManager
from utils.const import Globals


class SearchDialog(wx.Dialog):
    def __init__(self, parent: Optional[wx.Window]):
        super().__init__(parent, title="بحث", size=(560, 520))
        self.parent = parent
        self.manager = QuranSearchManager()
        self.current_settings = SettingsManager.current_settings
        self.results: list[dict] = []
        self.selected_index: Optional[int] = None
        self._load_static_data()
        self._build_ui()

    def _load_static_data(self) -> None:
        with open(os.path.join("database", "Surahs.Json"), encoding="utf-8") as file:
            data = json.load(file)
        self.sura = data["surahs"]
        self.pages = [str(i) for i in range(1, 605)]
        self.quarters = [str(i) for i in range(1, 241)]
        self.jus = [str(i) for i in range(1, 31)]
        self.hizb = [str(i) for i in range(1, 61)]

    def _build_ui(self) -> None:
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.search_box = wx.TextCtrl(self)
        main_sizer.Add(wx.StaticText(self, label="اكتب ما تريد البحث عنه:"), 0, wx.ALL, 5)
        main_sizer.Add(self.search_box, 0, wx.ALL | wx.EXPAND, 5)

        options_box = wx.StaticBox(self, label="خيارات")
        options_sizer = wx.StaticBoxSizer(options_box, wx.VERTICAL)
        self.advanced_checkbox = wx.CheckBox(self, label="البحث المتقدم")
        options_sizer.Add(self.advanced_checkbox, 0, wx.ALL, 5)

        advanced_panel = wx.Panel(self)
        advanced_sizer = wx.GridBagSizer(5, 5)

        self.criteria_choice = wx.Choice(advanced_panel, choices=[
            "صفحة",
            "سورة",
            "جزء",
            "حزب",
            "ربع",
        ])
        self.criteria_choice.SetSelection(0)
        advanced_sizer.Add(wx.StaticText(advanced_panel, label="نوع البحث:"), (0, 0))
        advanced_sizer.Add(self.criteria_choice, (0, 1), flag=wx.EXPAND)

        self.from_choice = wx.Choice(advanced_panel)
        self.to_choice = wx.Choice(advanced_panel)
        advanced_sizer.Add(wx.StaticText(advanced_panel, label="من:"), (1, 0))
        advanced_sizer.Add(self.from_choice, (1, 1), flag=wx.EXPAND)
        advanced_sizer.Add(wx.StaticText(advanced_panel, label="إلى:"), (2, 0))
        advanced_sizer.Add(self.to_choice, (2, 1), flag=wx.EXPAND)

        self.ignore_tashkeel = wx.CheckBox(advanced_panel, label="تجاهل التشكيل")
        self.ignore_tashkeel.SetValue(self.current_settings["search"]["ignore_tashkeel"])
        self.ignore_hamza = wx.CheckBox(advanced_panel, label="تجاهل الهمزات")
        self.ignore_hamza.SetValue(self.current_settings["search"]["ignore_hamza"])
        self.match_whole_word = wx.CheckBox(advanced_panel, label="تطابق الكلمة بأكملها")
        self.match_whole_word.SetValue(self.current_settings["search"]["match_whole_word"])

        advanced_sizer.Add(self.ignore_tashkeel, (3, 0), span=(1, 2))
        advanced_sizer.Add(self.ignore_hamza, (4, 0), span=(1, 2))
        advanced_sizer.Add(self.match_whole_word, (5, 0), span=(1, 2))
        advanced_panel.SetSizer(advanced_sizer)
        options_sizer.Add(advanced_panel, 0, wx.ALL | wx.EXPAND, 5)

        main_sizer.Add(options_sizer, 0, wx.ALL | wx.EXPAND, 5)

        self.result_list = wx.ListBox(self)
        main_sizer.Add(self.result_list, 1, wx.ALL | wx.EXPAND, 5)

        button_sizer = wx.StdDialogButtonSizer()
        self.search_button = wx.Button(self, wx.ID_APPLY, "بحث")
        self.ok_button = wx.Button(self, wx.ID_OK, "انتقال")
        cancel_button = wx.Button(self, wx.ID_CANCEL, "إلغاء")
        button_sizer.AddButton(self.search_button)
        button_sizer.AddButton(self.ok_button)
        button_sizer.AddButton(cancel_button)
        button_sizer.Realize()
        main_sizer.Add(button_sizer, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 5)

        self.SetSizer(main_sizer)
        self._update_range_choices()
        self._toggle_advanced(self.advanced_checkbox.GetValue())

        self.advanced_checkbox.Bind(wx.EVT_CHECKBOX, lambda evt: self._toggle_advanced(evt.IsChecked()))
        self.criteria_choice.Bind(wx.EVT_CHOICE, lambda evt: self._update_range_choices())
        self.search_button.Bind(wx.EVT_BUTTON, self._on_search)
        self.result_list.Bind(wx.EVT_LISTBOX_DCLICK, lambda evt: self._confirm_selection())
        self.ok_button.Bind(wx.EVT_BUTTON, lambda evt: self._confirm_selection())

    def _toggle_advanced(self, enabled: bool) -> None:
        self.criteria_choice.Enable(enabled)
        self.from_choice.Enable(enabled)
        self.to_choice.Enable(enabled)
        self.ignore_tashkeel.Enable(enabled)
        self.ignore_hamza.Enable(enabled)
        self.match_whole_word.Enable(enabled)

    def _update_range_choices(self) -> None:
        self.from_choice.Clear()
        self.to_choice.Clear()
        selection = self.criteria_choice.GetStringSelection()
        if selection == "صفحة":
            items = self.pages
            criteria = SearchCriteria.page
        elif selection == "سورة":
            items = [sura["name"] for sura in self.sura]
            criteria = SearchCriteria.sura
        elif selection == "جزء":
            items = self.jus
            criteria = SearchCriteria.juz
        elif selection == "حزب":
            items = self.hizb
            criteria = SearchCriteria.hizb
        else:
            items = self.quarters
            criteria = SearchCriteria.quarter
        self.from_choice.AppendItems(items)
        self.to_choice.AppendItems(items)
        if items:
            self.from_choice.SetSelection(0)
            self.to_choice.SetSelection(len(items) - 1)
        self._current_criteria = criteria

    def _on_search(self, event: wx.CommandEvent) -> None:
        search_text = self.search_box.GetValue().strip()
        if not search_text:
            wx.MessageBox("يرجى إدخال نص للبحث.", "تنبيه", style=wx.ICON_INFORMATION)
            return

        if self.advanced_checkbox.GetValue():
            from_value = self.from_choice.GetStringSelection()
            to_value = self.to_choice.GetStringSelection()
            ignore_tashkeel = self.ignore_tashkeel.GetValue()
            ignore_hamza = self.ignore_hamza.GetValue()
            match_whole_word = self.match_whole_word.GetValue()
        else:
            from_value = 1
            to_value = 604
            ignore_tashkeel = self.current_settings["search"]["ignore_tashkeel"]
            ignore_hamza = self.current_settings["search"]["ignore_hamza"]
            match_whole_word = self.current_settings["search"]["match_whole_word"]

        self.manager.set(
            no_tashkil=ignore_tashkeel,
            no_hamza=ignore_hamza,
            match_whole_word=match_whole_word,
            criteria=self._current_criteria,
            _from=from_value,
            _to=to_value,
        )
        self.results = self.manager.search(search_text) or []
        self.result_list.Clear()
        if not self.results:
            wx.MessageBox("لا توجد نتائج متاحة لبحثك.", "لا توجد نتائج", style=wx.ICON_INFORMATION)
            return

        for result in self.results:
            text = result["text"]
            self.result_list.Append(f"{result['sura_name']} - {result['numberInSurah']}: {text[:60]}...")
        Globals.effects_manager.play("open")

    def _confirm_selection(self) -> None:
        idx = self.result_list.GetSelection()
        if idx == wx.NOT_FOUND:
            wx.MessageBox("يرجى اختيار نتيجة.", "تنبيه", style=wx.ICON_INFORMATION)
            return
        self.selected_index = idx
        self.EndModal(wx.ID_OK)

    def get_selected_ayah(self) -> Optional[int]:
        if self.selected_index is None:
            return None
        return self.results[self.selected_index]["number"]
