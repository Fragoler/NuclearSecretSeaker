#!/bin/bash

pyinstaller --onefile \
            --add-data "pdf-generator/background.png:." \
            --name nuclearss-pdf \
            pdf-generator/main.py
            
pyinstaller --onefile \
            --add-data "seaker/patterns.json:." \
            --name nuclearss-seaker \
            seaker/src/main.py
            
pyinstaller --onefile \
            --name nuclearss \
            tui/src/main.py
