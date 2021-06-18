import os, sys
from os.path import abspath, dirname, join, isdir, isfile

# 'pub_scripts' directory
BASE_DIR = dirname(abspath(__file__))

TEMPLATES_DIR = join(BASE_DIR, 'templates')
OUTPUT_DIR = join(BASE_DIR, 'rendered')

dir_names = [TEMPLATES_DIR, OUTPUT_DIR]
for dname in dir_names:
    if not isdir(dname):
        os.makedirs(dname)
        print(f'creatd directory: {dname}')