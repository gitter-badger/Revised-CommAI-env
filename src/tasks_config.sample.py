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

# TODO fix imports
import worlds.grid_world
import tasks.sample.sample_tasks
import core.scheduler


def create_tasks():
    """

    :return:
    """
    # a world for some tasks
    grid_world = GridWorld()
    # we get today's task menu
    return RandomTaskScheduler([PickAnApple(grid_world), MovingTask(grid_world)])
