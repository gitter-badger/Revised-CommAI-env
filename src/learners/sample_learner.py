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

# TODO ix imports revised_core, learners
from revised_core.serializer import StandardSerializer, IdentitySerializer
from learners.base import BaseLearner


class SampleRepeatingLearner(BaseLearner):
    """

    """

    def reward(self, reward):
        # TODO static func
        """ YEAH! Reward!!! Whatever...

        :param reward:
        """
        pass

    def next(self, user_input):
        # TODO static function
        """

        :param user_input:
        :return:
        do super fancy computations return our guess
        """
        return user_input


class SampleSilentLearner(BaseLearner):
    """

    """
    def __init__(self):
        """

        """
        self.serializer = StandardSerializer()
        self.silence_code = self.serializer.to_binary(' ')
        self.silence_i = 0

    def reward(self, reward):
        # TODO attr reward not used
        """ YEAH! Reward!!! Whatever...

        :param reward:
        :return:
        """
        self.silence_i = 0

    def next(self, user_input):
        # TODO attr user_input not used
        """

        :param user_input:
        :return:
        """
        output = self.silence_code[self.silence_i]
        self.silence_i = (self.silence_i + 1) % len(self.silence_code)
        return output


class SampleMemorizingLearner(BaseLearner):
    """

    """
    def __init__(self):
        """ Learner has serialized 'hardcoded' to detect spaces

        """
        self.memory = ''
        self.teacher_stopped_talking = False
        self.serializer = StandardSerializer()
        self.silence_code = self.serializer.to_binary(' ')
        self.silence_i = 0

    def reward(self, reward):
        # TODO attr reward not used
        """ YEAH! Reward!!! Whatever Now this robotic teacher is going to mumble things again...

        :param reward:
        :return:
        """
        self.teacher_stopped_talking = False
        self.silence_i = 0
        self.memory = ''

    def next(self, user_input):
        # TODO attr user_input not used
        """ If we have received a silence byte.  send the memorized sequence.  Memorize what the teacher said

        :param:
        :return:
        """
        text_input = self.serializer.to_text(self.memory)
        if text_input and text_input[-2:] == '  ':
            self.teacher_stopped_talking = True
        if self.teacher_stopped_talking:
            output, self.memory = self.memory[0], self.memory[1:]
        else:
            output = self.silence_code[self.silence_i]
            self.silence_i = (self.silence_i + 1) % len(self.silence_code)
        self.memory += input
        return output
