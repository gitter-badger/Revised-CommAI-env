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
from core.task import Task, on_start, on_message, on_timeout, on_output_message
from tasks.competition.base import BaseTask
import logging
import random

"""
the small composition task use the following vocabulary:
    V reverse function
    P repeat function
    O rotate function
    C concatenate function
    0/1 alphabet for argument strings

constant to keep same input string length across tasks max_string_length = 5
"""

def return_random_01_sequence(L):
    """

    :param L:
    :return:
    """
    maxL=random.randint(1,L)
    random_string = ""
    for i in range(maxL):
        random_string += str(random.randrange(2))
    return random_string

def repeat_sequence(repetitions,sequence):
    """

    :param repetitions:
    :param sequence:
    :return:
    """
    repeated_sequence = ""
    for i in range(repetitions):
        repeated_sequence += sequence
    return repeated_sequence

def reverse_sequence(sequence):
    """

    :param sequence:
    :return:
    """
    return sequence[::-1]

def rotate_sequence(steps,sequence):
    """

    :param steps:
    :param sequence:
    :return:
    """
    string_length = len(sequence)
    if (steps>=string_length):
        steps=steps%string_length
    if (steps<0):
        raise ValueError('rotation step count (' + str(steps) + ') must be non-negative')
    rotated_sequence = ""
    for i in range(string_length):
        if (i>=steps):
            rotated_sequence += sequence[i-steps]
        else:
            rotated_sequence += sequence[i-steps+string_length]
    return rotated_sequence

class ReverseXTask(Task):
    """ NB: max_time will be dynamically adjusted below

    """
    def __init__(self, world=None):
        """

        :param world:
        """
        super(ReverseXTask, self).__init__(world=world, max_time=0)
        self.logger = logging.getLogger(__name__)

    @on_start()
    def give_instructions(self, event):
        """

        :param event:
        :return:
        """
        # TODO event not used
        self.response_check = False
        proposed_string = return_random_01_sequence(max_string_length)
        message = "V" + proposed_string + "."
        self.set_message(message)
        self.response_string = reverse_sequence(proposed_string)
        self._max_time = (8*len(message)) + (8*len(self.response_string)) - 8

    @on_output_message(r'\.$')
    def set_response_check(self, event):
        """

        :param event:
        :return:
        """
        # TODO event not used
        self.response_check = True
        self.response_counter = 0

    @on_message(r".$")
    def check_response(self, event):
        """

        :param event:
        :return:
        """
        if (self.response_check):
            # self.logger.info("current counter:" + str(self.response_counter))
            if (event.is_message(self.response_string[self.response_counter])):
                if (self.response_counter==(len(self.response_string)-1)):
                    self.set_reward(1)
                else:
                    self.response_counter = self.response_counter + 1
            else:
                self.set_reward(-1)
"""
     @on_timeout()
     def punish_slow_learner(self, event):
         self.set_reward(-1)
"""

class RepeatNXTask(BaseTask):
    def __init__(self, world=None):
        """ NB: max_time will be dynamically adjusted below
                self.logger = logging.getLogger(__name__)
        :param world:
        """
        super(RepeatNXTask, self).__init__(world=world, max_time=0)

    @on_start()
    def give_instructions(self, event):
        """

        :param event:
        :return:
        """
        # TODO event not used
        self.response_check = False
        proposed_string = return_random_01_sequence(max_string_length)
        repetitions = random.randint(1,4)
        message = "P" + str(repetitions) + "," + proposed_string + "."
        self.set_message(message)
        self.response_string = repeat_sequence(repetitions, proposed_string)
        self._max_time = (8*len(message)) + (8*len(self.response_string)) - 8

    @on_output_message(r'\.$')
    def set_response_check(self, event):
        # TODO event not used
        """

        :param event:
        :return:
        """
        self.response_check = True
        self.response_counter = 0

    @on_message(r".$")
    def check_response(self, event):
        """

        :param event:
        :return:
        """
        if (self.response_check):
            # self.logger.info("current counter:" + str(self.response_counter))
            if (event.is_message(self.response_string[self.response_counter])):
                if (self.response_counter==(len(self.response_string)-1)):
                    self.set_reward(1)
                else:
                    self.response_counter = self.response_counter + 1
            else:
                self.set_reward(-1)
"""
     @on_timeout()
     def punish_slow_learner(self, event):
         self.set_reward(-1)
"""

