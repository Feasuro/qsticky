import os

from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtWidgets import (QDialog, QFormLayout, QDialogButtonBox, QPushButton, QColorDialog,
                             QFontDialog)

DEBUG = os.getenv('DEBUG')

class ColorButton(QPushButton):
    """ Color selection button. """
    def __init__(self, color:str, *args, **kwargs) -> None:
        """ Initialize the color selection button.

        Args:
            color (str): The current background color. In '#RRGGBB format. """
        super().__init__(*args, **kwargs)
        self.color = color
        self.setStyleSheet(f'background-color: {self.color};')
        self.clicked.connect(self.pick_color)

    def pick_color(self) -> str:
        """ Dialog for color selection. """
        self.color = QColorDialog(self).getColor().name()
        if DEBUG: print("DEBUG: ColorButton::pick_color", self.color, type(self.color))
        self.setStyleSheet(f'background-color: {self.color};')
        return self.color


class FontButton(QPushButton):
    """ Font selection button. """
    def __init__(self, font:QFont, *args, **kwargs) -> None:
        """ Initialize the font selection button.

        Args:
            font (QFont): The current font. """
        super().__init__(*args, **kwargs)
        self.setFont(font)
        self.setStyleSheet('background-color: white;')
        self.setText(f"{font.family()} {font.styleName()} {font.pointSize()}")
        self.clicked.connect(self.pick_font)

    def pick_font(self) -> QFont:
        """ Dialog for font selection. """
        _font, _ = QFontDialog(self).getFont()
        if DEBUG: print("DEBUG: FontButton::pick_font", _font)
        self.setFont(_font)
        self.setText(f"{_font.family()} {_font.styleName()} {_font.pointSize()}")
        return _font


class PreferencesWidget(QDialog):
    """ Widget for selection of the app preferences. """
    def __init__(self, *args, **kwargs) -> None:
        """ Initialize the preferences dialog. """
        super().__init__(*args, **kwargs)
        if self.parent() is None:
            raise RuntimeError("PreferencesWidget needs a parent NoteWidget")
        _color = self.parent().palette().color(self.backgroundRole()).name()
        self.btn_color = ColorButton(_color)
        self.btn_font = FontButton(self.parent().font())
        self.ui_setup()

    def ui_setup(self) -> None:
        """ Set up the UI for the preferences dialog. """
        self.setWindowTitle(self.tr('QSticky - preferences'))
        self.setWindowIcon(QIcon(':/icons/main'))
        # Buttons
        btns = QDialogButtonBox( QDialogButtonBox.StandardButton.Apply |
                                  QDialogButtonBox.StandardButton.Cancel |
                                  QDialogButtonBox.StandardButton.Save)
        btns.accepted.connect(lambda: self.done(self.apply()))
        btns.rejected.connect(self.close)
        btns.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(self.apply)
        # Layout
        layout = QFormLayout(self)
        layout.addRow(self.tr("Background:"), self.btn_color)
        layout.addRow(self.tr("Font:"), self.btn_font)
        layout.addRow(btns)

    def apply(self) -> int:
        """ Apply selection.

        Returns:
         int: result code, to emit with finish signal. """
        if DEBUG: print("DEBUG: PreferencesWidget::apply", self.btn_color.color, self.btn_font.font())
        self.parent().apply(self.btn_color.color, self.btn_font.font())
        return 1