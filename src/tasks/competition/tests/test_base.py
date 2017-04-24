#!/usr/bin/env python3
#
# Copyright (c) 2017-, Stephen B. Hope. All rights reserved.
# Copyright (c) 2016-present, Facebook, Inc. All rights reserved.
#
# This source code is licensed under the BSD-style license found in the LICENSE.md file in the root directory of this
# source tree. An additional grant of patent rights can be found in the PATENTS file in the same directory.

# TODO fix imports
import unittest
import tasks.competition.base as base
from core.task import on_start, on_message
from tasks.competition.tests.helpers import task_messenger


class TestBase(unittest.TestCase):
    """

    """

    def testIgnoreInterruptions(self):
        """

        :return:
        """
        class TestTask(base.BaseTask):
            def __init__(self, max_time=1000):
                """

                :param max_time:
                """
                super(TestTask, self).__init__(max_time=max_time)
                self.interrupted = False

            @on_start()
            def on_start(self, event):
                # TODO event not used
                """

                :param event:
                :return:
                """
                self.set_message("Saying.")

            @on_message(r"Interrupt.$")
            def on_interrupt(self, event):
                """

                :param event:
                :return:
                """
                # TODO event not used
                self.set_message("Interrupted.")

            @on_message(r"Respectful.$")
            # TODO event not used
            def on_respect(self, event):
                """

                :param event:
                :return:
                """
                self.set_message("Good.")

        with task_messenger(TestTask) as m:
            # test for not solving it at all
            message = "Interrupt."
            m.send(message)
            blen = m.read()
            self.assertEqual(blen, 0)
            self.assertFalse(m.get_last_message() == "Interrupted.")
            m.send("Respectful.")
            blen = m.read()
            self.assertGreater(blen, 0)
            self.assertEqual(m.get_last_message(), 'Good.')
