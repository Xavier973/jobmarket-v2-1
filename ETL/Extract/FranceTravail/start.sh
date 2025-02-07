#!/bin/bash
Xvfb :99 -screen 0 1920x1080x24 > /dev/null 2>&1 &
cd src
python main.py "$@" 