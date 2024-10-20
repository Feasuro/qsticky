#!/usr/bin/env python

import sys
import os

from PyQt6.QtCore import Qt, QTranslator, QLibraryInfo, QLocale
from PyQt6.QtGui import QAction, QIcon, QFont
from PyQt6.QtWidgets import QApplication, QPlainTextEdit, QSizeGrip

import resources
from data import SQLiteConnector

DEBUG = os.getenv('DEBUG')
DBPATH = os.getenv('DBPATH', default='resources/qsticky.db')

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
        self.setStyleSheet('NoteWidget {background-color:' + bgcolor + ';}')
        _font = QFont()
        if _font.fromString(font):
            self.setFont(_font)
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
        # Signals
        self.actions['new'].triggered.connect(NoteApplication.instance().new_note)
        self.actions['hide'].triggered.connect(self.hide)
        self.actions['delete'].triggered.connect(lambda: NoteApplication.instance().delete_note(self.id))

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

    def resizeEvent(self, event) -> None:
        """ Adjust the resizing grip position while resizing. """
        super().resizeEvent(event)
        self.grip.move(self.rect().right() - self.grip.width(),
                       self.rect().bottom() - self.grip.height())

    def focusOutEvent(self, event) -> None:
        """ Save the note text and position when focus is lost. """
        super().focusOutEvent(event)
        NoteApplication.instance().db.update(self.as_dict())

    def as_dict(self) -> dict:
        """ Convert the note window to a dictionary. """
        return {
            'id': self.id,
            'text': self.toPlainText(),
            'xpos': self.x(),
            'ypos': self.y(),
            'width': self.width(),
            'height': self.height(),
            'bgcolor': self.palette().color(self.backgroundRole()).name(),
            'font': self.font().toString()
        }


class NoteApplication(QApplication):
    """ Application class for note management. """
    def __init__(self, *args, **kwargs) -> None:
        """ Initialize the application. """
        super().__init__(*args, **kwargs)
        self.db = SQLiteConnector(DBPATH)

    def start(self) -> None:
        """ Show saved notes if found, if not create one. """
        if DEBUG: print("DEBUG: NoteApplication::start")
        if rows := self.db.retrieve():
            for row in rows:
                if DEBUG: print("      ", row)
                NoteWidget(*row).show()
        else:
            self.new_note()

    def new_note(self) -> None:
        """ Create a new empty note window. """
        if DEBUG: print("DEBUG: NoteApplication::new_note")
        rowid = 0
        while rowid in NoteWidget.all:
            rowid += 1
        NoteWidget(rowid).show()
        self.db.save(NoteWidget.all[rowid].as_dict())

    def delete_note(self, rowid) -> None:
        """ Delete note window and database record. """
        if DEBUG: print("DEBUG: NoteApplication::delete_note", rowid)
        if rowid in NoteWidget.all:
            NoteWidget.all[rowid].close()
            self.db.delete(rowid)
            del NoteWidget.all[rowid]


if __name__ == '__main__':
    app = NoteApplication(sys.argv)

    path = QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)
    translator = QTranslator(app)
    if translator.load(QLocale(), "qtbase", "_", path):
        app.installTranslator(translator)
    if translator.load(QLocale(), "qsticky", "_", ":/i18n"):
        app.installTranslator(translator)

    app.start()
    sys.exit(app.exec())
