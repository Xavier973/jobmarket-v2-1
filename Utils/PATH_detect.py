import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))  # Chemin du script actuel
BASE_PATH = os.path.dirname(os.path.dirname(SCRIPT_DIR))  # Remonte de 2 niveaux
DATA_FOLDER = os.path.join(BASE_PATH, "data", "transformed", "francetravail")