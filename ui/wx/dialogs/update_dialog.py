"""wxPython dialog informing users about available updates."""

from __future__ import annotations

import webbrowser
from typing import Optional

import wx

from utils.const import program_name


class UpdateDialog(wx.Dialog):
    def __init__(self, parent: Optional[wx.Window], release_notes: str, download_url: str, latest_version: str) -> None:
        super().__init__(parent, title="تحديث جديد متاح", size=(520, 420))
        self.download_url = download_url

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(wx.StaticText(self, label=f"يتوفر إصدار جديد من {program_name}: {latest_version}"), 0, wx.ALL, 10)

        self.notes_ctrl = wx.TextCtrl(
            self,
            value=release_notes,
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2,
        )
        sizer.Add(self.notes_ctrl, 1, wx.ALL | wx.EXPAND, 10)

        button_sizer = wx.StdDialogButtonSizer()
        download_button = wx.Button(self, wx.ID_OK, "تحميل")
        later_button = wx.Button(self, wx.ID_CANCEL, "لاحقًا")
        button_sizer.AddButton(download_button)
        button_sizer.AddButton(later_button)
        button_sizer.Realize()
        sizer.Add(button_sizer, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 10)

        self.SetSizer(sizer)
        download_button.Bind(wx.EVT_BUTTON, self._open_download)

    def _open_download(self, event: wx.CommandEvent) -> None:
        if self.download_url:
            webbrowser.open(self.download_url)
        self.EndModal(wx.ID_OK)
