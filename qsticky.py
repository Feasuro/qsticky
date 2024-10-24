#!/usr/bin/env python

import sys
import os

from PyQt6.QtCore import Qt, QTranslator, QLibraryInfo, QLocale
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QApplication, QPlainTextEdit, QSizeGrip

import resources
from data import SQLiteConnector
from preferences import PreferencesWidget, Font

DEBUG = os.getenv('DEBUG')
db_path = os.path.join(os.path.dirname(__file__), 'resources/qsticky.db')
DBPATH = os.getenv('DBPATH', default=db_path)

class NoteWidget(QPlainTextEdit):
    """ Note window """
    all = {}
    db = None
    style = 'NoteWidget {{background: {}; color: {};}}'

    def __new__(cls, rowid=None, *args, **kwargs):
        """ Create a new instance of NoteWidget or return an existing one. """
        if rowid is None:
            rowid = 0
            while rowid in cls.all:
                rowid += 1
        return cls.all.setdefault(rowid, super().__new__(cls))

    def __init__(self, rowid=None, text='', xpos=10, ypos=10, width=256, height=256,
                 bgcolor='lemonchiffon', font='', fcolor='black', *args, **kwargs) -> None:
        """ Initialize the note window. """
        if DEBUG: print("DEBUG: NoteWidget::__init__\n      ",rowid, text, xpos, ypos,
                        width, height, bgcolor, font, fcolor, *args, **kwargs)
        if rowid is None:
            for id, note in self.all.items():
                if note is self:
                    rowid = id
                    break
        super().__init__(*args, **kwargs)
        self.id = rowid
        self.setGeometry(xpos, ypos, width, height)
        self.setPlainText(text)
        self.preference = (bgcolor, font, fcolor)
        self.apply(*self.preference)
        self.setup_ui()

    def setup_ui(self) -> None:
        """ Set up the UI for the note window. """
        # Window decorations
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
        #self.actions['new'].triggered.connect(NoteApplication.instance().new_note)
        self.actions['hide'].triggered.connect(self.close)
        self.actions['show'].triggered.connect(self.show_all)
        self.actions['preferences'].triggered.connect(self.prefs_dialog)
        self.actions['delete'].triggered.connect(self.delete)

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
        self.db.update(self.as_dict())

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
            'font': self.font().toString(),
            'fcolor': self.palette().color(self.foregroundRole()).name(),
        }

    def apply(self, bgcolor:str, font:str|Font, fcolor:str) -> None:
        """ Apply the selected color and font to the note window. """
        self.setStyleSheet(self.style.format(bgcolor, fcolor))
        if isinstance(font, str):
            font = Font(font)
        self.setFont(font)

    @classmethod
    def apply_to_all(cls, bgcolor:str, font:str|Font, fcolor:str) -> None:
        """ Apply the selected color and font to all notes. """
        if DEBUG: print("DEBUG: NoteWidget::apply_to_all", bgcolor, font, fcolor)
        for note in cls.all.values():
            note.apply(bgcolor, font, fcolor)

    @classmethod
    def show_all(cls) -> None:
        """ Show all hidden note windows. """
        if DEBUG: print("DEBUG: NoteWidget::show_all")
        for note in cls.all.values():
            if not note.isVisible():
                note.show()

    def delete(self) -> None:
        """ Delete note window and database record. """
        if DEBUG: print("DEBUG: NoteWidget::delete", self.id)
        self.close()
        self.db.delete(self.id)
        del self
        NoteApplication.instance().quit_condition()

    def prefs_dialog(self) -> None:
        """ Open the preferences dialog for the specified note. """
        global_pref = self.db.get_preferences()
        if DEBUG: print(f"DEBUG: NoteWidget::prefs_dialog prefs={global_pref}")
        self.pref_widget = PreferencesWidget(*global_pref, self)
        self.pref_widget.save_signal.connect(self.save_preferences)
        self.pref_widget.show()

    def save_preferences(self, preferences:tuple) -> None:
        """ Save chosen preferences in the database.

        Args:
            preferences (tuple): Global preferences chosen in dialog. """
        if DEBUG: print(f"DEBUG: NoteWidget::save_preferences", preferences)
        if not preferences[0]:
            self.db.save(self.as_dict())
            self.preference = (
                self.palette().color(self.backgroundRole()).name(),
                self.font().toString(),
                self.palette().color(self.foregroundRole()).name()
            )
        self.db.save_preferences(preferences)


class NoteApplication(QApplication):
    """ Application class for note management. """
    def __init__(self, *args, **kwargs) -> None:
        """ Initialize the application. """
        super().__init__(*args, **kwargs)
        self.setQuitOnLastWindowClosed(False)
        self.translate()

    def translate(self) -> None:
        """ Load translations of application's strings. """
        if DEBUG: print("DEBUG: NoteApplication::translate")
        path = QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)
        translator = QTranslator(self)
        if translator.load(QLocale(), "qtbase", "_", path):
            self.installTranslator(translator)
        translator = QTranslator(self)
        if translator.load(QLocale(), "qsticky", "_", ":/i18n"):
            self.installTranslator(translator)

    def start(self) -> None:
        """ Show saved notes if found, if not create one. """
        if DEBUG: print("DEBUG: NoteApplication::start")
        if rows := NoteWidget.db.retrieve():
            for row in rows:
                if DEBUG: print("      ", row)
                NoteWidget(*row).show()
        else:
            self.new_note()
        pref = NoteWidget.db.get_preferences()
        if pref[0]:
            NoteWidget.apply_to_all(*pref[1:])

    def new_note(self) -> None:
        """ Create a new empty note window. """
        if DEBUG: print("DEBUG: NoteApplication::new_note")
        rowid = 0
        while rowid in NoteWidget.all:
            rowid += 1
        NoteWidget(rowid).show()
        NoteWidget.db.save(NoteWidget.all[rowid].as_dict())

    def quit_condition(self) -> None:
        """ Check if any note window is visible, exit otherwise. """
        for note in NoteWidget.all.values():
            if note.isVisible():
                break
        else:
            if DEBUG: print("INFO : All notes are hidden. Exiting...")
            self.quit()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    path = QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)
    translator = QTranslator(app)
    if translator.load(QLocale(), "qtbase", "_", path):
        app.installTranslator(translator)
    translator = QTranslator(app)
    if translator.load(QLocale(), "qsticky", "_", ":/i18n"):
        app.installTranslator(translator)

    NoteWidget.db = SQLiteConnector(DBPATH)
    for row in NoteWidget.db.retrieve():
        NoteWidget(*row).show()
    pref = NoteWidget.db.get_preferences()
    if pref[0]:
        NoteWidget.apply_to_all(*pref[1:])

    sys.exit(app.exec())
