#!/usr/bin/env python3
#
# Copyright (c) 2017-, Stephen B. Hope. All rights reserved.
#
# CommAI-env source files, Copyright (c) 2016-present, Facebook, Inc. All rights reserved.
#
# This source code is licensed under the BSD-style license found in the LICENSE file in the root directory of this
# source tree. An additional grant of patent rights can be found in the PATENTS file in the same directory.

# TODO fix tasks, revised_core, imports
import unittest
import tasks.micro.nano as nano
from tasks.competition.tests.helpers import task_messenger
from revised_core.serializer import IdentitySerializer


class TestRepetitionTasks(unittest.TestCase):
    """
    task testing routines
    """
        def trySolution(self, Task, patient, solution, correct):
            """ rewards will be negative or positive.  try to get as much reward as possible from the solution

            :param Task:
            :param patient:
            :param solution:
            :param correct:
            :return:
            """
            with task_messenger(lambda: Task(patient=patient), serializer=IdentitySerializer()) as m:
                    n = m._env._max_reward_per_task
                    sign = correct and 1 or -1
                    for i in range(n):
                        m.send(solution)
                        self.assertEqual(m.get_cumulative_reward(), sign * (i + 1))

        def testTask0(self):
            """ Impatient solutions

            you have to stay silent for 5 bits (because by the time the 6th bit gets emitted, the task is already
            rewarding you for being silent), and then wait for one more bit for the task separator (to be removed
            later) This leads to 1 / 32 correct ratio. and also the last bit of the task doesn't really count.
            speaking earlier shouldn't work and stop you the patient teacher waits a bit longer

            :return:
            """
            self.trySolution(nano.Task0, patient=False, solution="0000000", correct=True)
            self.trySolution(nano.Task0, patient=False, solution="0000001", correct=True)
            self.trySolution(nano.Task0, patient=False, solution="0000010", correct=True)
            self.trySolution(nano.Task0, patient=False, solution="0000011", correct=True)
            self.trySolution(nano.Task0, patient=False, solution="000010", correct=False)
            self.trySolution(nano.Task0, patient=True, solution="0000100", correct=False)

        def testTask1(self):
            """ You have to say 1 by the 7th bit. What you say on the 8th bit doesn't matter. By the 8th bit is
            already too late. And the 6th bit too early. With a patient teacher you have to wait for the 8 bits of
            the task + 1 of the separator

            :return:
            """
            self.trySolution(nano.Task1, patient=False, solution="00000010", correct=True)
            self.trySolution(nano.Task1, patient=False, solution="00000011", correct=True)
            self.trySolution(nano.Task1, patient=False, solution="00000001", correct=False)
            self.trySolution(nano.Task1, patient=False, solution="0000010", correct=False)
            self.trySolution(nano.Task1, patient=True, solution="000001000", correct=False)

        def testTask10(self):
            """ You have to say 10 by the 8th bit. What you say on the 9th bit doesn't matter. If you didn't put a 1
            in the 8th bit, you are lost no matter what you do on the 9th bit. And the 7th bit is too early. With a
            patient teacher you have to wait for the 10 bits of the task + 1 of the separator

            :return:
            """
            self.trySolution(nano.Task10, patient=False, solution="0000000100", correct=True)
            self.trySolution(nano.Task10, patient=False, solution="0000000101", correct=True)
            self.trySolution(nano.Task10, patient=False, solution="000000000", correct=False)
            self.trySolution(nano.Task10, patient=False, solution="000000001", correct=False)
            self.trySolution(nano.Task10, patient=False, solution="00000010", correct=False)
            self.trySolution(nano.Task10, patient=True, solution="00000010000", correct=False)

        def testTask11(self):
            """ You have to say 10 by the 8th bit. What you say on the 9th bit doesn't matter. If you didn't put a 1
            in the 8th bit, you are lost no matter what you do on the 9th bit. And the 7th bit is too early With a
            patient teacher you have to wait for the 10 bits of the task + 1 of the separator

            :return:
            """
            # TODO no statement at end
            self.trySolution(nano.Task11, patient=False, solution="0000000110", correct=True)
            self.trySolution(nano.Task11, patient=False, solution="0000000111", correct=True)
            self.trySolution(nano.Task11, patient=False, solution="000000000", correct=False)
            self.trySolution(nano.Task11, patient=False, solution="000000001", correct=False)
            self.trySolution(nano.Task11, patient=False, solution="00000010", correct=False)
            self.trySolution(nano.Task11, patient=False, solution="00000011", correct=False)
            self.trySolution(nano.Task11, patient=True, solution="00000011000", correct=False)


def main():
    unittest.main()


if __name__ == '__main__':
    main()
