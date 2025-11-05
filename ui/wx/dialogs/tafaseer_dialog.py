"""wxPython tafaseer dialog."""

from __future__ import annotations

import os
from typing import Optional

import wx

from core_functions.tafaseer import TafaseerManager, Category
from utils.const import albayan_documents_dir, Globals
from utils.universal_speech import UniversalSpeech


class TafaseerDialog(wx.Dialog):
    def __init__(self, parent: Optional[wx.Window], ayah_info: list, default_category: str) -> None:
        title = f"تفسير آية {ayah_info[3]} من {ayah_info[2]}"
        super().__init__(parent, title=title, size=(600, 480))
        self.ayah_info = ayah_info
        self.manager = TafaseerManager()
        self.manager.set(Category.get_category_by_arabic_name(default_category))

        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.category_choice = wx.Choice(panel, choices=Category.get_categories_in_arabic())
        self.category_choice.SetStringSelection(default_category)
        self.category_choice.Bind(wx.EVT_CHOICE, self._on_category_changed)
        main_sizer.Add(self.category_choice, 0, wx.ALL | wx.EXPAND, 10)

        self.text_ctrl = wx.TextCtrl(
            panel,
            value=self.manager.get_tafaseer(ayah_info[0], ayah_info[1]),
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2,
        )
        self.text_ctrl.SetForegroundColour(wx.Colour(220, 220, 220))
        self.text_ctrl.SetBackgroundColour(wx.Colour(45, 45, 45))
        main_sizer.Add(self.text_ctrl, 1, wx.EXPAND | wx.ALL, 10)

        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        copy_button = wx.Button(panel, label="نسخ التفسير")
        copy_button.Bind(wx.EVT_BUTTON, self._copy_content)
        button_sizer.Add(copy_button, 0, wx.ALL, 5)

        save_button = wx.Button(panel, label="حفظ التفسير")
        save_button.Bind(wx.EVT_BUTTON, self._save_content)
        button_sizer.Add(save_button, 0, wx.ALL, 5)

        close_button = wx.Button(panel, wx.ID_OK, "إغلاق")
        button_sizer.Add(close_button, 0, wx.ALL, 5)

        main_sizer.Add(button_sizer, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)
        panel.SetSizer(main_sizer)

        Globals.effects_manager.play("open")

    def _on_category_changed(self, event: wx.CommandEvent) -> None:
        category = self.category_choice.GetStringSelection()
        self.manager.set(Category.get_category_by_arabic_name(category))
        self.text_ctrl.SetValue(self.manager.get_tafaseer(self.ayah_info[0], self.ayah_info[1]))
        self.text_ctrl.SetFocus()
        Globals.effects_manager.play("change")

    def _copy_content(self, event: wx.CommandEvent) -> None:
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(wx.TextDataObject(self.text_ctrl.GetValue()))
            wx.TheClipboard.Close()
        UniversalSpeech.say("تم نسخ التفسير.")
        Globals.effects_manager.play("copy")

    def _save_content(self, event: wx.CommandEvent) -> None:
        default_name = os.path.join(albayan_documents_dir, self.GetTitle() + ".txt")
        with wx.FileDialog(
            self,
            "حفظ التفسير",
            wildcard="Text files (*.txt)|*.txt",
            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
            defaultFile=default_name,
        ) as dlg:
            if dlg.ShowModal() != wx.ID_OK:
                return
            with open(dlg.GetPath(), "w", encoding="utf-8") as file:
                file.write(self.text_ctrl.GetValue())

    def EndModal(self, retCode: int) -> None:
        Globals.effects_manager.play("clos")
        super().EndModal(retCode)
