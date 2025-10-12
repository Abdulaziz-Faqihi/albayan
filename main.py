import sys
import os
current_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
os.chdir(current_dir)

from multiprocessing import freeze_support
import wx
import wx.adv
from ui.quran_interface import QuranInterface
from core_functions.athkar.athkar_scheduler import AthkarScheduler
from utils.update import UpdateManager
from utils.settings import SettingsManager
from utils.const import program_name, program_icon, user_db_path
from utils.logger import Logger
from utils.audio_player import StartupSoundEffectPlayer, VolumeController

class SingleInstanceApplication(wx.App):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        app_id = "Albayan" if sys.argv[0].endswith(".exe") else "Albayan_Source"
        self.SetAppName(program_name)
        self.instance_name = app_id
        self.instance_checker = wx.SingleInstanceChecker(app_id)
        self.volume_controller = VolumeController()
        
        if self.instance_checker.IsAnotherRunning():
            self.notify_existing_instance()
            return None
        
        self.setup_ipc_server()

    def setup_ipc_server(self) -> None:
        self.server = wx.adv.SimpleServer(wx.adv.IPCService(self.instance_name))
        self.server.Create(self.instance_name)

    def notify_existing_instance(self) -> None:
        client = wx.adv.IPCClient()
        connection = client.MakeConnection("localhost", self.instance_name, "SHOW")
        if connection:
            connection.Poke("SHOW", b"SHOW")
            connection.Disconnect()

    def set_main_window(self, main_window) -> None:
        self.main_window = main_window
        
    def ProcessEvent(self, event):
        """Process keyboard events for volume control"""
        if isinstance(event, wx.KeyEvent) and event.GetEventType() == wx.EVT_KEY_DOWN.typeId:
            keycode = event.GetKeyCode()
            modifiers = event.GetModifiers()
            
            if keycode == wx.WXK_F5:
                self.volume_controller.switch_category("next")
                return True
            elif keycode == wx.WXK_F6:
                self.volume_controller.switch_category("previous")
                return True
            elif keycode == wx.WXK_F7:
                if modifiers == wx.MOD_CONTROL:
                    self.volume_controller.adjust_volume(-10)
                elif modifiers == wx.MOD_SHIFT:
                    self.volume_controller.adjust_volume(-5)
                elif modifiers == wx.MOD_ALT:
                    self.volume_controller.adjust_volume(-100)
                else:
                    self.volume_controller.adjust_volume(-1)
                return True
            elif keycode == wx.WXK_F8:
                if modifiers == wx.MOD_CONTROL:
                    self.volume_controller.adjust_volume(10)
                elif modifiers == wx.MOD_SHIFT:
                    self.volume_controller.adjust_volume(5)
                elif modifiers == wx.MOD_ALT:
                    self.volume_controller.adjust_volume(100)
                else:
                    self.volume_controller.adjust_volume(1)
                return True
        
        return super().ProcessEvent(event)

def call_after_starting(parent: QuranInterface) -> None:
    basmala = StartupSoundEffectPlayer("Audio/basmala")
    basmala.play()

    check_update_enabled = SettingsManager.current_settings["general"].get("check_update_enabled", False)
    update_manager = UpdateManager(parent, check_update_enabled)
    update_manager.check_auto_update()

    parent.SetFocus()
    wx.CallLater(500, lambda: parent.quran_view.SetFocus() if hasattr(parent, 'quran_view') else None)

def main():
    try:
        app = SingleInstanceApplication()
        
        # Check if another instance is running
        if app.instance_checker.IsAnotherRunning():
            return
        
        main_window = QuranInterface(None, title=program_name)
        app.set_main_window(main_window)
        
        if "--minimized" not in sys.argv:
            main_window.Show()
        
        call_after_starting(main_window)
        app.MainLoop()
    except Exception as e:
        print(e)
        Logger.error(str(e))
        dlg = wx.MessageDialog(None, 
            "حدث خطأ، إذا استمرت المشكلة، يرجى تفعيل السجل وتكرار الإجراء الذي تسبب بالخطأ ومشاركة رمز الخطأ والسجل مع المطورين.",
            "خطأ",
            wx.OK | wx.ICON_ERROR)
        dlg.ShowModal()
        dlg.Destroy()

if __name__ == "__main__":    
    freeze_support()
    main()
