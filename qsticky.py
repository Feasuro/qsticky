#!/usr/bin/env python

import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QApplication, QTextEdit

import resources


class NoteWindow(QTextEdit):
    """ Note window """
    
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        # Window decorations
        self.setWindowTitle('QSticky')
        self.setWindowIcon(QIcon(':/icons/main'))
        self.setToolTip('''Drag with left mouse button.\nRight click to open context menu.''')
        self.setToolTipDuration(2000)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        # Icons
        self.icons = {}
        self.icons['new'] = QIcon(':/icons/new')
        self.icons['hide'] = QIcon(':/icons/hide')
        self.icons['properties'] = QIcon(':/icons/prop')
        self.icons['delete'] = QIcon(':/icons/del')
        # Actions
        self.actions = {}
        self.actions['new'] = QAction('&New', self)
        self.actions['new'].setShortcut('Ctrl+N')
        self.actions['hide'] = QAction('&Hide', self)
        self.actions['hide'].setShortcut('Ctrl+H')
        self.actions['properties'] = QAction('Pr&operties', self)
        self.actions['properties'].setShortcut('Ctrl+O')
        self.actions['delete'] = QAction('&Delete', self)
        self.actions['delete'].setShortcut('Ctrl+D')
        for key in self.actions:
            self.actions[key].setIcon(self.icons[key])

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
            self._dragStart = event.pos()

    def mouseMoveEvent(self, event) -> None:
        """ Drag & drop support - move window"""
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._dragStart)


if __name__ == '__main__':
    app = QApplication([])
    note = NoteWindow()
    note.show()
    sys.exit(app.exec())
