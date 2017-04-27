#!/usr/bin/env python3
#
# Copyright (c) 2017-, Stephen B. Hope
# All rights reserved.
#
# CommAI-env source files, Copyright (c) 2016-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the LICENSE file in the root directory of this
# source tree. An additional grant of patent rights can be found in the PATENTS file in the same directory.

# TODO fix revised_core imports
import unittest
import revised_core.task as task
import revised_core.session as session
import revised_core.serializer as serializer
import revised_core.environment as environment
from revised_core.obs.observer import Observable


class NullTask(task.Task):
    """

    """
    def __init__(self):
        """

        """
        super(NullTask, self).__init__(max_time=100)


class EnvironmentMock(object):
    """

    """
    def __init__(self):
        """

        """
        self.task_updated = Observable()

    def set_task(self, task):
        """

        :param task:
        :return:
        """
        self.task = task

    def next(self, token):
        """ always return a reward od 1

        :param token:
        :return:
        """
        self.task_updated(self.task)
        return token, 1

    def raise_event(self, event):
        # TODO static
        """

        :param event:
        :return:
        """
        pass

    def set_task_scheduler(self, ts):
        # TODO static
        """

        :param ts:
        :return:
        """
        pass


class LearnerMock(object):
    """

    """
    def next(self, token):
        # TODO static
        """

        :param token:
        :return:
        """
        return token

    def try_reward(self, r):
        # TODO static
        """

        :param r:
        :return:
        """
        pass


class SingleTaskScheduler:
    """

    """
    def __init__(self, task):
        """

        :param task:
        """
        self.task = task

    def get_next_task(self):
        """

        :return:
        """
        return self.task

    def reward(self, reward):
        # TODO static
        """

        :param reward:
        :return:
        """
        pass


class TestSession(unittest.TestCase):
    """

    """

    def testLimitReward(self):
        """

        :return:
        """
        env = environment.Environment(serializer.StandardSerializer(), SingleTaskScheduler(NullTask()))
        learner = LearnerMock()
        s = session.Session(env, learner)

        def on_time_updated(t):
            """

            :param t:
            :return:
            """
            if t >= 20:
                s.stop()
        s.total_time_updated.register(on_time_updated)
        s.run()
        self.assertLessEqual(s._total_reward, 10)
