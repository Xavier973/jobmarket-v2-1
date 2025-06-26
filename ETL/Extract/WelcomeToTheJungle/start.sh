#!/bin/bash

# Script de démarrage pour Welcome To The Jungle scraper

echo "Starting Welcome To The Jungle scraper..."

# Démarrer Xvfb en arrière-plan avec une résolution plus grande
Xvfb :99 -screen 0 1920x1080x24 -ac +extension GLX +render -noreset > /dev/null 2>&1 &

# Attendre que Xvfb soit prêt
sleep 3

# Vérifier que Xvfb fonctionne
if ! xdpyinfo -display :99 >/dev/null 2>&1; then
    echo "Xvfb failed to start, trying alternative configuration..."
    Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &
    sleep 2
fi

# Exécuter le script principal
python main.py

echo "Welcome To The Jungle scraper finished." 