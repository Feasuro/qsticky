#!/usr/bin/env python

import sys
import os

from PyQt6.QtCore import Qt, QTranslator, QLibraryInfo, QLocale
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QApplication, QPlainTextEdit, QSizeGrip

import resources

DEBUG = os.getenv('DEBUG')

class NoteWidget(QPlainTextEdit):
    """ Note window """
    all = {}

    def __new__(cls, rowid, *args, **kwargs):
        """ Create a new instance of NoteWidget or return an existing one. """
        if rowid in cls.all:
            return cls.all[rowid]
        self = super().__new__(cls)
        cls.all[rowid] = self
        return self

    def __init__(self, rowid, text='', xpos=10, ypos=10, width=256, height=256, bgcolor='lemonchiffon', font=None, *args, **kwargs) -> None:
        """ Initialize the note window. """
        if DEBUG: print("DEBUG: NoteWidget::__init__\n      ", rowid, text, xpos, ypos, width, height, bgcolor, font, *args, **kwargs)
        super().__init__(*args, **kwargs)
        self.id = rowid
        self.setGeometry(xpos, ypos, width, height)
        self.setPlainText(text)
        self.setup_ui()

    def setup_ui(self) -> None:
        """ Set up the UI for the note window. """
        # Window decorations
        self.setWindowTitle('QSticky')
        self.setWindowIcon(QIcon(':/icons/main'))
        self.setToolTip(self.tr('Drag with left mouse button.\nRight click to open context menu.'))
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
            'show': QIcon(':/icons/show'),
            'preferences': QIcon(':/icons/prop'),
            'delete': QIcon(':/icons/del')
        }
        self.actions = {}
        self.actions['new'] = QAction(self.tr('&New'), self)
        self.actions['new'].setShortcut('Ctrl+N')
        self.actions['hide'] = QAction(self.tr('&Hide'), self)
        self.actions['hide'].setShortcut('Ctrl+H')
        self.actions['show'] = QAction(self.tr('Sho&w all'), self)
        self.actions['show'].setShortcut('Ctrl+W')
        self.actions['preferences'] = QAction(self.tr('Pre&ferences'), self)
        self.actions['preferences'].setShortcut('Ctrl+P')
        self.actions['delete'] = QAction(self.tr('&Delete'), self)
        self.actions['delete'].setShortcut('Ctrl+D')
        for name, action in self.actions.items():
            action.setIcon(icons[name])

    def contextMenuEvent(self, event) -> None:
        """ Add custom actions to default context menu. """
        menu = self.createStandardContextMenu()
        top = menu.actions()[0]     # get the first action
        menu.insertActions(top, self.actions.values())
        menu.insertSeparator(top)
        menu.exec(event.globalPos())

    def mousePressEvent(self, event) -> None:
        """ Drag & drop support - save starting position. """
        super().mousePressEvent(event)
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragstart = event.pos()

    def mouseMoveEvent(self, event) -> None:
        """ Drag & drop support - move window. """
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._dragstart)

    def resizeEvent(self, event):
        """ Adjust the resizing grip position while resizing. """
        super().resizeEvent(event)
        self.grip.move(self.rect().right() - self.grip.width(),
                       self.rect().bottom() - self.grip.height())


if __name__ == '__main__':
    app = QApplication([])

    path = QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)
    translator = QTranslator(app)
    if translator.load(QLocale(), "qtbase", "_", path):
        app.installTranslator(translator)
    if translator.load(QLocale(), "qsticky", "_", ":/i18n"):
        app.installTranslator(translator)

    note = NoteWidget(0)
    note.show()
    sys.exit(app.exec())
