#!/usr/bin/env python3
#
# Copyright (c) 2017-, Stephen B. Hope
# All rights reserved.
#
# CommAI-env source files, Copyright (c) 2016-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.

# TODO fix imports
import unittest
import core.events as events


class MyEvent(object):
    # TODO static class
    """

    """
    pass


class TestEvents(unittest.TestCase):
    """

    """
    def __init__(self, *args, **kwargs):
        """

        :param args:
        :param kwargs:
        """
        super(TestEvents, self).__init__(*args, **kwargs)

    def testEvents(self):
        """

        :return:
        """
        self.event_raised = False

        def on_start(self, event):
            # TODO attr event not used, self shadowing
            """

            :param self:
            :param event:
            :return:
            """
            self.event_raised = True

        em = events.EventManager()
        em.register(self,
                    events.Trigger(MyEvent, lambda e: True, on_start))
        em.raise_event(MyEvent())
        self.assertTrue(self.event_raised)


def main():
    unittest.main()

if __name__ == '__main__':
    main()
