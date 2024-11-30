# Maintainer: Feasuro <feasuro at pm dot me>
pkgname=qsticky
pkgver=1.3
pkgrel=1
pkgdesc='Sticky desktop notes application.'
arch=(any)
url="https://github.com/Feasuro/${pkgname}"
license=('GPL-3.0-or-later')
depends=('python-pyqt6')
optdepends=(
  'python-psycopg2: PostgreSQL database support'
  'python-mysqlclient: MySQL database support'
  )
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

prepare() {
  cd "${srcdir}/${pkgname}"
  sed -i "3s/^\(Version=\).*/\1${pkgver}/" "${pkgname}.desktop"
}

build() {
  cd "${srcdir}/${pkgname}"
  python -m build --wheel --no-isolation
}

package() {
  cd "${srcdir}/${pkgname}"
  python -m installer --destdir="${pkgdir}" dist/*.whl
  install -Dm0644 "resources/basket.png" "${pkgdir}/usr/share/icons/hicolor/128x128/apps/${pkgname}.png"
  install -Dm0644 -t "${pkgdir}/usr/share/applications/" "${pkgname}.desktop"
}
