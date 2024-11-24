""" Defines dialog widget that presents the user with controls for selecting colors and font. """
import logging

from PyQt6.QtCore import pyqtSignal as Signal
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QGroupBox, QDialogButtonBox,
                             QPushButton, QColorDialog, QFontDialog)

logger = logging.getLogger(__name__)

class Font(QFont):
    def __init__(self, string:str, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if string:
            self.fromString(string)


class ColorButton(QPushButton):
    """ Color selection button. """
    style = 'background: {};'

    def __init__(self, color:str, *args, **kwargs) -> None:
        """ Initialize the color selection button.

        Args:
            color (str): The current background color. In '#RRGGBB format. """
        super().__init__(*args, **kwargs)
        self.color = color
        self.setStyleSheet(self.style.format(self.color))
        self.clicked.connect(self.pick_color)

    def pick_color(self) -> str:
        """ Dialog for color selection. """
        self.color = QColorDialog(self).getColor().name()
        logger.debug(f"ColorButton::pick_color; {self.color}, {type(self.color)}")
        self.setStyleSheet(self.style.format(self.color))
        return self.color


class FontButton(QPushButton):
    """ Font selection button. """
    style = 'background: white;'

    def __init__(self, font:QFont, *args, **kwargs) -> None:
        """ Initialize the font selection button.

        Args:
            font (QFont): The current font. """
        super().__init__(*args, **kwargs)
        self.setFont(font)
        self.setStyleSheet(self.style)
        self.setText(f"{font.family()} {font.styleName()} {font.pointSize()}")
        self.clicked.connect(self.pick_font)

    def pick_font(self) -> QFont:
        """ Dialog for font selection. """
        font, _ = QFontDialog(self).getFont()
        logger.debug(f"FontButton::pick_font, {font}")
        self.setFont(font)
        self.setText(f"{font.family()} {font.styleName()} {font.pointSize()}")
        return font


class FontColorButton(ColorButton):
    """ Color selection button. """
    style = 'color: {}; font-weight: bold;'

    def __init__(self, color:str, *args, **kwargs) -> None:
        """ Initialize the font color selection button.

        Args:
            color (str): The current font color. In '#RRGGBB format. """
        super().__init__(color, *args, **kwargs)
        self.setText(self.tr('lorem ipsum'))


class PreferencesWidget(QDialog):
    """ Widget for selection of the app preferences. """
    save_signal = Signal(dict)
    
    def __init__(self, global_preference:tuple, *args, **kwargs) -> None:
        """ Initialize the preferences dialog.
        
        Args:
            global_preference (tuple): Tuple of checked, bgcolor, font, fcolor. """
        logger.debug(f'PreferencesWidget::__init__\n      {global_preference}, {args}, {kwargs}')
        super().__init__(*args, **kwargs)
        if (parent := self.parent()) is None:
            raise RuntimeWarning("PreferencesWidget needs a parent NoteWidget")
        self.checked = bool(global_preference[0])
        self.global_check = QGroupBox(self.tr('Global settings'))
        self.btn_g_bgcolor = ColorButton(global_preference[1])
        self.btn_g_font = FontButton(Font(global_preference[2]))
        self.btn_g_fcolor = FontColorButton(global_preference[3])
        self.btn_bgcolor = ColorButton(parent.preference[0])
        self.btn_font = FontButton(Font(parent.preference[1]))
        self.btn_fcolor = FontColorButton(parent.preference[2])
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
        grouplayout = QFormLayout(self.global_check)
        grouplayout.addRow(self.tr("Background color:"), self.btn_g_bgcolor)
        grouplayout.addRow(self.tr("Font:"), self.btn_g_font)
        grouplayout.addRow(self.tr("Font color:"), self.btn_g_fcolor)
        group = QGroupBox(self.tr("Chosen settings"))
        grouplayout = QFormLayout(group)
        grouplayout.addRow(self.tr("Background color:"), self.btn_bgcolor)
        grouplayout.addRow(self.tr("Font:"), self.btn_font)
        grouplayout.addRow(self.tr("Font color:"), self.btn_fcolor)
        layout = QVBoxLayout(self)
        layout.addWidget(self.global_check)
        layout.addWidget(group)     
        layout.addWidget(btns)
        # Signals
        group.setDisabled(self.checked)
        self.global_check.setCheckable(True)
        self.global_check.setChecked(self.checked)
        self.global_check.toggled.connect(group.setDisabled)

    def apply(self) -> None:
        """ Apply selection. """
        logger.info("PreferencesWidget::Applying settings")
        if self.global_check.isChecked():
            self.parent().apply_to_all(
                self.btn_g_bgcolor.color,
                self.btn_g_font.font(),
                self.btn_g_fcolor.color
            )
        else:
            self.parent().apply(self.btn_bgcolor.color, self.btn_font.font(), self.btn_fcolor.color)

    def save(self) -> None:
        """ Save selection. """
        self.apply()
        self.save_signal.emit({
            'checked': int(self.global_check.isChecked()),
            'bgcolor': self.btn_g_bgcolor.color,
            'font': self.btn_g_font.font().toString(),
            'fcolor': self.btn_g_fcolor.color
            })
        self.close()
