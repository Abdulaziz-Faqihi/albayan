import wx
import wx.adv
from utils.const import Globals


class SystemTrayManager:
    def __init__(self, main_window, program_name: str, program_icon: str):
        self.main_window = main_window
        self.tray_icon = wx.adv.TaskBarIcon()
        
        # Load icon
        icon = wx.Icon(program_icon, wx.BITMAP_TYPE_ICO)
        self.tray_icon.SetIcon(icon, program_name)
        
        # Bind events
        self.tray_icon.Bind(wx.adv.EVT_TASKBAR_LEFT_DOWN, self.on_tray_icon_click)
        self.tray_icon.Bind(wx.adv.EVT_TASKBAR_RIGHT_DOWN, self.on_right_click)
        
        Globals.TRAY_ICON = self.tray_icon

    def on_right_click(self, event):
        """Show context menu on right click"""
        menu = wx.Menu()
        
        show_item = menu.Append(wx.ID_ANY, "إظهار النافذة الرئيسية")
        self.tray_icon.Bind(wx.EVT_MENU, lambda evt: self.show_main_window(), show_item)
        
        quit_item = menu.Append(wx.ID_EXIT, "إغلاق البرنامج")
        self.tray_icon.Bind(wx.EVT_MENU, lambda evt: self.main_window.menu_bar.quit_application(), quit_item)
        
        self.tray_icon.PopupMenu(menu)
        menu.Destroy()

    def show_main_window(self):
        if hasattr(self.main_window, 'menu_bar') and \
           hasattr(self.main_window.menu_bar, 'sura_player_window') and \
           self.main_window.menu_bar.sura_player_window is not None and \
           self.main_window.menu_bar.sura_player_window.IsShown():
            self.main_window.menu_bar.sura_player_window.Raise()
            self.main_window.menu_bar.sura_player_window.SetFocus()
            return

        self.main_window.Show()
        self.main_window.Raise()
        self.main_window.SetFocus()

    def on_tray_icon_click(self, event):
        self.show_main_window()

    def hide_icon(self):
        self.tray_icon.RemoveIcon()
        self.tray_icon.Destroy()

