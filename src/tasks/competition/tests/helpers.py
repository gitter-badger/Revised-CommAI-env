#!/usr/bin/env python3
#
# Copyright (c) 2017-, Stephen B. Hope
# All rights reserved.
#
# CommAI-env source files, Copyright (c) 2016-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the# LICENSE.md file in the root directory of this
# source tree. An additional grant of patent rights can be found in the PATENTS file in the same directory.

# TODO fix imports
import core.environment as environment
import core.serializer as serializer
import core.channels as channels
import contextlib
import re


class EnvironmentMessenger:
    """

    """
    def __init__(self, env, serializer):
        """

        :param env:
        :param serializer:
        """
        self._env = env
        self._serializer = serializer
        self._input_channel = channels.InputChannel(serializer)
        self._output_channel = channels.OutputChannel(serializer)
        self.cum_reward = 0
        self.init()

    def init(self):
        """ Kick-starts the environment

        :return:
        """
        first_bit, reward = self._env.next(None)
        self._input_channel.consume_bit(first_bit)

    def is_silent(self):
        """

        :return:
        """
        # TODO access protected member outside of class
        return self._env._output_channel.is_silent()

    def read(self):
        """ Sends silence until the teacher has stopped speaking. Keep on putting silence in the output channel

        :return:
        """
        nbits = 0
        while not self.is_silent():
            nbits += self.send(self._serializer.SILENCE_TOKEN)
        return nbits

    def read_until(self, condition):
        """ Sends silence until a given condition holds true. Keep on putting silence in the output channel

        :param condition: a function that takes an EnvironmentMessenger
        :return:
        """
        def safe_condition_eval():
            """ wrap the condition to catch exceptions

            :return:
            """
            try:
                return condition(self)
            # TODO To broad, will never trigger
            except BaseException:
                return False
        nbits = 0
        while not self.is_silent() and not safe_condition_eval():
            nbits += self.send(self._serializer.SILENCE_TOKEN)
        return nbits

    def send(self, msg=None):
        """ default message is a silence, puts the message in the output channel. send every bit in it. send/receive a
        bit and reward. save the bit. save the reward. a reward marks the end of a task for now, so clear the buffers

        :param msg:
        :return:
        """
        if msg is None:
            msg = self._serializer.SILENCE_TOKEN
        nbits = 0
        self._output_channel.set_message(msg)
        while not self._output_channel.is_empty():
            env_bit, reward = self._env.next(self._output_channel.consume_bit())
            self._input_channel.consume_bit(env_bit)
            if reward is not None:
                self.cum_reward += reward
            nbits += 1
        return nbits

    def get_full_message(self):
        """

        :return:
        """
        return self._input_channel.get_text()

    def get_last_message(self, n_silence=2):
        """ Returns the last message sent by the teacher. The message is delimited between the end of the input
        stream and the point after n_silence silent tokens where issued. get the input text remove the trailing
        silences find the point where the last message started (after at least n_silence tokens)

        :param n_silence:
        :return:
        """
        input_text = self._input_channel.get_text()
        input_text = input_text.rstrip(self._serializer.SILENCE_TOKEN)
        last_silence = input_text.rfind(self._serializer.SILENCE_TOKEN * n_silence)
        if last_silence == -1:
            return input_text
        else:
            return input_text[last_silence + n_silence:]

    def search_on(self, message, pattern):
        # TODO method may be static
        """

        :param message:
        :param pattern:
        :return:
        """
        match = re.search(pattern, message)
        if match is None:
            raise RuntimeError("'{0}' did not find any match on '{1}'".format(pattern, message))
        return match.groups()

    def search_last_message(self, pattern):
        """

        :param pattern:
        :return:
        """
        message = self.get_last_message()
        return self.search_on(message, pattern)

    def search_full_message(self, pattern):
        """

        :param pattern:
        :return:
        """
        message = self.get_full_message()
        return self.search_on(message, pattern)

    def get_cumulative_reward(self):
        """

        :return:
        """
        return self.cum_reward

    def get_time(self):
        """

        :return:
        """
        # TODO access protected member
        return self._env._task_time


class SingleTaskScheduler:
    """

    """
    def __init__(self, task):
        self.task = task

    def get_next_task(self):
        return self.task

    def reward(self, reward):
        pass


@contextlib.contextmanager
def task_messenger(task_funct, world_funct=None, serializer=serializer.StandardSerializer()):
    """ Returns an EnvironmentMessenger to interact with the created task.

    :param task_funct: takes an environment (optionally a world) and returns a task object.
    :param world_funct: takes an environment and returns a world object.
    :param serializer:
    :return:
    """
    if world_funct:
        world = world_funct()
        task = task_funct(world)
    else:
        task = task_funct()
    scheduler = SingleTaskScheduler(task)
    env = environment.Environment(serializer, scheduler)
    m = EnvironmentMessenger(env, serializer)
    yield m
