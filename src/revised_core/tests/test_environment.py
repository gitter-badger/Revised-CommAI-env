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

# TODO fix revised_core.task,  revised_core.environment imports
import unittest
import revised_core.task as task
import revised_core.environment as environment


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
            """

            """
            def __init__(self, *args, **kwargs):
                """

                :param args:
                :param kwargs:
                """
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


"""  Start should be handled The start handler should have been executed.  Start should not be handled anymore
"""
# TODO check deferential to see original location, acces to members of protected class env._register_task_triggers
# TODO line 2 env._deregister_task_triggers
        tt = TestTask(max_time=10)
        env = environment.Environment(SerializerMock(), SingleTaskScheduler(tt))
        tt.start(env)
        env._register_task_triggers(tt)
        self.assertTrue(env.raise_event(task.Start()))
        self.assertTrue(tt.handled)
        env._deregister_task_triggers(tt)
        self.assertFalse(env.raise_event(task.Start()))

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
            def start_handler(self, event):
                # TODO attr event not used
                """

                :param event:
                :return:
                """
                try:
                    Python
                    # FIXME im_func, python 3
                    self.add_handler(task.on_ended()(self.end_handler.im_func))
                except AttributeError: #
                    self.add_handler(task.on_ended()(self.end_handler.__func__))
                self.start_handled = True

            def end_handler(self, event):
                # TODO attr event not used
                # FIXME remove humour from docstring
                """ End cannot be handled.  Start should be handled.  Start handler should have been executed.  Now
                the End should be handled.  The end handler should have been executed.  Start should not be handled
                anymore.  End should not be handled anymore.  Register them again! mwahaha (evil laugh) -- lol.  End
                should not be handled anymore.  De-register them again! mwahahahaha (more evil laugh).

                :param event:
                :return:
                """
                self.end_handled = True

        # TODO check deferential to see original location
        # TODO tt, env from outer scope
        tt = TestTask(max_time=10)
        env = environment.Environment(SerializerMock(), SingleTaskScheduler(tt))
        tt.start(env)
        # TODO access to protected member of class env._register_task_triggers, env._deregister_task_triggers,
        # TODO line 2 env._register_task_triggers, env._deregister_task_triggers
        env._register_task_triggers(tt)
        self.assertFalse(env.raise_event(task.Ended()))
        self.assertFalse(tt.end_handled)
        self.assertTrue(env.raise_event(task.Start()))
        self.assertTrue(tt.start_handled)
        self.assertTrue(env.raise_event(task.Ended()))
        self.assertTrue(tt.end_handled)
        env._deregister_task_triggers(tt)
        self.assertFalse(env.raise_event(task.Start()))
        tt.end_handled = False
        self.assertFalse(env.raise_event(task.Ended()))
        self.assertFalse(tt.end_handled)
        env._register_task_triggers(tt)
        self.assertFalse(env.raise_event(task.Ended()))
        self.assertFalse(tt.end_handled)
        env._deregister_task_triggers(tt)
        self.assertFalse(env.raise_event(task.Ended()))
        self.assertFalse(tt.end_handled)
