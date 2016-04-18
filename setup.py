#!/usr/bin/env python

from distutils.core import setup
from sys import argv

import glob
from os.path import basename

extensions = []
if not '--no-extensions' in argv:
    for ext in glob.glob('pyglbuffers_extensions/*.py'):
        if 'create_mmo' in ext or '__init__' in ext:
            continue

        name = basename(ext).split('.')[0]
        extensions.append('pyglbuffers_extensions.'+name)        

else:
    argv.remove('--no-extensions')
   

setup(name='pyglbuffers',
      version='1.0.0',
      description='OpenGL buffers wrapper for python',
      author='Gabriel Dubé',
      author_email='gdube@azanka.ca',
      license='MIT',
      url='https://github.com/gabdube/pyglbuffers',
      download_url='https://github.com/gabdube/pyglbuffers',
      py_modules=['pyglbuffers']+extensions,
     )
