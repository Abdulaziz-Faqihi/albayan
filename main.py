import sys
import os
from multiprocessing import freeze_support

import wx
from wx import adv as wxadv

current_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
os.chdir(current_dir)

from ui.wx.quran_interface import QuranInterface
from utils.update import UpdateManager
from utils.settings import SettingsManager
from utils.const import program_name
from utils.logger import Logger
from utils.audio_player import StartupSoundEffectPlayer, VolumeController


class AlbayanApp(wx.App):
    """Albayan main wxPython application."""

    def __init__(self):
        super().__init__(clearSigInt=True)
        self.instance_checker = None
        self.volume_controller = VolumeController()
        self.frame: QuranInterface | None = None

    def OnInit(self) -> bool:
        app_id = "Albayan" if sys.argv[0].endswith(".exe") else "Albayan_Source"
        self.instance_checker = wxadv.SingleInstanceChecker(app_id)
        if self.instance_checker.IsAnotherRunning():
            wx.MessageBox(
                "يعمل البرنامج بالفعل.",
                program_name,
                style=wx.ICON_INFORMATION | wx.OK,
            )
            return False

        self.SetAppName(program_name)
        self.frame = QuranInterface(None, title=program_name)
        if "--minimized" not in sys.argv:
            self.frame.Show()

        wx.CallAfter(self._post_startup)
        self._bind_global_shortcuts()
        return True

    def _bind_global_shortcuts(self) -> None:
        if not self.frame:
            return

        entries: list[wx.AcceleratorEntry] = []
        shortcuts = [
            (wx.ACCEL_NORMAL, wx.WXK_F5, "next_category"),
            (wx.ACCEL_NORMAL, wx.WXK_F6, "prev_category"),
            (wx.ACCEL_NORMAL, wx.WXK_F7, "vol_down_1"),
            (wx.ACCEL_SHIFT, wx.WXK_F7, "vol_down_5"),
            (wx.ACCEL_CTRL, wx.WXK_F7, "vol_down_10"),
            (wx.ACCEL_ALT, wx.WXK_F7, "vol_mute"),
            (wx.ACCEL_NORMAL, wx.WXK_F8, "vol_up_1"),
            (wx.ACCEL_SHIFT, wx.WXK_F8, "vol_up_5"),
            (wx.ACCEL_CTRL, wx.WXK_F8, "vol_up_10"),
            (wx.ACCEL_ALT, wx.WXK_F8, "vol_max"),
        ]

        for flags, keycode, command in shortcuts:
            cmd_id = wx.NewIdRef()
            entry = wx.AcceleratorEntry(flags, keycode, cmd_id)
            entries.append(entry)
            self.frame.Bind(wx.EVT_MENU, lambda evt, cmd=command: self._handle_volume_shortcut(cmd), id=cmd_id)

        self.frame.SetAcceleratorTable(wx.AcceleratorTable(entries))

    def _handle_volume_shortcut(self, command: str) -> None:
        mapping = {
            "next_category": lambda: self.volume_controller.switch_category("next"),
            "prev_category": lambda: self.volume_controller.switch_category("previous"),
            "vol_down_1": lambda: self.volume_controller.adjust_volume(-1),
            "vol_down_5": lambda: self.volume_controller.adjust_volume(-5),
            "vol_down_10": lambda: self.volume_controller.adjust_volume(-10),
            "vol_mute": lambda: self.volume_controller.adjust_volume(-100),
            "vol_up_1": lambda: self.volume_controller.adjust_volume(1),
            "vol_up_5": lambda: self.volume_controller.adjust_volume(5),
            "vol_up_10": lambda: self.volume_controller.adjust_volume(10),
            "vol_max": lambda: self.volume_controller.adjust_volume(100),
        }
        handler = mapping.get(command)
        if handler:
            handler()

    def _post_startup(self) -> None:
        if not self.frame:
            return

        basmala = StartupSoundEffectPlayer("Audio/basmala")
        basmala.play()

        check_update_enabled = SettingsManager.current_settings["general"].get("check_update_enabled", False)
        update_manager = UpdateManager(self.frame, check_update_enabled)
        update_manager.check_auto_update()
        self.frame.SetFocus()
        wx.CallLater(500, self.frame.focus_quran_view)


def main() -> None:
    try:
        app = AlbayanApp()
        app.MainLoop()
    except Exception as exc:  # pragma: no cover - safety net
        Logger.error(str(exc))
        wx.MessageBox(
            "حدث خطأ غير متوقع. إذا استمرت المشكلة يرجى مشاركة السجل مع المطورين.",
            "خطأ",
            style=wx.ICON_ERROR | wx.OK,
        )


if __name__ == "__main__":
    freeze_support()
    main()
