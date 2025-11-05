"""Update helpers implemented with wxPython dialogs."""

from __future__ import annotations

import threading
from typing import Optional

import requests
import wx
from packaging import version

from utils.logger import Logger
from utils.settings import SettingsManager
from utils.const import program_name, program_version


class UpdateManager:
    """Check for application updates using a background thread."""

    UPDATE_URL = "https://raw.githubusercontent.com/tecwindow/albayan/main/info.json"

    def __init__(self, parent: Optional[wx.Window], auto_update: bool = False) -> None:
        self.parent = parent
        self.auto_update = auto_update
        self._session = requests.Session()

    def check_auto_update(self) -> None:
        if self.auto_update:
            self.check_updates()
        else:
            threading.Thread(target=self._warm_up, daemon=True).start()

    def check_updates(self) -> None:
        threading.Thread(target=self._fetch_update_info, daemon=True).start()

    def _warm_up(self) -> None:
        try:
            self._session.get(self.UPDATE_URL, timeout=5)
        except Exception as exc:  # pragma: no cover - warm up best effort
            Logger.info(f"Update warm up failed: {exc}")

    def _fetch_update_info(self) -> None:
        try:
            response = self._session.get(self.UPDATE_URL, timeout=15)
            response.raise_for_status()
            info = response.json()
        except requests.exceptions.ConnectionError:
            message = "لا يوجد اتصال بالإنترنت."
            Logger.info(message)
            if not self.auto_update:
                wx.CallAfter(self._show_error_message, message)
            return
        except Exception as exc:  # pragma: no cover - network failures
            message = "حدث خطأ أثناء الاتصال بالخادم."
            Logger.error(f"Update check failed: {exc}")
            if not self.auto_update:
                wx.CallAfter(self._show_error_message, message)
            return

        wx.CallAfter(self._handle_update_info, info)

    def _handle_update_info(self, info: dict) -> None:
        latest_version = info.get("latest_version")
        if not latest_version:
            return

        if version.parse(latest_version) <= version.parse(program_version):
            if not self.auto_update:
                wx.MessageBox(
                    f"أنت تستخدم {program_name} الإصدار {program_version}، وهو الإصدار الأحدث.",
                    "لا يوجد تحديث",
                    parent=self.parent,
                )
            return

        language = SettingsManager.current_settings["general"].get("language", "Arabic")
        release_notes = info.get("release_notes", {}).get(language)
        if not release_notes:
            release_notes = info.get("release_notes", {}).get("Arabic", "")
        download_url = info.get("download_url", "")
        self._show_update_dialog(release_notes, download_url, latest_version)

    def _show_error_message(self, error_message: str) -> None:
        wx.MessageBox(error_message, "خطأ", style=wx.ICON_ERROR | wx.OK, parent=self.parent)

    def _show_update_dialog(self, release_notes: str, download_url: str, latest_version: str) -> None:
        from ui.wx.dialogs.update_dialog import UpdateDialog

        dialog = UpdateDialog(self.parent, release_notes, download_url, latest_version)
        dialog.ShowModal()
        dialog.Destroy()
