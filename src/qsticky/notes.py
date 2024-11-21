""" Define the widget class that displays sticky notes. """
from PyQt6.QtCore import Qt, QTranslator, QLibraryInfo, QLocale, qDebug, qInfo
from PyQt6.QtCore import pyqtSignal as Signal
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QApplication, QPlainTextEdit, QSizeGrip

import qsticky.resources
from qsticky import __version__
from qsticky.data import NoStorage
from qsticky.preferences import PreferencesWidget, Font

DEFAULTS = ('', 10, 10, 256, 256, 'lemonchiffon', '', 'black')

class NoteWidget(QPlainTextEdit):
    """ Note Widget class representing a sticky note.

    Class Attributes:
        all (dict): Dictionary mapping ids to notes
        db (data.StorageConnector): Storage tasks helper object.
        style (string): QSS style sheet string for widgets. """
    all = {}
    db = NoStorage()
    style = 'NoteWidget {{background: {}; color: {};}}'
    quit_signal = Signal()

    def __new__(cls, row:tuple, *args, **kwargs):
        """ Create a new instance of NoteWidget or return an existing one. """
        return cls.all.setdefault(row[0], super().__new__(cls))

    def __init__(self, row:tuple, *args, **kwargs) -> None:
        """ Initialize the note window.

        Args:
            row (tuple): Tuple of id, text, xpos, ypos, width, height, bgcolor, font,
                fcolor. A database record of note. """
        qDebug(f"DEBUG: NoteWidget::__init__\n      {row}, {args}, {kwargs}")
        self.id = row[0]
        super().__init__(row[1], *args, **kwargs)
        self.setGeometry(*row[2:6])
        self.preference = row[6:]
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
        self.actions['new'].triggered.connect(self.new_note)
        self.actions['hide'].triggered.connect(lambda: self.close() and self.quit_signal.emit())
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
        qDebug(f"DEBUG: NoteWidget::apply_to_all {bgcolor}, {font}, {fcolor}")
        for note in cls.all.values():
            note.apply(bgcolor, font, fcolor)

    @classmethod
    def show_all(cls) -> None:
        """ Show all hidden note windows. """
        qDebug("DEBUG: NoteWidget::show_all")
        for note in cls.all.values():
            if not note.isVisible():
                note.show()

    @classmethod
    def new_note(cls) -> 'NoteWidget':
        """ Create a new empty note window. """
        qDebug("DEBUG: NoteWidget::new_note")
        new_rowid = 1 + max(cls.all, default=0)
        ## Can manipulate new row-id calculation here, like:
        #new_rowid = 0
        #while new_rowid in cls.all:
        #    new_rowid += 1
        note = cls((new_rowid, *DEFAULTS))
        last_rowid = cls.db.save(note.as_dict())
        if note.id != last_rowid:
            raise RuntimeWarning(f"WARNING: id mismatch: {note.id} != {last_rowid}")
        if (pref := cls.db.get_preferences()) and pref[0]:
            note.apply(*pref[1:])
        note.show()
        return note

    def delete(self) -> None:
        """ Delete note window and database record. """
        qDebug(f"DEBUG: NoteWidget::delete; {self.id}")
        self.all.pop(self.id).close()
        self.db.delete(self.id)
        self.quit_signal.emit()

    def prefs_dialog(self) -> None:
        """ Open the preferences dialog for the specified note. """
        if not (global_pref := self.db.get_preferences()):
            global_pref = (1, *DEFAULTS[5:])
        qDebug(f"DEBUG: NoteWidget::prefs_dialog; {global_pref}")
        self.pref_widget = PreferencesWidget(global_pref, self)
        self.pref_widget.save_signal.connect(self.save_preferences)
        self.pref_widget.show()

    def save_preferences(self, preferences:dict) -> None:
        """ Save chosen preferences in the database.

        Args:
            preferences (dict): Global preferences chosen in dialog. """
        qDebug(f"DEBUG: NoteWidget::save_preferences; {preferences}")
        if not preferences['checked']: # Global not chosen
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
        self.setApplicationName('Qsticky')
        self.setApplicationVersion(qsticky.__version__)
        self.setQuitOnLastWindowClosed(False)
        self.translation()

    def translation(self) -> None:
        """ Load translations of application's strings. """
        qDebug("DEBUG: NoteApplication::translation")
        path = QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)
        translator = QTranslator(self)
        if translator.load(QLocale(), "qtbase", "_", path):
            self.installTranslator(translator)
        translator = QTranslator(self)
        if translator.load(QLocale(), "qsticky", "_", ":/i18n"):
            self.installTranslator(translator)

    def start(self) -> None:
        """ Show saved notes if found, if not create one. """
        qDebug("DEBUG: NoteApplication::start")
        if rows := NoteWidget.db.retrieve():
            for row in rows:
                qDebug(f"      {row}")
                note = NoteWidget(row)
                note.quit_signal.connect(self.quit_condition)
                note.show()
            # Check for global preference state
            if (pref := NoteWidget.db.get_preferences()) and pref[0]:
                NoteWidget.apply_to_all(*pref[1:])
        else:
            note = NoteWidget.new_note()
            note.quit_signal.connect(self.quit_condition)

    def quit_condition(self) -> None:
        """ Check if any note window is visible, exit otherwise. """
        for note in NoteWidget.all.values():
            if note.isVisible():
                break
        else:
            qInfo("INFO : All notes are hidden. Exiting...")
            self.quit()
