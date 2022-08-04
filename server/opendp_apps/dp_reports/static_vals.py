from decimal import Decimal
from os.path import abspath, dirname, join
from pathlib import Path

IMAGE_DIR = join(dirname(abspath(__file__)), 'static', 'images')
DPCREATOR_LOGO_PATH = Path(join(IMAGE_DIR, 'dpcreator_logo.png'))

PYPI_OPENDP_URL = 'https://pypi.org/project/opendp/'

TOC_L1_LINK_OFFSET = Decimal(40)
TOC_L2_LINK_OFFSET = Decimal(60)
