#!/usr/bin/env python3
#
# Copyright (c) 2017-, Stephen B. Hope
# All rights reserved.
#
# CommAi-env Source code Copyright (c) 2016-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.

"""
import all learners in the current directory
"""
import glob

modules = glob.glob('./*.py')
for each_module in modules:
    __import__('learner' + m)

"""
Sets the user interface to get the user input
"""
self._view = view