class RotateRXTask(BaseTask):
    def __init__(self, world=None):
        """ NB: max_time will be dynamically adjusted below
                self.logger = logging.getLogger(__name__)

        :param world:
        """
        super(RotateRXTask, self).__init__(world=world, max_time=0)

    @on_start()
    def give_instructions(self, event):
        """

        :param event:
        :return:
        """
        # TODO event not used
        self.response_check = False
        proposed_string = return_random_01_sequence(max_string_length)
        steps = random.randint(1,len(proposed_string))
        message = "O" + str(steps) + "," + proposed_string + "."
        self.set_message(message)
        self.response_string = rotate_sequence(steps,proposed_string)
        self._max_time = (8*len(message)) + (8*len(self.response_string)) - 8

    @on_output_message(r'\.$')
    def set_response_check(self, event):
        """

        :param event:
        :return:
        """
        # TODO event not used
        self.response_check = True
        self.response_counter = 0

    @on_message(r".$")
    def check_response(self, event):
        """

        :param event:
        :return:
        """
        if (self.response_check):
            # self.logger.info("current counter:" + str(self.response_counter))
            if (event.is_message(self.response_string[self.response_counter])):
                if (self.response_counter==(len(self.response_string)-1)):
                    self.set_reward(1)
                else:
                    self.response_counter = self.response_counter + 1
            else:
                self.set_reward(-1)
"""
     @on_timeout()
     def punish_slow_learner(self, event):
         self.set_reward(-1)
"""

class ConcatenateXYTask(BaseTask):
    """

    """
    def __init__(self, world=None):
        """ NB: max_time will be dynamically adjusted below
                self.logger = logging.getLogger(__name__)
        :param world:
        """
        super(ConcatenateXYTask, self).__init__(world=world, max_time=0)

    @on_start()
    def give_instructions(self, event):
        """

        :param event:
        :return:
        """
        # TODO event not used
        self.response_check = False
        proposed_string_1 = return_random_01_sequence(max_string_length)
        proposed_string_2 = return_random_01_sequence(max_string_length)
        message = "C" + proposed_string_1 + "," + proposed_string_2 + "."
        self.set_message(message)
        self.response_string = proposed_string_1 + proposed_string_2
        self._max_time = (8*len(message)) + (8*len(self.response_string)) - 8

    @on_output_message(r'\.$')
    def set_response_check(self, event):
        """

        :param event:
        :return:
        """
        # TODO event not used
        self.response_check = True
        self.response_counter = 0

    @on_message(r".$")
    def check_response(self, event):
        """

        :param event:
        :return:
        """
        if (self.response_check):
#            self.logger.info("current counter:" + str(self.response_counter))
            if (event.is_message(self.response_string[self.response_counter])):
                if (self.response_counter==(len(self.response_string)-1)):
                    self.set_reward(1)
                else:
                    self.response_counter = self.response_counter + 1
            else:
                self.set_reward(-1)
"""
     @on_timeout()
     def punish_slow_learner(self, event):
         self.set_reward(-1)
"""

class ReverseRepeatNXTask(BaseTask):
    """
    composed tasks from here
    """
    def __init__(self, world=None):
        """ NB: max_time will be dynamically adjusted below
                self.logger = logging.getLogger(__name__)
        :param world:
        """
        super(ReverseRepeatNXTask, self).__init__(world=world, max_time=0)

    @on_start()
    def give_instructions(self, event):
        """

        :param event:
        :return:
        """
        # TODO event not used
        self.response_check = False
        repetitions = random.randint(1,4)
        proposed_string = return_random_01_sequence(max_string_length)
        message = "VP" + str(repetitions) + "," + proposed_string + "."
        self.set_message(message)
        self.response_string = reverse_sequence(repeat_sequence(repetitions,proposed_string))
        self._max_time = (8*len(message)) + (8*len(self.response_string)) - 8

    @on_output_message(r'\.$')
    def set_response_check(self, event):
        """

        :param event:
        :return:
        """
        # TODO event not used
        self.response_check = True
        self.response_counter = 0

    @on_message(r".$")
    def check_response(self, event):
        """

        :param event:
        :return:
        """
        if (self.response_check):
            # self.logger.info("current counter:" + str(self.response_counter))
            if (event.is_message(self.response_string[self.response_counter])):
                if (self.response_counter==(len(self.response_string)-1)):
                    self.set_reward(1)
                else:
                    self.response_counter = self.response_counter + 1
            else:
                self.set_reward(-1)
"""
     @on_timeout()
     def punish_slow_learner(self, event):
         self.set_reward(-1)
"""

