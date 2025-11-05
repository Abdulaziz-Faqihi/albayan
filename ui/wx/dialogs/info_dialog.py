"""Generic information dialog used across the application."""

from __future__ import annotations

import os
from typing import Optional

import wx

from utils.universal_speech import UniversalSpeech
from utils.const import Globals, albayan_documents_dir


class InfoDialog(wx.Dialog):
    def __init__(
        self,
        parent: Optional[wx.Window],
        title: str,
        label: str,
        text: str,
        is_html: bool = False,
        show_message_button: bool = False,
        save_message_as_img_button: bool = False,
    ) -> None:
        super().__init__(parent, title=title, size=(600, 480))
        self.text = text
        panel = wx.Panel(self)
        panel.SetBackgroundColour(wx.Colour(30, 30, 30))

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        label_ctrl = wx.StaticText(panel, label=label)
        label_ctrl.SetForegroundColour(wx.Colour(255, 255, 255))
        main_sizer.Add(label_ctrl, 0, wx.ALL, 10)

        self.text_ctrl = wx.TextCtrl(
            panel,
            value=text,
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2,
        )
        self.text_ctrl.SetForegroundColour(wx.Colour(220, 220, 220))
        self.text_ctrl.SetBackgroundColour(wx.Colour(45, 45, 45))
        main_sizer.Add(self.text_ctrl, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        copy_button = wx.Button(panel, label="نسخ")
        copy_button.Bind(wx.EVT_BUTTON, self.copy_text)
        button_sizer.Add(copy_button, 0, wx.ALL, 5)

        if show_message_button:
            message_button = wx.Button(panel, label="رسالة لك")
            message_button.Bind(wx.EVT_BUTTON, self.choose_quotes_message)
            button_sizer.Add(message_button, 0, wx.ALL, 5)

        if save_message_as_img_button:
            save_button = wx.Button(panel, label="حفظ كصورة")
            save_button.Bind(wx.EVT_BUTTON, self.save_text_as_image)
            button_sizer.Add(save_button, 0, wx.ALL, 5)

        close_button = wx.Button(panel, wx.ID_OK, "إغلاق")
        button_sizer.Add(close_button, 0, wx.ALL, 5)

        main_sizer.Add(button_sizer, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)
        panel.SetSizer(main_sizer)

        Globals.effects_manager.play("open")
        self.text_ctrl.SetFocus()

    def copy_text(self, event: wx.CommandEvent) -> None:
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(wx.TextDataObject(self.text_ctrl.GetValue()))
            wx.TheClipboard.Close()
        UniversalSpeech.say("تم نسخ النص إلى الحافظة")
        Globals.effects_manager.play("copy")

    def choose_quotes_message(self, event: wx.CommandEvent) -> None:
        from utils.const import data_folder
        import json
        import random

        file_path = data_folder / "quotes/QuotesMessages.json"
        if not file_path.exists():
            wx.MessageBox(f"الملف غير موجود: {file_path}", "خطأ", style=wx.ICON_ERROR)
            return
        with open(file_path, "r", encoding="utf-8") as file:
            quotes_list = json.load(file)
        message = random.choice(quotes_list)
        self.text_ctrl.SetValue(message)
        UniversalSpeech.say(message)
        Globals.effects_manager.play("message")

    def save_text_as_image(self, event: wx.CommandEvent) -> None:
        wx.MessageBox("ميزة الحفظ كصورة غير متاحة حاليًا في إصدار wxPython.", "تنبيه", style=wx.ICON_INFORMATION)

    def EndModal(self, retCode: int) -> None:
        Globals.effects_manager.play("clos")
        super().EndModal(retCode)
