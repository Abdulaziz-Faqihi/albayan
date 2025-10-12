# PyQt6 to wxPython Conversion Status

## Overview
This document tracks the conversion of the Albayan application from PyQt6 to wxPython.

## Progress Summary
- **Total Files**: 32 files require conversion
- **Completed**: 15 files (46.88%)
- **Remaining**: 17 files (53.12%)

## Completed Files ✓

### Core Application (3 files)
1. ✓ `main.py` - Application entry point and single instance management
2. ✓ `requirements.txt` - Dependencies updated (PyQt6 → wxPython 4.2.1)
3. ✓ `setup.py` - Build configuration updated for wxPython

### Widgets (3 files)
4. ✓ `ui/widgets/button.py` - Custom button widget (QPushButton → wx.Button)
5. ✓ `ui/widgets/system_tray.py` - System tray (QSystemTrayIcon → wx.adv.TaskBarIcon)
6. ✓ `ui/widgets/qText_edit.py` - Text editor (QTextEdit → wx.richtext.RichTextCtrl)

### Dialogs (1 file)
7. ✓ `ui/dialogs/go_to.py` - Go-to dialog (QDialog → wx.Dialog)

### Utility Files (5 files)
8. ✓ `utils/const.py` - Removed PyQt6 import
9. ✓ `theme/__init__.py` - Theme manager (QSS not supported, needs reimplementation)
10. ✓ `utils/audio_player/sura_player.py` - Removed unused import
11. ✓ `utils/audio_player/ayah_player.py` - Removed unused import

### Core Functions (3 files)
12. ✓ `core_functions/bookmark.py` - Removed unused import
13. ✓ `core_functions/tasbih/controller.py` - Converted to wx.EvtHandler with custom events
14. ✓ `core_functions/athkar/athkar_scheduler.py` - Updated tray notifications

## Critical Path Files (BLOCKING - Must be completed for app to run)

### ⚠️ Main Window Components (4 files - 1,111 lines)
- [ ] **ui/quran_interface.py** (470 lines) - Main window (QMainWindow → wx.Frame)
- [ ] **ui/widgets/menu_bar.py** (374 lines) - Menu bar (QMenuBar → wx.MenuBar)
- [ ] **ui/widgets/toolbar.py** (267 lines) - Toolbar (QToolBar → wx.ToolBar)
- [ ] **utils/update.py** - Update manager (QThread → wx.lib.delayedresult)

**These 4 files are interdependent and the application cannot run without them.**

## Remaining Dialogs (10 files)

15. [ ] `ui/dialogs/athkar_dialog.py` - Athkar management dialog (~150 lines)
16. [ ] `ui/dialogs/prophets_stories_dialog.py` - Prophet stories dialog
17. [ ] `ui/dialogs/info_dialog.py` - Info display dialog
18. [ ] `ui/dialogs/quick_access.py` - Quick access navigation
19. [ ] `ui/dialogs/tafaseer_Dialog.py` - Tafseer (interpretation) dialog
20. [ ] `ui/dialogs/find.py` - Search dialog
21. [ ] `ui/dialogs/settings_dialog.py` - Settings dialog (~500 lines)
22. [ ] `ui/dialogs/bookmark_dialog.py` - Bookmark management
23. [ ] `ui/dialogs/update_dialog.py` - Update notification dialog
24. [ ] `ui/dialogs/tasbih_dialog.py` - Tasbih counter dialog

## Remaining Sura Player UI (5 files)

25. [ ] `ui/sura_player_ui/sura_player_ui.py` - Sura player window
26. [ ] `ui/sura_player_ui/menubar.py` - Player menu bar
27. [ ] `ui/sura_player_ui/audio_looper.py` - Audio looping functionality
28. [ ] `ui/sura_player_ui/FilterManager.py` - Filter manager
29. [ ] `ui/sura_player_ui/key_handler.py` - Key event handler

## Conversion Patterns Used

### Widgets
- `QDialog` → `wx.Dialog`
- `QMainWindow` → `wx.Frame`
- `QPushButton` → `wx.Button`
- `QLabel` → `wx.StaticText`
- `QTextEdit` → `wx.richtext.RichTextCtrl` or `wx.TextCtrl`
- `QSpinBox` → `wx.SpinCtrl`
- `QComboBox` → `wx.ComboBox`
- `QCheckBox` → `wx.CheckBox`
- `QRadioButton` → `wx.RadioButton`
- `QSystemTrayIcon` → `wx.adv.TaskBarIcon`

### Layouts
- `QVBoxLayout` → `wx.BoxSizer(wx.VERTICAL)`
- `QHBoxLayout` → `wx.BoxSizer(wx.HORIZONTAL)`
- `QGridLayout` → `wx.GridSizer` or `wx.FlexGridSizer`
- `addWidget()` → `Add()`
- `setLayout()` → `SetSizer()`

