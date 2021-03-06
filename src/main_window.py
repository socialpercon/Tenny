import keyboard
from PyQt5.QtWidgets import (QWidget,
                             QPushButton,
                             QLCDNumber,
                             QGridLayout,
                             QSystemTrayIcon,
                             QMenu,
                             QAction,
                             QMessageBox)
from PyQt5.QtCore import (QTime,
                          QTimer,
                          Qt,
                          QSettings)
from PyQt5.QtGui import QIcon
from src.dialog.preferences import SetOpacity
from resources import tenny_resources


__title__ = 'Tenny'
__author__ = 'mokachokokarbon'
__version__ = '0.4'
DEFAULT_STORT_SHORTCUT = 'shift+f1'
DEFAULT_RESET_SHORTCUT = 'shift+f2'
DEFAULT_QUIT_SHORCUT = 'ctrl+q'
DEFAULT_OPACITY_VALUE = 0.7


# [] TODO: separate the logic and UI, this class is getting heavier
class Ten(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._START = '&START'
        self._STOP = '&STOP'
        self._RESET = '&RESET'
        self._FORMAT = 'hh:mm:ss.zzz'
        self.close_shortcut = False
        self.stort_hotkey = DEFAULT_STORT_SHORTCUT
        self.reset_hotkey = DEFAULT_RESET_SHORTCUT
        self.quit_hotkey = DEFAULT_QUIT_SHORCUT
        self.opacity_value = DEFAULT_OPACITY_VALUE
        self._EXISTING_HOTKEYS = {'Start/Stop': DEFAULT_STORT_SHORTCUT,
                                  'Reset': DEFAULT_RESET_SHORTCUT,
                                  'Quit': self.quit_hotkey}
        self._operations = {'Start/Stop': self._update_stort_hotkey,
                            'Reset': self._update_reset_hotkey}
        self._read_settings()
        self._create_actions()
        self._create_menus()
        self._widgets()
        self._layout()
        self._properties()
        self._connections()
        self._hotkeys()

    def _create_actions(self):

        # self.tennyMenu actions
        self.openAction = QAction('Open Tenny', self,
                                  triggered=self.on_openTenny_action)
        self.stortAction = QAction('Start/Stop', self,
                                   triggered=self.stort_timer,
                                   shortcut=self.stort_hotkey)
        self.resetAction = QAction('Reset', self,
                                   triggered=self.reset_timer,
                                   shortcut=self.reset_hotkey)

        # self.setShortCutKeysMenu actions
        self.set_stortAction = QAction('Start/Stop', self,
                                       triggered=self.on_setShortcut_action)
        self.set_resetAction = QAction('Reset', self,
                                       triggered=self.on_setShortcut_action)
        self.set_opacityAction = QAction('Set Opacity', self,
                                         triggered=self.on_setOpacity_action)
        self.quitAction = QAction('Quit Tenny', self,
                                  shortcut=self.quit_hotkey,
                                  triggered=self.close)

    def _create_menus(self):

        # Sub-menu
        self.setShortCutKeysMenu = QMenu('Set Shortcut Keys')
        self.setShortCutKeysMenu.addAction(self.set_stortAction)
        self.setShortCutKeysMenu.addAction(self.set_resetAction)

        # Main menu
        self.tennyMenu = QMenu()
        self.tennyMenu.addAction(self.openAction)
        self.tennyMenu.addAction(self.stortAction)
        self.tennyMenu.addAction(self.resetAction)
        self.tennyMenu.addSeparator()
        self.tennyMenu.addMenu(self.setShortCutKeysMenu)
        self.tennyMenu.addAction(self.set_opacityAction)
        self.tennyMenu.addSeparator()
        self.tennyMenu.addAction(self.quitAction)

    def _widgets(self):

        self.shiverTimer = QTime(0, 0, 0)
        self.timer = QTimer()
        self.timerLCDNumber = QLCDNumber()
        self.stortPushButton = QPushButton(self._START)
        self.resetPushButton = QPushButton(self._RESET)
        self.set_opacityDialog = SetOpacity()
        self.tennySystemTray = QSystemTrayIcon()
        self.setShortcutMessageBox = QMessageBox(self)

    def _layout(self):

        grid = QGridLayout()
        grid.addWidget(self.timerLCDNumber, 0, 0, 1, 2)
        grid.addWidget(self.stortPushButton, 1, 0)
        grid.addWidget(self.resetPushButton, 1, 1)

        self.setLayout(grid)

    def _properties(self):

        # Main window
        self.setWindowIcon(QIcon(':/stopwatch-32.png'))
        self.resize(350, 125)
        self.setWindowTitle(f'{__title__}')
        self.setWindowOpacity(self.opacity_value)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        self.timerLCDNumber.setDigitCount(12)
        self.timerLCDNumber.display("00:00:00.000")

        self.stortPushButton.setToolTip(self.stort_hotkey)
        self.resetPushButton.setToolTip(self.reset_hotkey)

        self.set_opacityDialog.opacityLabel.setText(f'{self.opacity_value * 100:.0f}')
        self.set_opacityDialog.opacitySlider.setSliderPosition(self.opacity_value * 100)

        # SetShortcut QMessageBox
        self.setShortcutMessageBox.setIcon(QMessageBox.Warning)
        self.setShortcutMessageBox.setWindowTitle('Set Shortcut Message')

        self.tennySystemTray.setIcon(QIcon(':/stopwatch-32.png'))
        self.tennySystemTray.setToolTip(f'{__title__} {__version__}')
        self.tennySystemTray.setContextMenu(self.tennyMenu)
        self.tennySystemTray.show()

    def _connections(self):

        self.timer.timeout.connect(self.showStopwatch)
        self.stortPushButton.clicked.connect(self.on_stortPushButton_clicked)
        self.resetPushButton.clicked.connect(self.on_resetPushButton_clicked)
        self.set_opacityDialog.opacitySlider.valueChanged.connect(self.on_opacitySlider_valueChanged)

    def _hotkeys(self):

        keyboard.add_hotkey(self.stort_hotkey, self.stortPushButton.click)
        keyboard.add_hotkey(self.reset_hotkey, self.resetPushButton.click)

    def _read_settings(self):
        """ Method for restoring Tenny's position, size and values. """

        settings = QSettings('GIPSC Core Team', 'Tenny')
        self.restoreGeometry(settings.value('tenny_geometry', self.saveGeometry()))
        self.stort_hotkey = settings.value('tenny_stort_hotkey', self.stort_hotkey)
        self.reset_hotkey = settings.value('tenny_reset_hotkey', self.reset_hotkey)
        self.opacity_value = float(settings.value('tenny_opacity', self.opacity_value))
        self._EXISTING_HOTKEYS.update({'Start/Stop': self.stort_hotkey,
                                       'Reset': self.reset_hotkey})

    def showStopwatch(self):
        """ Event handler for showing elapsed time, just like a stopwatch. """

        self.shiverTimer = self.shiverTimer.addMSecs(1)
        text = self.shiverTimer.toString(self._FORMAT)
        self.timerLCDNumber.display(text)

    def on_stortPushButton_clicked(self):
        """ Call self.stort_timer to activate the timer. """

        self.stort_timer()

    def stort_timer(self):
        """ Method that will start or stop the timer. """

        if self.stortPushButton.text() == self._START:
            self.timer.start(1)
            self.stortPushButton.setText(self._STOP)
        else:
            self.timer.stop()
            self.stortPushButton.setText(self._START)

    def on_resetPushButton_clicked(self):
        """ Call self.reset_timer to reset the timer. """

        self.reset_timer()

    def reset_timer(self):
        """ Method that will reset the timer. """

        self.timer.stop()
        self.shiverTimer = QTime(0, 0, 0)
        self.timerLCDNumber.display(self.shiverTimer.toString(self._FORMAT))

        if self.stortPushButton.text() == self._STOP:
            self.stortPushButton.setText(self._START)

    def on_openTenny_action(self):
        """ Show Tenny window if its hidden. """

        if self.isHidden():
            self.show()

    def on_setShortcut_action(self):

        which_action = self.sender()
        text = which_action.text()

        from src.dialog.preferences import SetShortcut
        dialog = SetShortcut(self)
        dialog.setWindowTitle(f'Set Shortcut for {text}')

        # [] TODO: make this block of code Pythonic, so far so good
        # [] TODO: show a notification via Notif area, after update_hotkey()
        if dialog.exec():
            selected_hotkey = dialog.selected_hotkeys
            if selected_hotkey not in self._EXISTING_HOTKEYS.values():
                update_hotkey = self._operations.get(text)
                update_hotkey(text, selected_hotkey)
            else:
                hotkey_owner = self._get_hotkey_owner(selected_hotkey)
                self._show_setShortcutMessageBox(selected_hotkey, hotkey_owner)

    def _get_hotkey_owner(self, user_hotkey):
        """ Return the current owner of an existing hotkey. """

        for k, v in self._EXISTING_HOTKEYS.items():
            if user_hotkey == v:
                return k

    def _show_setShortcutMessageBox(self, hotkey, owner):
        """ Set the text and show the message box. """

        self.setShortcutMessageBox.setText(f'\'{hotkey}\' already registered as shortcut for <b>{owner}</b> button. Try again.')
        self.setShortcutMessageBox.show()

    def _update_stort_hotkey(self, text, selected_hotkey):

        keyboard.remove_hotkey(self.stort_hotkey)                           # Remove previous hotkey
        self.stort_hotkey = selected_hotkey                                 # Update self.stort_hotkey
        keyboard.add_hotkey(self.stort_hotkey, self.stortPushButton.click)  # Register new hotkey in keyboard
        self.stortPushButton.setToolTip(self.stort_hotkey)                  # Update tooltip for the button
        self.stortAction.setShortcut(self.stort_hotkey)                     # Update stort QAction
        self._EXISTING_HOTKEYS.update({text: self.stort_hotkey})

    def _update_reset_hotkey(self, text, selected_hotkey):

        keyboard.remove_hotkey(self.reset_hotkey)
        self.reset_hotkey = selected_hotkey
        keyboard.add_hotkey(self.reset_hotkey, self.resetPushButton.click)
        self.resetPushButton.setToolTip(self.reset_hotkey)
        self.resetAction.setShortcut(self.reset_hotkey)
        self._EXISTING_HOTKEYS.update({text: self.reset_hotkey})

    def on_setOpacity_action(self):

        self.set_opacityDialog.show()
        self.set_opacityDialog.move(self.tennyMenu.pos())

    def on_opacitySlider_valueChanged(self):

        self.opacity_value = self.set_opacityDialog.opacitySlider.value() / 100
        self.setWindowOpacity(self.opacity_value)
        self.set_opacityDialog.opacityLabel.setText(f'{self.opacity_value * 100:.0f}')

    def mousePressEvent(self, QMouseEvent):

        if self.set_opacityDialog.isVisible():
            self.set_opacityDialog.close()

    def closeEvent(self, event):

        who_closes = self.sender()
        if isinstance(who_closes, QAction) or self.close_shortcut:
            self._write_settings()
            self.tennySystemTray.hide()
            event.accept()
        else:
            self.hide()
            self.tennySystemTray.showMessage('Tenny', 'You can still found me here :)', QSystemTrayIcon.Information, 3000)
            event.ignore()

    def keyPressEvent(self, event):

        if event.modifiers() & Qt.ControlModifier and event.key() == Qt.Key_Q:
            self.close_shortcut = True
            self.close()

    def _write_settings(self):
        """ Method for saving Tenny's position, size and values. """

        settings = QSettings('GIPSC Core Team', 'Tenny')
        settings.setValue('tenny_geometry', self.saveGeometry())
        settings.setValue('tenny_stort_hotkey', self.stort_hotkey)
        settings.setValue('tenny_reset_hotkey', self.reset_hotkey)
        settings.setValue('tenny_opacity', self.opacity_value)
