#!/usr/bin/env python

import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QApplication, QTextEdit, QPushButton, QGridLayout

import resources


class NoteWindow(QTextEdit):
    """ Note window """
    
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        #self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        self.icons = {}
        self.icons['new'] = QIcon(':/icons/new')
        self.icons['hide'] = QIcon(':/icons/hide')
        self.icons['properties'] = QIcon(':/icons/prop')
        self.icons['delete'] = QIcon(':/icons/del')
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


if __name__ == '__main__':
    app = QApplication([])
    note = NoteWindow()
    note.show()
    sys.exit(app.exec())
