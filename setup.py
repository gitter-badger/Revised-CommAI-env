# Copyright (c) 2017-, Stephen B. Hope
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the LICENSE file in the root directory of this
# source tree. An additional grant of patent rights can be found in the PATENTS file in the same directory.

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = dict(description='A standard environment for machine learning',
              author='Stephen Hope',
              url='https://github.com/stephenbhope/Revised-CommAI-env',
              download_url='https://github.com/stephenbhope/Revised-CommAI-env',
              author_email='stephenbhope@gmail.com.',
              version='0.1',
              install_requires=['nose'],
              packages=['NAME'],
              scripts=[],
              name='Revised CommAI-env')

setup(**config)