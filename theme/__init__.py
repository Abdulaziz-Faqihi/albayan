import os
import wx
from utils.logger import Logger

class ThemeManager:
    def __init__(self, window):
        self.window = window
        self.theme_dir = os.path.dirname(__file__)
        self.themes = {}

    def get_themes(self):

        self.themes = {"الافتراضي": "default"}
        for file in os.listdir(self.theme_dir):
            if file.endswith(".qss"):
                theme_name = os.path.splitext(file)[0]
                self.themes[theme_name] = file

        return list(self.themes.keys())

    def apply_theme(self, selected_theme):

        if selected_theme == "default":
            # Reset to default theme in wxPython
            # Note: wxPython doesn't use QSS stylesheets
            return

        theme_file = self.themes.get(selected_theme)
        if not theme_file:
            Logger.error(f"Theme not found: {selected_theme}")
            return None

        theme_path = os.path.join(self.theme_dir, theme_file)
        if not os.path.isfile(theme_path):
            Logger.error(f"File not found: {theme_path}")
            return None

        try:
            # Note: wxPython doesn't support QSS stylesheets
            # Theme files would need to be converted to wxPython styling
            Logger.warning("Theme system needs to be reimplemented for wxPython")
        except Exception as e:
            Logger.error(str(e))
            dlg = wx.MessageDialog(self.window, 
                "حدث خطأ أثناء تغيير الثيم.", 
                "خطأ", 
                wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()

