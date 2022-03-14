from os.path import abspath, dirname, join
from pathlib import Path

IMAGE_DIR = join(dirname(abspath(__file__)), 'static', 'images')
DPCREATOR_LOGO_PATH = Path(join(IMAGE_DIR, 'dpcreator_logo.png'))