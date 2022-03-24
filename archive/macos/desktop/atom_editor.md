# Mac OS Einrichtung - Atom Editor

## Installation

* download atom, copy to Programs
* Productivity plugins:
    * Settings
        * Install
    		* language-markdown
        	* markdown-preview-extended
            * image-view
            * markdown-image-paste
            * pdf-view
            * teletype
* my plugins:
    * Settings
        * Install
            * ex-mode
            * hydrogen
            ```
            pip3 install ipykernel
            python3 -m ipykernel install --user    
            ```
                * options: output in dock
            * atom-keyboard-macros-vim
            * atom-clock
            * convert-to-utf8
            * ex-mode-sort
            * remote-edit
            * sync-settings
            * vim-mode-plus
            * vim-mode-zz
            * vim-surround

* Markdown Preview PDF export:
    * via npm:
        ```bash
        sudo npm install -g phantomjs-prebuilt
        ```
    * manually:
        * [download PhantomJS](http://phantomjs.org/download.html) and
        * copy to `/usr/local/bin/`:
            ```bash
            sudo cp ~/Downloads/phantomjs-*-macosx/bin/phantomjs /usr/local/bin
            ```
    * test: `phantomjs` must be executable
    * configure
        * edit `~/.mume/style.less`
            ```
            .markdown-preview.markdown-preview {
                @media print {
                    font-size: 8pt;
                }
            }
            ```

## Latex PDF export
Edit markdown files, export to pdflatex via `markdown-preview-enhanced`:
* install pandoc adn pdflatex in macos
```bash
brew install pandoc
brew cask install basictex
ln -s /Library/TeX/texbin/pdflatex /usr/local/bin/
```

See https://kofler.info/atom-als-markdownpandoc-editor/
Usage: Start md document like


check out: pandoc-convert - works good with standard markdown ... todo: format
code blocks and hyperlinks better,

```
---
title: "Habits"
author: John Doe
date: March 22, 2005
output: pdf_document
---
```

## Configuration
sync- settings plugin:
* see [Instructions](https://atom.io/packages/sync-settings)
* Github Token: `64db9efd0ac6d52dd68a4677ce05a2aa8098e01b`
* Gist ID: `695b86c22458b37f221e2e01057faa8f`
* Usage: Shift-Command-P sync-settings backup|restore

Settings
* Core
    * Enable "open empty editor on start"
* Editor
    * Enable Softwrap
* Packages
  * spell-check > Use Locales > de-DE
   * spell-check > Activate Add Known Words
    * Autocomplete Plus
        * Keymap for confirming a Suggestion "Tab always, enter when ..."
* My Settings
    * VIM Escape mode via `jk` (`ESC` is a little far from home position): edit `~/.atom/keymap.cson`:
        ```yaml
        'atom-text-editor.vim-mode-plus.insert-mode':
          'j k': 'vim-mode-plus:activate-normal-mode'
        ```
    * Editor
        * Font family "menlo"
    * Packages
        * atom-clock
            * Time format `dd. DD. MMM HH:mm (W)` (with calendar week)
            * Locale `de`
* At first start, change to `welcome.md` pane and uncheck "Show Welcome Guide ..."
* Enable "autosave" plugin in settings - stores "untitled" tabs etc.
* Switch language for spell checker
* Fix Tab switching to work with Control-Tab and Shift-Control Ta
    * Go the Atom menu > Open Your Keymap and add:
    ```yaml
    'body':
      'ctrl-tab': 'pane:show-next-item'
      'ctrl-shift-tab': 'pane:show-previous-item'
    ```

## Usage
See [Sitepoint blog]( https://www.sitepoint.com/12-favorite-atom-tips-and-shortcuts-to-improve-your-workflow/)

* Command palette: Shift-Command-P - run every command available in atom
* Work on current document, hide everything else Command-ENTER
* Multiple cursors: Command+Click
* Preview Toogle: Shift-Control-M
* Open Project folder: Control-Shift-A
* edit from command line: atom FILE1 FILE2 DIR1 DIR2
* markdown preview:
    * activate like Shift-Control-M for files ending like `*.md`
    * in preview pane:
		* Table of contents: ESC
        * PDF export:
    		* Right click
    			* PhantomJS
    				* PDF
* sort text: visual mode, mark, Control-s, type "sort"
* disable core packages (mostly redundant to vim functions):
    * about
    * autocomplete-atom-api
    * autocomplete-css
    * autocomplete-html
    * autoflow
    * background-tips
    * bookmarks
    * bracket-matcher
    * command-palette
    * deprecation-cop
    * dev-live-reload
    * encoding-selector
    * execution-reporting
    * git-diff
    * github
    * go-to-line
    * grammar-selector
    * language- c coffee-script css csharp git go java java-script less mustache objective-c ruby ruby-on-rails sass toml typescript
    * markdown-preview
    * metrics
    * open-on-github
    * package-generator
    * styleguide
    * welcome