### Events
- `pyqtSignal` → `wx.lib.newevent.NewEvent()`
- `signal.connect()` → `Bind()`
- `signal.emit()` → `wx.PostEvent()`
- `QObject` → `wx.EvtHandler`

### Keyboard Shortcuts
- `QKeySequence` → `wx.AcceleratorTable`
- `QShortcut` → Accelerator entries
- `setShortcut()` → `SetAcceleratorTable()`

### Dialogs & Windows
- `exec()` → `ShowModal()`
- `accept()` → `EndModal(wx.ID_OK)`
- `reject()` → `EndModal(wx.ID_CANCEL)`
- `show()` → `Show()`
- `hide()` → `Hide()`
- `close()` → `Close()`
- `setWindowTitle()` → Set in constructor or `SetTitle()`
- `resize()` → `SetSize()`

### Timers
- `QTimer.singleShot()` → `wx.CallLater()`
- `QTimer` → `wx.Timer`

### Threading
- `QThread` → `wx.lib.delayedresult` or Python `threading` module
- `pyqtSignal` for thread communication → `wx.CallAfter()` or custom events

## Major Technical Challenges

### 1. Icon System
**Challenge**: qtawesome (Font Awesome icons for PyQt) has no direct wxPython equivalent.

**Solutions**:
- Remove icons (current approach for simplicity)
- Use wx.ArtProvider for built-in icons
- Load PNG/ICO files directly
- Use a separate icon library

### 2. Stylesheet System (QSS)
**Challenge**: wxPython doesn't support Qt StyleSheets (QSS).

**Solutions**:
- Use wxPython's native styling (SetForegroundColour, SetBackgroundColour, SetFont)
- Implement custom rendering
- Accept default system theme

### 3. Rich Text Handling
**Challenge**: QTextEdit has extensive rich text capabilities that differ from wx.richtext.RichTextCtrl.

**Solutions**:
- Use wx.richtext.RichTextCtrl for formatted text
- Use wx.TextCtrl for simple text
- May need to adapt HTML/formatting approaches

### 4. Signal/Slot System
**Challenge**: PyQt6's signal/slot system is more integrated than wx Events.

**Solutions**:
- Use `wx.lib.newevent.NewEvent()` for custom events
- Use `Bind()` for event connections
- Use `wx.CallAfter()` for cross-thread communication

### 5. Layout Management
**Challenge**: Different layout paradigms (QLayout vs wx.Sizer).

**Solutions**:
- Convert layouts manually
- Use proportion and flags in Add() calls
- Test layout behavior carefully

## Known Issues & Limitations

1. **Theme System**: QSS themes will not work and need complete reimplementation
2. **Icons**: qtawesome icons removed, may need alternative icon solution
3. **RTL Text**: Right-to-left text direction handling may need adjustment
4. **Keyboard Shortcuts**: Some complex shortcut combinations may behave differently
5. **IPC**: Single instance communication simplified (may need adjustment)

## Estimated Remaining Work

### Time Estimates
- **Main Window Files** (4 files, ~1,111 lines): 8-12 hours
- **Dialogs** (10 files): 6-10 hours
- **Sura Player UI** (5 files): 4-6 hours
- **Integration Testing**: 8-10 hours
- **Bug Fixing**: 8-12 hours
- **Documentation**: 2-4 hours

**Total Estimated**: 36-54 hours of development work

### Risk Assessment
- **High Risk**: Main window integration, menu system, toolbar functionality
- **Medium Risk**: Dialog conversions, keyboard shortcuts, RTL text handling
- **Low Risk**: Remaining utility file conversions

## Testing Strategy

### Unit Testing
- Test individual widgets and dialogs
- Test event handling
- Test layout behavior

### Integration Testing
- Test main window with all components
- Test navigation and interactions
- Test audio playback features
- Test bookmark and tasbih features
- Test settings and preferences

### Platform Testing
- Test on Windows (primary platform)
- Test on Linux (if applicable)
- Test on macOS (if applicable)

## Migration Recommendations

### For Future Conversions
1. Start with utility files and simple dialogs
2. Create conversion patterns and document them
3. Convert widgets before windows that use them
4. Test frequently during conversion
5. Keep PyQt6 version in a branch for reference

### For This Project
1. Complete the critical path files first (main window, menu bar, toolbar)
2. Test basic application functionality
3. Convert dialogs one by one
4. Convert sura player UI
5. Comprehensive integration testing
6. Bug fixing and polish

## Notes

- This is a **major framework migration**, not a simple refactoring
- The application **cannot run** until all critical path files are converted
- Extensive testing is required after conversion
- Some features may need to be reimplemented due to API differences
- User experience may change slightly due to framework differences

## Resources

- [wxPython Documentation](https://docs.wxpython.org/)
- [wxPython Phoenix Migration Guide](https://wxpython.org/Phoenix/docs/html/MigrationGuide.html)
- [PyQt to wxPython Conversion Guide](https://wiki.wxpython.org/PyQtAndwxPython)

---

Last Updated: 2025-10-12
Conversion Progress: 46.88% (15/32 files)
