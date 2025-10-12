import wx
from utils.const import Globals


class GoToDialog(wx.Dialog):
    def __init__(self, parent, current_position: int, max: int, category_label: str):
        super().__init__(parent, title='الذهاب إلى', size=(300, 150))
        
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.label = wx.StaticText(panel, label='أدخل رقم ال{}:'.format(category_label))
        sizer.Add(self.label, 0, wx.ALL, 5)
        
        self.input_field = wx.SpinCtrl(panel, value=str(current_position), min=1, max=max)
        self.input_field.SetValue(current_position)
        self.input_field.SelectAll()
        sizer.Add(self.input_field, 0, wx.ALL | wx.EXPAND, 5)
        
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.go_to_button = wx.Button(panel, wx.ID_OK, 'اذهب')
        self.go_to_button.SetDefault()
        self.go_to_button.Bind(wx.EVT_BUTTON, self.on_go_to)
        button_sizer.Add(self.go_to_button, 0, wx.ALL, 5)
        
        self.cancel_button = wx.Button(panel, wx.ID_CANCEL, 'إغلاق')
        self.cancel_button.Bind(wx.EVT_BUTTON, self.on_cancel)
        button_sizer.Add(self.cancel_button, 0, wx.ALL, 5)
        
        # Set up accelerators for keyboard shortcuts
        accel_entries = [
            wx.AcceleratorEntry(wx.ACCEL_CTRL, ord('W'), wx.ID_CANCEL),
            wx.AcceleratorEntry(wx.ACCEL_CTRL, wx.WXK_F4, wx.ID_CANCEL)
        ]
        accel_table = wx.AcceleratorTable(accel_entries)
        self.SetAcceleratorTable(accel_table)
        
        sizer.Add(button_sizer, 0, wx.ALL | wx.CENTER, 5)
        panel.SetSizer(sizer)
        
        self.CenterOnParent()
    
    def on_go_to(self, event):
        if Globals.effects_manager:
            Globals.effects_manager.play("move")
        self.EndModal(wx.ID_OK)
    
    def on_cancel(self, event):
        self.EndModal(wx.ID_CANCEL)
    
    def get_input_value(self):
        return self.input_field.GetValue()

        