class ReverseRotateRXTask(BaseTask):
    def __init__(self, world=None):
        """ NB: max_time will be dynamically adjusted below
                self.logger = logging.getLogger(__name__)
        :param world:
        """
        super(ReverseRotateRXTask, self).__init__(world=world, max_time=0)

    @on_start()
    def give_instructions(self, event):
        """

        :param event:
        :return:
        """
        # TODO event not used
        self.response_check = False
        proposed_string = return_random_01_sequence(max_string_length)
        steps = random.randint(1,len(proposed_string))
        message = "VO" + str(steps) + "," + proposed_string + "."
        self.set_message(message)
        self.response_string = reverse_sequence(rotate_sequence(steps, proposed_string))
        self._max_time = (8*len(message)) + (8*len(self.response_string)) - 8

    @on_output_message(r'\.$')
    def set_response_check(self, event):
        """

        :param event:
        :return:
        """
        # TODO event not used
        self.response_check = True
        self.response_counter = 0

    @on_message(r".$")
    def check_response(self, event):
        """

        :param event:
        :return:
        """
        if (self.response_check):
            # self.logger.info("current counter:" + str(self.response_counter))
            if (event.is_message(self.response_string[self.response_counter])):
                if (self.response_counter==(len(self.response_string)-1)):
                    self.set_reward(1)
                else:
                    self.response_counter = self.response_counter + 1
            else:
                self.set_reward(-1)
"""
     @on_timeout()
     def punish_slow_learner(self, event):
         self.set_reward(-1)
"""


class ReverseConcatenateXYTask(BaseTask):
    def __init__(self, world=None):
        """ NB: max_time will be dynamically adjusted below
                self.logger = logging.getLogger(__name__)
        :param world:
        """
        super(ReverseConcatenateXYTask, self).__init__(world=world, max_time=0)


    @on_start()
    def give_instructions(self, event):
        """

        :param event:
        :return:
        """
        # TODO event not used
        self.response_check = False
        proposed_string_1 = return_random_01_sequence(max_string_length)
        proposed_string_2 = return_random_01_sequence(max_string_length)
        message = "VC" + proposed_string_1 + "," + proposed_string_2 + "."
        self.set_message(message)
        self.response_string = reverse_sequence(proposed_string_1 + proposed_string_2)
        self._max_time = (8*len(message)) + (8*len(self.response_string)) - 8

    @on_output_message(r'\.$')
    def set_response_check(self, event):
        """

        :param event:
        :return:
        """
        # TODO event not used
        self.response_check = True
        self.response_counter = 0

    @on_message(r".$")
    def check_response(self, event):
        """

        :param event:
        :return:
        """
        if (self.response_check):
            # self.logger.info("current counter:" + str(self.response_counter))
            if (event.is_message(self.response_string[self.response_counter])):
                if (self.response_counter==(len(self.response_string)-1)):
                    self.set_reward(1)
                else:
                    self.response_counter = self.response_counter + 1
            else:
                self.set_reward(-1)
"""
     @on_timeout()
     def punish_slow_learner(self, event):
         self.set_reward(-1)
"""

class RepeatNReverseXTask(BaseTask):
    def __init__(self, world=None):
        """ NB: max_time will be dynamically adjusted below
                self.logger = logging.getLogger(__name__)
        :param world:
        """
        super(RepeatNReverseXTask, self).__init__(world=world, max_time=0)

    @on_start()
    def give_instructions(self, event):
        """

        :param event:
        :return:
        """
        # TODO event not used
        self.response_check = False
        proposed_string = return_random_01_sequence(max_string_length)
        repetitions = random.randint(1,4)
        message = "P" + str(repetitions) + ",V" + proposed_string + "."
        self.set_message(message)
        self.response_string = reverse_sequence(repeat_sequence(repetitions, proposed_string))
        self._max_time = (8*len(message)) + (8*len(self.response_string)) - 8

    @on_output_message(r'\.$')
    def set_response_check(self, event):
        """

        :param event:
        :return:
        """
        # TODO event not used
        self.response_check = True
        self.response_counter = 0

    @on_message(r".$")
    def check_response(self, event):
        """

        :param event:
        :return:
        """
        if (self.response_check):
            # self.logger.info("current counter:" + str(self.response_counter))
            if (event.is_message(self.response_string[self.response_counter])):
                if (self.response_counter==(len(self.response_string)-1)):
                    self.set_reward(1)
                else:
                    self.response_counter = self.response_counter + 1
            else:
                self.set_reward(-1)
