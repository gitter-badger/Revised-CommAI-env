#!/usr/bin/env python3
#
# Copyright (c) 2017-, Stephen B. Hope. All rights reserved.
#
# CommAI-env source files, Copyright (c) 2016-present, Facebook, Inc. All rights reserved.
#
# This source code is licensed under the BSD-style license found in the LICENSE.md file in the root directory of this
# source tree. An additional grant of patent rights can be found in the PATENTS file in the same directory.

# TODO fix tasks, revised_core, imports
import unittest
import tasks.micro.small_comp as small_comp
from tasks.competition.tests.helpers import task_messenger
from Revised_core.serializer import IdentitySerializer


class TestSmallCompTasks(unittest.TestCase):
    """
    helper methods
    """
    def _test_solution(self, Task, get_answer, answer_correct=True):
        # TODO agr case to lower
        """ we will solve the task N times (to check for sync issues), wait for the instructions there are some
        instructions we should have received the reward from the previous iteration extract the correct answer get
        the next task going

        :param Task:
        :param get_answer:
        :param answer_correct:
        :return:
        """
        sign = answer_correct and 1 or -1
        with task_messenger(Task, serializer = IdentitySerializer()) as m:
            n = m._env._max_reward_per_task
            for i in range(n):
                instructions_blen = m.read()
                self.assertGreater(instructions_blen, 0, "No instructions!")
                self.assertEqual(m.get_cumulative_reward(), sign * i)
                answer = get_answer(m)
                m.send(answer)
                m.send()
"""
unit tests
"""
    def testReverseXTask(self):
        """ function that reads the instructions and produces the correct answer

        :param self:
        :return:
        """
        def get_correct_answer(m):
            """

            :param m:
            :return:
            """
            answer, = m.search_full_message(r"V([01]*)\.$")
            return answer[::-1]

        def get_incorrect_answer_impatient(m):
            """ function that reads the instructions and produces an incorrect answer try to solve correctly try to
            solve incorrectly with an impatient teacher

            :param m:
            :return:
            """
            answer, = m.search_full_message(r"V([01]*)\.$")
            return "1" if answer[-1] == "0" else "0"

        self._test_solution(small_comp.ReverseXTask, get_correct_answer, True)
        # TODO statement expected
        self._test_solution(small_comp.ReverseXTask, get_incorrect_answer_impatient, False)


def main():
    unittest.main()


if __name__ == '__main__':
    main()
