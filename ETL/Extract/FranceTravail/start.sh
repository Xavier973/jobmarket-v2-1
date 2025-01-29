#!/bin/bash
Xvfb :99 -screen 0 1920x1080x24 > /dev/null 2>&1 &
cd /app/src
python main.py "$@" 