"""
     @on_timeout()
     def punish_slow_learner(self, event):
         self.set_reward(-1)
"""

class RepeatNRotateRXTask(BaseTask):
    def __init__(self, world=None):
        """ NB: max_time will be dynamically adjusted below
                self.logger = logging.getLogger(__name__)
        :param world:
        """
        super(RepeatNRotateRXTask, self).__init__(world=world, max_time=0)


    @on_start()
    def give_instructions(self, event):
        """

        :param event:
        :return:
        """
        # TODO event not used
        self.response_check = False
        proposed_string = return_random_01_sequence(max_string_length)
        repetitions = random.randint(1,4)
        steps = random.randint(1,len(proposed_string))
        message = "P" + str(repetitions) + ",O" + str(steps) + "," + proposed_string + "."
        self.set_message(message)
        self.response_string = repeat_sequence(repetitions, rotate_sequence(steps, proposed_string))
        self._max_time = (8*len(message)) + (8*len(self.response_string)) - 8

    @on_output_message(r'\.$')
    def set_response_check(self, event):
        # TODO event not used
        """

        :param event:
        :return:
        """
        self.response_check = True
        self.response_counter = 0

    @on_message(r".$")
    def check_response(self, event):
        """

        :param event:
        :return:
        """
        if (self.response_check):
#            self.logger.info("current counter:" + str(self.response_counter))
            if (event.is_message(self.response_string[self.response_counter])):
                if (self.response_counter==(len(self.response_string)-1)):
                    self.set_reward(1)
                else:
                    self.response_counter = self.response_counter + 1
            else:
                self.set_reward(-1)
"""
     @on_timeout()
     def punish_slow_learner(self, event):
         self.set_reward(-1)
"""

class RepeatNConcatenateXYTask(BaseTask):
    """

    """
    def __init__(self, world=None):
        """

        :param world:
        """
        super(RepeatNConcatenateXYTask, self).__init__(world=world, max_time=0)
        # NB: max_time will be dynamically adjusted below
#        self.logger = logging.getLogger(__name__)

    @on_start()
    def give_instructions(self, event):
        """

        :param event:
        :return:
        """
        # TODO event not used
        self.response_check = False
        proposed_string_1 = return_random_01_sequence(max_string_length)
        proposed_string_2 = return_random_01_sequence(max_string_length)
        repetitions = random.randint(1,4)
        message = "P" + str(repetitions) + ",C" + proposed_string_1 + "," + proposed_string_2 + "."
        self.set_message(message)
        self.response_string = repeat_sequence(repetitions, proposed_string_1 + proposed_string_2)
        self._max_time = (8*len(message)) + (8*len(self.response_string)) - 8

    @on_output_message(r'\.$')
    def set_response_check(self, event):
        """

        :param event:
        :return:
        """
        # TODO event not used
        self.response_check = True
        self.response_counter = 0

    @on_message(r".$")
    def check_response(self, event):
        """

        :param event:
        :return:
        """
        if (self.response_check):
#            self.logger.info("current counter:" + str(self.response_counter))
            if (event.is_message(self.response_string[self.response_counter])):
                if (self.response_counter==(len(self.response_string)-1)):
                    self.set_reward(1)
                else:
                    self.response_counter = self.response_counter + 1
            else:
                self.set_reward(-1)
"""
     @on_timeout()
     def punish_slow_learner(self, event):
         self.set_reward(-1)
"""

class RotateRReverseXTask(BaseTask):
    """

    """
    def __init__(self, world=None):
        """ NB: max_time will be dynamically adjusted below
                self.logger = logging.getLogger(__name__)

        :param world:
        """
        super(RotateRReverseXTask, self).__init__(world=world, max_time=0)

    @on_start()
    def give_instructions(self, event):
        """

        :param event:
        :return:
        """
        # TODO event not used
        self.response_check = False
        proposed_string = return_random_01_sequence(max_string_length)
        steps = random.randint(1,len(proposed_string))
        message = "O" + str(steps) + ",V" + proposed_string + "."
        self.set_message(message)
        self.response_string = rotate_sequence(steps,reverse_sequence(proposed_string))
        self._max_time = (8*len(message)) + (8*len(self.response_string)) - 8

    @on_output_message(r'\.$')
    def set_response_check(self, event):
        """

        :param event:
        :return:
        """
        # TODO event not used
        self.response_check = True
        self.response_counter = 0

    @on_message(r".$")
    def check_response(self, event):
        """

        :param event:
        :return:
        """
        if (self.response_check):
