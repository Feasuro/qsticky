import os

from PyQt6.QtCore import pyqtSignal as Signal
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QGroupBox, QDialogButtonBox,
                             QPushButton, QCheckBox, QColorDialog, QFontDialog)

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
    save_signal = Signal(tuple)
    
    def __init__(self, checked:int, global_color:str, global_font:str, *args, **kwargs) -> None:
        """ Initialize the preferences dialog. """
        if DEBUG: print(f'DEBUG: PreferencesWidget::__init__ checked={checked}; color={global_color}; font={global_font}; args={args}; kwargs={kwargs}')
        super().__init__(*args, **kwargs)
        if (_parent := self.parent()) is None:
            raise RuntimeError("PreferencesWidget needs a parent NoteWidget")
        self.global_check = QCheckBox(self.tr('Use global settings.'))
        self.global_check.setChecked(bool(checked))
        self.btn_gcolor = ColorButton(global_color)
        _font = QFont()
        _font.fromString(global_font)
        self.btn_gfont = FontButton(_font)
        _color = _parent.palette().color(self.backgroundRole()).name()
        self.btn_color = ColorButton(_color)
        self.btn_font = FontButton(_parent.font())
        self.ui_setup()

    def ui_setup(self) -> None:
        """ Set up the UI for the preferences dialog. """
        self.setWindowTitle(self.tr('QSticky - preferences'))
        self.setWindowIcon(QIcon(':/icons/main'))
        # Buttons
        btns = QDialogButtonBox( QDialogButtonBox.StandardButton.Apply |
                                  QDialogButtonBox.StandardButton.Cancel |
                                  QDialogButtonBox.StandardButton.Save)
        btns.accepted.connect(self.save)
        btns.rejected.connect(self.close)
        btns.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(self.apply)
        # Layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.global_check)
        group = QGroupBox(self.tr("Global settings"))
        grouplayout = QFormLayout(group)
        grouplayout.addRow(self.tr("Background:"), self.btn_gcolor)
        grouplayout.addRow(self.tr("Font:"), self.btn_gfont)
        layout.addWidget(group)
        group = QGroupBox(self.tr("Chosen settings"))
        grouplayout = QFormLayout(group)
        grouplayout.addRow(self.tr("Background:"), self.btn_color)
        grouplayout.addRow(self.tr("Font:"), self.btn_font)   
        layout.addWidget(group)     
        layout.addWidget(btns)

    def apply(self) -> None:
        """ Apply selection. """
        if DEBUG: print("DEBUG: PreferencesWidget::apply", (self.global_check.isChecked(), self.btn_color.color, self.btn_font.font()))
        if self.global_check.isChecked():
            self.parent().apply_to_all(self.btn_gcolor.color, self.btn_gfont.font())
        else:
            self.parent().apply(self.btn_color.color, self.btn_font.font())

    def save(self) -> None:
        """ Save selection. """
        self.apply()
        self.save_signal.emit((int(self.global_check.isChecked()), self.btn_gcolor.color, self.btn_gfont.font().toString()))
        self.close()