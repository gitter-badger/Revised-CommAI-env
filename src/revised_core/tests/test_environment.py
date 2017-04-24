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

# TODO fix imports
import unittest
import core.task as task
import core.environment as environment


class SerializerMock(object):
    # TODO static class
    """

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
        # TODO static function
        """

        :param reward:
        :return:
        """
        pass


class TestEnvironment(unittest.TestCase):
    """

    """

    def testRegistering(self):
        """

        :return:
        """
        class TestTask(task.Task):
            def __init__(self, *args, **kwargs):
                super(TestTask, self).__init__(*args, **kwargs)
                self.handled = False

            @task.on_start()
            def start_handler(self, event):
                # TODO attr event not used
                """

                :param event:
                :return:
                """
                self.handled = True


        tt = TestTask(max_time=10)
        env = environment.Environment(SerializerMock(), SingleTaskScheduler(tt))
        tt.start(env)
        env._register_task_triggers(tt)
        self.assertTrue(env.raise_event(task.Start()))  # Start should be handled
        self.assertTrue(tt.handled)  # The start handler should have been executed
        env._deregister_task_triggers(tt)
        self.assertFalse(env.raise_event(task.Start()))  # Start should not be handled anymore

    def testDynRegistering(self):
        """

        :return:
        """
        class TestTask(task.Task):
            """

            """
            def __init__(self, *args, **kwargs):
                """

                :param args:
                :param kwargs:
                """
                super(TestTask, self).__init__(*args, **kwargs)
                self.start_handled = False
                self.end_handled = False

            @task.on_start()
            """

            """
            def start_handler(self, event):
                # TODO attr event not used
                """

                :param event:
                :return:
                """
                try:
                    self.add_handler(task.on_ended()(self.end_handler.im_func))
                    # TODO fix im_func
                except AttributeError: # Python 3
                    self.add_handler(task.on_ended()(self.end_handler.__func__))
                self.start_handled = True

            def end_handler(self, event):
                # TODO attr event not used
                """

                :param event:
                :return:
                """
                self.end_handled = True

        tt = TestTask(max_time=10)
        env = environment.Environment(SerializerMock(), SingleTaskScheduler(tt))
        tt.start(env)
        env._register_task_triggers(tt)
        self.assertFalse(env.raise_event(task.Ended()))  # End cannot be handled
        self.assertFalse(tt.end_handled)
        self.assertTrue(env.raise_event(task.Start()))  # Start should be handled
        self.assertTrue(tt.start_handled)  # Start handler shpuld have been executed
        self.assertTrue(env.raise_event(task.Ended()))  # Now the End should be handled
        self.assertTrue(tt.end_handled)  # The end handler should have been executed
        env._deregister_task_triggers(tt)
        self.assertFalse(env.raise_event(task.Start()))  # Start should not be handled anymore
        tt.end_handled = False
        self.assertFalse(env.raise_event(task.Ended()))  # End should not be handled anymore
        self.assertFalse(tt.end_handled)
        # TODO rewrite - humor
        # Register them again! mwahaha (evil laugh) -- lol
        env._register_task_triggers(tt)
        self.assertFalse(env.raise_event(task.Ended()))  # End should not be handled anyore
        self.assertFalse(tt.end_handled)
        # TODO rewrite - humor
        # Deregister them again! mwahahahaha (more evil laugh)
        env._deregister_task_triggers(tt)
        self.assertFalse(env.raise_event(task.Ended()))
        self.assertFalse(tt.end_handled)