#            self.logger.info("current counter:" + str(self.response_counter))
            if (event.is_message(self.response_string[self.response_counter])):
                if (self.response_counter==(len(self.response_string)-1)):
                    self.set_reward(1)
                else:
                    self.response_counter = self.response_counter + 1
            else:
                self.set_reward(-1)
"""
     @on_timeout()
     def punish_slow_learner(self, event):
         self.set_reward(-1)
"""
class RotateRRepeatNXTask(BaseTask):
    def __init__(self, world=None):
        """ NB: max_time will be dynamically adjusted below
                self.logger = logging.getLogger(__name__)

        :param world:
        """
        super(RotateRRepeatNXTask, self).__init__(world=world, max_time=0)

    @on_start()
    def give_instructions(self, event):
        """

        :param event:
        :return:
        """
        # TODO event not used
        self.response_check = False
        proposed_string = return_random_01_sequence(max_string_length)
        repetitions = random.randint(1,4)
        steps = random.randint(1,len(proposed_string)*repetitions)
        message = "O" + str(steps) + ",P" + str(repetitions) + "," + proposed_string + "."
        self.set_message(message)
        self.response_string = rotate_sequence(steps,repeat_sequence(repetitions,proposed_string))
        self._max_time = (8*len(message)) + (8*len(self.response_string)) - 8

    @on_output_message(r'\.$')
    def set_response_check(self, event):
        # TODO event not used
        """

        :param event:
        :return:
        """
        self.response_check = True
        self.response_counter = 0

    @on_message(r".$")
    def check_response(self, event):
        """

        :param event:
        :return:
        """
        if (self.response_check):
             # self.logger.info("current counter:" + str(self.response_counter))
            if (event.is_message(self.response_string[self.response_counter])):
                if (self.response_counter==(len(self.response_string)-1)):
                    self.set_reward(1)
                else:
                    self.response_counter = self.response_counter + 1
            else:
                self.set_reward(-1)
"""
     @on_timeout()
     def punish_slow_learner(self, event):
         self.set_reward(-1)
"""
class RotateRConcatenateXYTask(BaseTask):
    def __init__(self, world=None):
        """ NB: max_time will be dynamically adjusted below
                self.logger = logging.getLogger(__name__)

        :param world:
        """
        super(RotateRConcatenateXYTask, self).__init__(world=world, max_time=0)

    @on_start()
    def give_instructions(self, event):
        # TODO event not used
        self.response_check = False
        proposed_string_1 = return_random_01_sequence(max_string_length)
        proposed_string_2 = return_random_01_sequence(max_string_length)
        steps = random.randint(1,len(proposed_string_1)+len(proposed_string_2))
        message = "O" + str(steps) + ",C" + proposed_string_1 + "," + proposed_string_2 + "."
        self.set_message(message)
        self.response_string = rotate_sequence(steps,proposed_string_1+proposed_string_2)
        self._max_time = (8*len(message)) + (8*len(self.response_string)) - 8

    @on_output_message(r'\.$')
    def set_response_check(self, event):
        """

        :param event:
        :return:
        """
        # TODO event not used
        self.response_check = True
        self.response_counter = 0

    @on_message(r".$")
    def check_response(self, event):
        """

        :param event:
        :return:
        """
        if (self.response_check):
            # self.logger.info("current counter:" + str(self.response_counter))
            if (event.is_message(self.response_string[self.response_counter])):
                if (self.response_counter==(len(self.response_string)-1)):
                    self.set_reward(1)
                else:
                    self.response_counter = self.response_counter + 1
            else:
                self.set_reward(-1)
"""
     @on_timeout()
     def punish_slow_learner(self, event):
         self.set_reward(-1)
"""
class ConcatenateReverseXReverseYTask(BaseTask):
    def __init__(self, world=None):
        """  NB: max_time will be dynamically adjusted below
                 self.logger = logging.getLogger(__name__)

        :param world:
        """
        super(ConcatenateReverseXReverseYTask, self).__init__(world=world, max_time=0)

    @on_start()
    def give_instructions(self, event):
        """

        :param event:
        :return:
        """
        # TODO event not used
        self.response_check = False
        proposed_string_1 = return_random_01_sequence(max_string_length)
        proposed_string_2 = return_random_01_sequence(max_string_length)
        message = "CV" + proposed_string_1 + ",V" + proposed_string_2 + "."
        self.set_message(message)
        self.response_string = reverse_sequence(proposed_string_1) + reverse_sequence(proposed_string_2)
        self._max_time = (8*len(message)) + (8*len(self.response_string)) - 8

    @on_output_message(r'\.$')
    def set_response_check(self, event):
        """

        :param event:
        :return:
        """
        # TODO event not used
        self.response_check = True
        self.response_counter = 0

    @on_message(r".$")
    def check_response(self, event):
        """

        :param event:
        :return:
        """
        # TODO event not used
        if (self.response_check):
            # self.logger.info("current counter:" + str(self.response_counter))
            if (event.is_message(self.response_string[self.response_counter])):
                if (self.response_counter==(len(self.response_string)-1)):
                    self.set_reward(1)
                else:
                    self.response_counter = self.response_counter + 1
            else:
                self.set_reward(-1)
