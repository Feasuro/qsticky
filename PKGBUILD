# Maintainer: Feasuro <feasuro at pm dot me>
pkgname=qsticky
pkgver=1.2
pkgrel=1
pkgdesc='Sticky desktop notes application.'
arch=(any)
url='https://github.com/Feasuro/qsticky'
license=('GPL-3.0-or-later')
depends=('python-pyqt6')
makedepends=('git' 'python-setuptools' 'python-build' 'python-installer')
source=("${pkgname}::git+${url}.git")
sha256sums=('SKIP')

pkgver() {
  cd "${pkgname}"
  ( set -o pipefail
    git describe --tags 2>/dev/null | sed 's/^v//;s/-/.r/;s/-/./' ||
    printf "0.r%s.%s" "$(git rev-list --count HEAD)" "$(git rev-parse --short=7 HEAD)"
  )
}

build() {
  cd "${srcdir}/${pkgname}"
  python -m build --wheel --no-isolation
}

package() {
  cd "${srcdir}/${pkgname}"
  python -m installer --destdir="${pkgdir}" dist/*.whl
}
