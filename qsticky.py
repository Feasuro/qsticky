#!/usr/bin/env python

import sys
import os

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QApplication, QPlainTextEdit, QSizeGrip

import resources

DEBUG = os.getenv('DEBUG')

class NoteWindow(QPlainTextEdit):
    """ Note window """
    def __init__(self, *args, **kwargs) -> None:
        """ Initialize the note window. """
        super().__init__(*args, **kwargs)
        self.setup_ui()

    def setup_ui(self) -> None:
        """ Set up the UI for the note window. """
        # Window decorations
        self.setWindowTitle('QSticky')
        self.setWindowIcon(QIcon(':/icons/main'))
        self.setToolTip('Drag with left mouse button.\nRight click to open context menu.')
        self.setToolTipDuration(2000)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool | Qt.WindowType.ToolTip)
        # Resizing
        gripsize = 16
        self.grip = QSizeGrip(self)
        self.grip.resize(gripsize, gripsize)
        # Actions
        icons = {
            'new': QIcon(':/icons/new'),
            'hide': QIcon(':/icons/hide'),
            'preferences': QIcon(':/icons/prop'),
            'delete': QIcon(':/icons/del')
        }
        self.actions = {}
        self.actions['new'] = QAction('&New', self)
        self.actions['new'].setShortcut('Ctrl+N')
        self.actions['hide'] = QAction('&Hide', self)
        self.actions['hide'].setShortcut('Ctrl+H')
        self.actions['preferences'] = QAction('Pre&ferences', self)
        self.actions['preferences'].setShortcut('Ctrl+P')
        self.actions['delete'] = QAction('&Delete', self)
        self.actions['delete'].setShortcut('Ctrl+D')
        for name, action in self.actions.items():
            action.setIcon(icons[name])

    def contextMenuEvent(self, event) -> None:
        """ Add custom actions to default context menu """
        menu = self.createStandardContextMenu()
        top = menu.actions()[0]     # get the first action
        menu.insertActions(top, self.actions.values())
        menu.insertSeparator(top)
        menu.exec(event.globalPos())

    def mousePressEvent(self, event) -> None:
        """ Drag & drop support - save starting position """
        super().mousePressEvent(event)
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragstart = event.pos()

    def mouseMoveEvent(self, event) -> None:
        """ Drag & drop support - move window"""
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._dragstart)

    def resizeEvent(self, event):
        """ Adjust the resizing grip position while resizing. """
        super().resizeEvent(event)
        self.grip.move(self.rect().right() - self.grip.width(),
                       self.rect().bottom() - self.grip.height())


if __name__ == '__main__':
    app = QApplication([])
    note = NoteWindow()
    note.show()
    sys.exit(app.exec())
