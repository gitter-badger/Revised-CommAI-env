# Copyright (c) 2017-, Stephen B. Hope
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the LICENSE.md file in the root directory of this
# source tree. An additional grant of patent rights can be found in the PATENTS file in the same directory.

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = dict(description='A new standard environment for machine learning and AI research',
              author='Stephen B. Hope',
              url='https://github.com/stephenbhope/Revised-CommAI-env',
              download_url='https://github.com/stephenbhope/Revised-CommAI-env',
              author_email='stephenbhope@gmail.com.',
              version='0.2',
              install_requires=['nose'],
              packages=[''],
              scripts=[],
              copywrite='Copyright(C) 2017-, Stephen B. Hope',
              name='Revised CommAI-env')

setup(**config)

