import wx


class EnterButton(wx.Button):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.Bind(wx.EVT_KEY_DOWN, self.on_key_press)
    
    def on_key_press(self, event):
        keycode = event.GetKeyCode()
        if keycode in {wx.WXK_RETURN, wx.WXK_SPACE, wx.WXK_NUMPAD_ENTER}:
            # Emit a button click event
            click_event = wx.PyCommandEvent(wx.EVT_BUTTON.typeId, self.GetId())
            wx.PostEvent(self, click_event)
        else:
            event.Skip()

