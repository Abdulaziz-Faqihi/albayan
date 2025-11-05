"""Quick access dialog implemented with wxPython."""

from __future__ import annotations

import json
import os
from typing import Optional

import wx

from utils.audio_player import SoundEffectPlayer


class QuickAccessDialog(wx.Dialog):
    def __init__(self, parent: Optional[wx.Window]):
        super().__init__(parent, title="الوصول السريع", size=(360, 360))
        self.SetBackgroundColour(wx.Colour(30, 30, 30))
        self.effects_manager = SoundEffectPlayer("Audio/sounds")
        with open(os.path.join("database", "Surahs.Json"), encoding="utf-8") as file:
            data = json.load(file)
        self.sura = data["surahs"]
        self.pages = [str(i) for i in range(1, 605)]
        self.quarters = [str(i) for i in range(1, 241)]
        self.jus = [str(i) for i in range(1, 31)]
        self.hizb = [str(i) for i in range(1, 61)]
        self._selected_result: Optional[str] = None
        self._build_ui()

    def _build_ui(self) -> None:
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        view_box = wx.StaticBox(self, label="عرض وفقا ل:")
        view_sizer = wx.StaticBoxSizer(view_box, wx.VERTICAL)
        self.sura_radio = wx.RadioButton(self, label="سور", style=wx.RB_GROUP)
        self.pages_radio = wx.RadioButton(self, label="صفحات")
        self.quarters_radio = wx.RadioButton(self, label="أرباع")
        self.hizb_radio = wx.RadioButton(self, label="أحزاب")
        self.jus_radio = wx.RadioButton(self, label="أجزاء")
        for control in (
            self.sura_radio,
            self.pages_radio,
            self.quarters_radio,
            self.hizb_radio,
            self.jus_radio,
        ):
            view_sizer.Add(control, 0, wx.ALL, 2)

        self.choice_label = wx.StaticText(self, label="انتقل إلى:")
        self.choice = wx.Choice(self)

        button_sizer = wx.StdDialogButtonSizer()
        self.go_button = wx.Button(self, wx.ID_OK, "اذهب")
        cancel_button = wx.Button(self, wx.ID_CANCEL, "إلغاء")
        button_sizer.AddButton(self.go_button)
        button_sizer.AddButton(cancel_button)
        button_sizer.Realize()

        main_sizer.Add(view_sizer, 0, wx.ALL | wx.EXPAND, 10)
        main_sizer.Add(self.choice_label, 0, wx.LEFT | wx.RIGHT, 10)
        main_sizer.Add(self.choice, 0, wx.ALL | wx.EXPAND, 10)
        main_sizer.Add(button_sizer, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 10)

        self.SetSizer(main_sizer)

        self.sura_radio.SetValue(True)
        self._populate_choices()

        self.Bind(wx.EVT_RADIOBUTTON, lambda evt: self._populate_choices())
        self.Bind(wx.EVT_BUTTON, self._on_submit, id=wx.ID_OK)

    def _populate_choices(self) -> None:
        self.choice.Clear()
        if self.sura_radio.GetValue():
            self.choice.AppendItems([sura["name"] for sura in self.sura])
        elif self.pages_radio.GetValue():
            self.choice.AppendItems(self.pages)
        elif self.quarters_radio.GetValue():
            self.choice.AppendItems(self.quarters)
        elif self.hizb_radio.GetValue():
            self.choice.AppendItems(self.hizb)
        elif self.jus_radio.GetValue():
            self.choice.AppendItems(self.jus)
        if self.choice.GetCount():
            self.choice.SetSelection(0)

    def _on_submit(self, event: wx.CommandEvent) -> None:
        if self.choice.GetSelection() == wx.NOT_FOUND:
            event.Veto()
            return
        index = self.choice.GetSelection() + 1
        parent = self.GetParent()
        if not parent:
            return
        if self.sura_radio.GetValue():
            self._selected_result = parent.quran.get_surah(index)
        elif self.pages_radio.GetValue():
            self._selected_result = parent.quran.get_page(index)
        elif self.quarters_radio.GetValue():
            self._selected_result = parent.quran.get_quarter(index)
        elif self.hizb_radio.GetValue():
            self._selected_result = parent.quran.get_hizb(index)
        elif self.jus_radio.GetValue():
            self._selected_result = parent.quran.get_juzz(index)
        self.effects_manager.play("change")
        self.EndModal(wx.ID_OK)

    def get_selected_text(self) -> Optional[str]:
        return self._selected_result
