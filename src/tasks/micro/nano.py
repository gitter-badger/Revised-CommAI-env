#!/usr/bin/env python3
#
# Copyright (c) 2017-, Stephen B. Hope. All rights reserved.
#
# CommAI-env source files, Copyright (c) 2016-present, Facebook, Inc. All rights reserved.
#
# This source code is licensed under the BSD-style license found in the LICENSE.md file in the root directory of this
# source tree. An additional grant of patent rights can be found in the PATENTS file in the same directory.

# TODO fix imports
from core.task import on_start, on_message, on_timeout, on_output_message, Task

""" The following tasks us the following bit-based vocabulary: stay_quiet 01, space 00. period 10,  say 11
"""
default_patient = False


class NanoTask(Task):
    """

    """
    def __init__(self, max_time=1000, patient=default_patient):
        """

        :param max_time:
        :param patient:
        """
        super(NanoTask, self).__init__(max_time=max_time)
        self.patient = patient

    def get_default_output(self):
        """ Pad with 0s at the end

        :return:
        """
        # TODO  def outside __init__
        self.task_separator_issued = True
        return '0'

    def deinit(self):
        """

        :return:
        """
        if not self.task_separator_issued:
            self.add_message(self.get_default_output())

    @on_start()
    def reset_received_reward(self, event):
        """

        :param event:
        :return:
        """
        # TODO event not used, def outside __init__
        self.task_separator_issued = False
        self.received_reward = False

    def set_reward(self, reward):
        """

        :param reward:
        :return:
        """
        # TODO def outside __init__
        if self.patient:
            if not self.received_reward:
                self.received_reward = reward
        else:
            super(NanoTask, self).set_reward(reward)

    @on_timeout()
    def on_timeout(self, timeout):
        # TODO timeout not used
        """ import pdb; pdb.set_trace()

        :param timeout:
        :return:
        """
        if self.patient:
            assert self.received_reward
            # TODO unresolved attrib ref set_reward super
            super(Task, self).set_reward(self.received_reward)


class Task0(NanoTask):
    """
    in task0, the learner must only produce the 0 bit until the end of the task
    """
    def __init__(self, patient=default_patient):
        """

        :param patient:
        """
        super(Task0, self).__init__(max_time=6, patient=patient)

    @on_start()
    def give_instructions(self, event):
        # TODO event not used
        """

        :param event:
        :return:
        """
        self.set_message('011000')

    @on_output_message(r'1000')
    def reward_at_end(self, event):
        """

        :param event:
        :return:
        """
        # TODO event not used, def outside __init__
        self.finished_talking = True
        self.set_reward(1)

    @on_message(r'1')
    def punish_not_quiet(self, event):
        """

        :param event:
        :return:
        """
        # TODO event not used
        self.set_reward(-1)


class Task1(NanoTask):
    """
    in task1, the learner must produce 1 right after the environment stops speaking (and 0 while env is talking)
    """
    def __init__(self, patient=default_patient):
        """

        :param patient:
        """
        super(Task1, self).__init__(max_time=8, patient=patient)

    @on_start()
    def give_instructions(self, event):
        """

        :param event:
        :return:
        """
        # TODO event not used, def outside __init__
        self.finished_talking = False
        self.set_message('1111000')

    @on_output_message(r'1000')
    def set_finished_talking_flag(self, event):
        """

        :param event:
        :return:
        """
        # TODO event not used, def outside __init__
        self.finished_talking = True

    @on_message(r'.')
    def check_right_response(self, event):
        """

        :param event:
        :return:
        """
        if event.is_message('1'):
            if self.finished_talking:
                self.set_reward(1)
            else:
                self.set_reward(-1)
        elif self.finished_talking:
            self.set_reward(-1)


class Task11(NanoTask):
    """
    task11 is like task1, but not the learner must produce a 11 bit sequence
    """
    def __init__(self, patient=default_patient):
        """

        :param patient:
        """
        super(Task11, self).__init__(max_time=10, patient=patient)

    @on_start()
    def give_instructions(self, event):
        """

        :param event:
        :return:
        """
        # TODO event not used, def outside __init__
        self.finished_talking = False
        self.learner_turn_counter = 0
        self.set_message('11111000')

    @on_output_message(r'1000')
    def set_finished_talking_flag(self, event):
        """

        :param event:
        :return:
        """
        # TODO event not used, def outside __init__
        self.finished_talking = True

    @on_message(r'.')
    def check_right_response(self, event):
        """

        :param event:
        :return:
        """
        if event.is_message('1'):
            if self.finished_talking:
                if self.learner_turn_counter == 0:
                    self.learner_turn_counter += 1
                else:
                    self.set_reward(1)
            else:
                self.set_reward(-1)
        elif self.finished_talking:
            self.set_reward(-1)


class Task10(NanoTask):
    """
    task10 is like task11, but not the learner must produce a 10 bit sequence
    """
    def __init__(self, patient=default_patient):
        """

        :param patient:
        """
        super(Task10, self).__init__(max_time=10, patient=patient)

    @on_start()
    def give_instructions(self, event):
        """

        :param event:
        :return:
        """
        # TODO event not used, def outside __init__
        self.finished_talking = False
        self.learner_turn_counter = 0
        self.set_message('11101000')

    @on_output_message(r'1000')
    def set_finished_talking_flag(self, event):
        """

        :param event:
        :return:
        """
        # TODO event not used, def outside __init__
        self.finished_talking = True

    @on_message(r'.')
    def check_right_response(self, event):
        """

        :param event:
        :return:
        """
        if event.is_message('1'):
            if self.finished_talking and self.learner_turn_counter == 0:
                    self.learner_turn_counter += 1
            else:
                self.set_reward(-1)
        elif self.finished_talking:
            if self.learner_turn_counter > 0:
                self.set_reward(1)
            else:
                self.set_reward(-1)
