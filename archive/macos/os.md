Homebrew 
========

Run this as admin user, otherwise a lot of things won't work

    xcode-select --install # Ok, yes
    sudo mkdir -p /usr/local/var/homebrew /usr/local/homebrew /usr/local/etc
    curl -L https://github.com/Homebrew/brew/tarball/master | sudo tar xz --strip 1 -C /usr/local/homebrew
    sudo chown -R $(whoami) /usr/local/etc/bash_completion.d /usr/local/lib/pkgconfig /usr/local/share/aclocal /usr/local/share/doc /usr/local/share/info /usr/local/share/locale /usr/local/share/man /usr/local/share/man/man1 /usr/local/share/man/man3 /usr/local/share/man/man5 /usr/local/share/man/man7 /usr/local/share/man/man8 /usr/local/share/zsh /usr/local/share/zsh/site-functions /usr/local/var/log /usr/local/Cellar/
    sudo ln -s /usr/local/Homebrew/bin/brew /usr/bin/
    sudo chown -R $(whoami)  /usr/local/Cellar

Updateing

    brew update-reset
    /usr/local/bin/brew upgrade

Maintenance

remove deprecated taps

    brew untap homebrew/dupes
    brew untap homebrew/python
    brew untap homebrew/versions
    brew update-reset
