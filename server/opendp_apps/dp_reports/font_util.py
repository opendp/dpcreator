"""
Methods for retrieving custom fonts
"""
from decimal import Decimal
from pathlib import Path
from os.path import abspath, dirname, join
from borb.pdf.canvas.font.simple_font.true_type_font import TrueTypeFont
from borb.pdf.canvas.font.font import Font

FONT_DIR = join(dirname(abspath(__file__)), 'fonts')
FONT_DIR_OPEN_SANS = join(FONT_DIR, 'Open_Sans', 'static', 'OpenSans')

OPEN_SANS_LIGHT = 'OPEN_SANS_LIGHT'
OPEN_SANS_REGULAR = 'OPEN_SANS_LIGHT'
OPEN_SANS_SEMI_BOLD = 'OPEN_SEMI_BOLD'
OPEN_SANS_BOLD = 'OPEN_SANS_BOLD'
OPEN_SANS_ITALIC = 'OPEN_SANS_ITALIC'
OPEN_SANS_BOLD_ITALIC = 'OPEN_SANS_BOLD_ITALIC'

FONT_INFO = {
    OPEN_SANS_LIGHT: join(FONT_DIR_OPEN_SANS, 'OpenSans-Light.ttf'),
    OPEN_SANS_REGULAR: join(FONT_DIR_OPEN_SANS, 'OpenSans-Regular.ttf'),
    OPEN_SANS_BOLD: join(FONT_DIR_OPEN_SANS, 'OpenSans-Bold.ttf'),
    OPEN_SANS_SEMI_BOLD: join(FONT_DIR_OPEN_SANS, 'OpenSans-SemiBold.ttf'),
    OPEN_SANS_ITALIC: join(FONT_DIR_OPEN_SANS, 'OpenSans-Italic.ttf'),
    OPEN_SANS_BOLD_ITALIC: join(FONT_DIR_OPEN_SANS, 'OpenSans-BoldItalic.ttf'),
}
DEFAULT_FONT = OPEN_SANS_REGULAR

LOADED_FONTS = {}

def get_custom_font(font_name):
    """Get a custom TTF"""
    # Has the font been loaded?
    if LOADED_FONTS.get(font_name):
        # return the font object
        return LOADED_FONTS[font_name]

    # Get the font path
    font_path = FONT_INFO.get(font_name)
    if not font_path:
        # No path! Use the default font
        print('Font not found! {font_name}')
        if LOADED_FONTS.get(DEFAULT_FONT):
            return LOADED_FONTS[DEFAULT_FONT]
        font_path = FONT_INFO.get(DEFAULT_FONT)

    # Load the font!
    font_obj = TrueTypeFont.true_type_font_from_file(Path(font_path))

    # Save the font for future use
    LOADED_FONTS[font_name] = font_obj

    # return the font object
    return font_obj


# construct the Font object
# font_path: Path = Path(__file__).parent / "Jsfont-Regular.ttf"
# font: Font = TrueTypeFont.true_type_font_from_file(font_path)
