arch linux 

install package from AUR PKGBUILD file
```
mkdir build
cd build
git clone https://aur.archlinux.org/php-redis.git
pacman -S kernel26-headers file base-devel abs
makepkg -Acs
sudo pacman -U *.pkg.tar.xz
```
