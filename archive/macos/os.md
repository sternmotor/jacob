# Brew installation

# homebrew setup

    xcode-select --install # Ok, yes
    cd /usr/local
    sudo mkdir -p bin var/homebrew homebrew etc
    curl -L https://github.com/Homebrew/brew/tarball/master | sudo tar xz --strip 1 -C homebrew
    sudo chown -R $(whoami) var/homebrew homebrew etc
    ln -s /usr/local/homebrew/bin/brew /usr/local/bin/
