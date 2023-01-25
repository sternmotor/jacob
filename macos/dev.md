# Development under macOS


## High sierra

homebrew + Python3

    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"
    sudo chown -R $(whoami) \
        /usr/local/Cellar \
        /usr/local/Cellar/ca-certificates \
        /usr/local/etc/openssl* \
    ;
    python3 -m pip install --upgrade pip
    brew install python3
    sudo chown -R $(whoami) \
        /usr/local/Frameworks/Python.framework \
    ;
    brew link --overwrite python3


Jupyter python sketchbook

    brew install jupyter
    brew link --overwrite jupyter
    jupyter notebook





