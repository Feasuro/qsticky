# <img src="https://github.com/Feasuro/qsticky/blob/main/resources/basket.png" width="64" height="64" /> QSticky
### Sticky notes on your desktop.
* Simple
* Written in Python and Qt6
* Doesn't trash system tray
* Manageable from drop-down menu
## Installation instructions.
### Arch linux and other distros using pacman:
1. Download [PKGBUILD](https://github.com/Feasuro/qsticky/blob/main/PKGBUILD) file
2. Run `makepkg -srci` from the directory where you downloaded PKGBUILD
### Other systems:
Basically just download the application code and install it with pip.
```
git clone https://github.com/Feasuro/qsticky.git
cd qsticky
pip install .
```
Not tested for anything other than linux, but should work on any UNIX and possibly on Windows. Let me know if it's different.
