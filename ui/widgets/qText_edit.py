import re
import wx
import wx.richtext as rt
from utils.settings import SettingsManager
from utils.const import Globals


class ReadOnlyTextEdit(rt.RichTextCtrl):
    def __init__(self, parent=None):
        super().__init__(parent, style=wx.TE_READONLY | wx.TE_MULTILINE | wx.TE_RICH2 | wx.HSCROLL | wx.VSCROLL)
        self.parent = parent
        self.SetEditable(False)
        
        # Set font
        font = wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        text_attr = rt.RichTextAttr()
        text_attr.SetFont(font)
        self.SetBasicStyle(text_attr)
        
        # Enable word wrapping or not
        # self.SetWrapMode(wx.richtext.RICHTEXT_WRAP_WORD)  # For wrapping
        self.SetWrapMode(wx.richtext.RICHTEXT_WRAP_NONE)  # No wrapping


class QuranViewer(ReadOnlyTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.is_page_turn_alert = False
        self.Bind(wx.EVT_TEXT, self.set_ctrl)
        self.Bind(wx.EVT_KEY_DOWN, self.on_key_press)

    def set_ctrl(self, event=None):
        """Update control states based on current text"""
        try:
            # Get current line text
            insertion_point = self.GetInsertionPoint()
            current_line_text = self.GetLineText(self.GetCurrentLine())
            
            # Check status
            status = False if "سُورَةُ" in current_line_text or current_line_text == "|" or not re.search(r"\(\d+\)$", current_line_text) else True
            
            # Enable/disable controls based on status
            if hasattr(self.parent, 'interpretation_verse'):
                self.parent.interpretation_verse.Enable(status)
            if hasattr(self.parent, 'save_current_position'):
                self.parent.save_current_position.Enable(status)
            if hasattr(self.parent, 'menu_bar'):
                self.parent.menu_bar.save_position_action.Enable(status)
                self.parent.menu_bar.save_bookmark_action.Enable(status)
                self.parent.menu_bar.verse_tafsir_action.Enable(status)
                self.parent.menu_bar.tafaseer_menu.Enable(status)
                self.parent.menu_bar.ayah_info_action.Enable(status)
                self.parent.menu_bar.verse_info_action.Enable(status)
                self.parent.menu_bar.verse_grammar_action.Enable(status)
                self.parent.menu_bar.copy_verse_action.Enable(status)
        except:
            pass
        
        if event:
            event.Skip()

    def on_key_press(self, event):
        """Handle key press events"""
        keycode = event.GetKeyCode()
        modifiers = event.GetModifiers()
        
        # Call set_ctrl after key press
        wx.CallAfter(self.set_ctrl)
        
        # Handle Space key
        if keycode == wx.WXK_SPACE:
            if modifiers == wx.MOD_CONTROL:  # Ctrl + Space
                if hasattr(self.parent, 'toolbar'):
                    self.parent.toolbar.stop_audio()
                return
            elif modifiers == wx.MOD_SHIFT or modifiers == wx.MOD_NONE:
                if hasattr(self.parent, 'toolbar'):
                    self.parent.toolbar.toggle_play_pause()
                return
        
        # Handle Ctrl+Shift for text direction
        if modifiers == wx.MOD_CONTROL and keycode == wx.WXK_SHIFT:
            # Note: scan code detection is platform-specific and complex in wxPython
            # Simplified implementation
            pass
        
        # Auto page turn feature
        if not SettingsManager.current_settings["reading"].get("auto_page_turn", False):
            event.Skip()
            return
        
        current_line = self.GetCurrentLine()
        total_lines = self.GetNumberOfLines()
        
        if current_line >= 1 and current_line + 1 != total_lines:
            self.is_page_turn_alert = False
        
        # Handle Up arrow
        if keycode == wx.WXK_UP:
            if (current_line == 0) and hasattr(self.parent, 'quran') and (self.parent.quran.current_pos > 1):
                if not self.is_page_turn_alert:
                    self.is_page_turn_alert = True
                    if Globals.effects_manager:
                        Globals.effects_manager.play("alert")
                    event.Skip()
                    return
                if hasattr(self.parent, 'OnBack'):
                    self.parent.OnBack(is_auto_call=True)
        # Handle Down arrow
        elif keycode == wx.WXK_DOWN:
            if (current_line == total_lines - 1) and hasattr(self.parent, 'quran') and (self.parent.quran.current_pos < self.parent.quran.max_pos):
                if not self.is_page_turn_alert:
                    self.is_page_turn_alert = True
                    if Globals.effects_manager:
                        Globals.effects_manager.play("alert")
                    event.Skip()
                    return
                if hasattr(self.parent, 'OnNext'):
                    self.parent.OnNext()
        
        event.Skip()

