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

# TODO resovle imports
from core.channels import InputChannel, OutputChannel
from learners.base import BaseLearner
import logging
import re


class HumanLearner(BaseLearner):
    def __init__(self, serializer):
        """ Takes the serialization protocol

        :param serializer:
        """
        self._serializer = serializer
        self._input_channel = InputChannel(serializer)
        self._output_channel = OutputChannel(serializer)
        self._input_channel.message_updated.register(self.on_message)
        self.logger = logging.getLogger(__name__)
        self.speaking = False

    def reward(self, reward):
        """

        :param reward:
        :return:
        """
        self.logger.info("Reward received: {0}".format(reward))
        self._input_channel.clear()
        self._output_channel.clear()

    def next(self, user_input):
        """ If the buffer is empty, fill it with silence

        :param user_input:
        :return:
        """
        if self._output_channel.is_empty():
            self.logger.debug("Output buffer is empty, filling with silence")
            self._output_channel.set_message(self._serializer.SILENCE_TOKEN)  # Add 1 silence token to buffer
        output = self._output_channel.consume_bit()  # Get the bit to return
        self._input_channel.consume_bit(user_input)  # Interpret the bit from the learner
        return output

    def on_message(self, message):
        """ we ask for input on two consecutive silences

        :param message:
        :return:
        """
        if message[-2:] == self._serializer.SILENCE_TOKEN * 2 and self._output_channel.is_empty() and not self.speaking:
            self.ask_for_input()
        elif self._output_channel.is_empty():
            self.speaking = False # If speaking, changes to speaking off

    def ask_for_input(self):
        """

        :return:
        """
        output = self._view.get_input()
        self.logger.debug("Received input from the human: '{0}'".format(output))
        if output:
            self.speaking = True
            output = re.compile('\.+').sub('.', output)
            self._output_channel.set_message(output)


class ManualHumanLearner(HumanLearner):
    """

    """
    def __init__(self, serializer):
        """

        :param serializer:
        """
        super(ManualHumanLearner, self).__init__(serializer)

    def next(self, user_input):
        """ If the buffer is empty, ask for what to do

        :param user_input:
        :return:
        """
        while self._output_channel.is_empty():
            self.ask_for_input()
        return super(ManualHumanLearner, self).next(user_input)