"""
     @on_timeout()
     def punish_slow_learner(self, event):
         self.set_reward(-1)
"""
class ConcatenateRepeatNXRepeatMYTask(BaseTask):
    """

    """
    def __init__(self, world=None):
        """ NB: max_time will be dynamically adjusted below
                self.logger = logging.getLogger(__name__)
        :param world:
        """
        super(ConcatenateRepeatNXRepeatMYTask, self).__init__(world=world, max_time=0)

    @on_start()
    def give_instructions(self, event):
        """

        :param event:
        :return:
        """
        # TODO event not used
        self.response_check = False
        proposed_string_1 = return_random_01_sequence(max_string_length)
        repetitions_1 = random.randint(1,4)
        proposed_string_2 = return_random_01_sequence(max_string_length)
        repetitions_2 = random.randint(1,4)
        message = "CP" + str(repetitions_1) + "," + proposed_string_1 + ",P" + str(repetitions_2) + ","\
                   + proposed_string_2 + "."
        self.set_message(message)
        self.response_string = repeat_sequence(repetitions_1, proposed_string_1) + repeat_sequence(repetitions_2,
                                                                                                   proposed_string_2)
        self._max_time = (8*len(message)) + (8*len(self.response_string)) - 8

    @on_output_message(r'\.$')
    def set_response_check(self, event):
        """

        :param event:
        :return:
        """
        # TODO event not used
        self.response_check = True
        self.response_counter = 0

    @on_message(r".$")
    def check_response(self, event):
        """

        :param event:
        :return:
        """
        if (self.response_check):
#            self.logger.info("current counter:" + str(self.response_counter))
            if (event.is_message(self.response_string[self.response_counter])):
                if (self.response_counter==(len(self.response_string)-1)):
                    self.set_reward(1)
                else:
                    self.response_counter = self.response_counter + 1
            else:
                self.set_reward(-1)
"""
     @on_timeout()
     def punish_slow_learner(self, event):
         self.set_reward(-1)
"""

class ConcatenateRotateRXRotateSYTask(BaseTask):
    """

    """
    def __init__(self, world=None):
        """ NB: max_time will be dynamically adjusted below
                self.logger = logging.getLogger(__name__)
        :param world:
        """
        super(ConcatenateRotateRXRotateSYTask, self).__init__(world=world, max_time=0)

    @on_start()
    def give_instructions(self, event):
        # TODO event not used
        """

        :param event:
        :return:
        """
        self.response_check = False
        proposed_string_1 = return_random_01_sequence(max_string_length)
        steps_1 = random.randint(1,len(proposed_string_1))
        proposed_string_2 = return_random_01_sequence(max_string_length)
        steps_2 = random.randint(1,len(proposed_string_2))
        message = "CO" + str(steps_1) + "," + proposed_string_1 + ",O" + str(steps_2) + "," + proposed_string_2 + "."
        self.set_message(message)
        self.response_string = rotate_sequence(steps_1, proposed_string_1) + rotate_sequence(steps_2,proposed_string_2)
        self._max_time = (8*len(message)) + (8*len(self.response_string)) - 8

    @on_output_message(r'\.$')
    def set_response_check(self, event):
        """

        :param event:
        :return:
        """
        # TODO event not used
        self.response_check = True
        self.response_counter = 0

    @on_message(r".$")
    def check_response(self, event):
        """

        :param event:
        :return:
        """
        if (self.response_check):
            # self.logger.info("current counter:" + str(self.response_counter))
            if (event.is_message(self.response_string[self.response_counter])):
                if (self.response_counter==(len(self.response_string)-1)):
                    self.set_reward(1)
                else:
                    self.response_counter = self.response_counter + 1
            else:
                self.set_reward(-1)
"""
     @on_timeout()
     def punish_slow_learner(self, event):
         self.set_reward(-1)
"""