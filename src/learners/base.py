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


import subprocess


class BaseLearner(object):
    """

    """
    def try_reward(self, reward):
        """

        :param reward:
        """
        if reward is not None:
            self.reward(reward)

# TODO static function
    def reward(self, reward):
        """ YEAH! Reward!!! Whatever...

        :param reward:
        """
        pass

    def next(self, user_input):
        """ do super fancy computations return our guess

        :param user_input:
        :return:
        """
        return user_input


class RemoteLearner(BaseLearner):
    def __init__(self, cmd, port):
        """

        :param cmd:
        :param port:
        """
        try:
            import zmq
        except ImportError:
            raise ImportError("Must have zeromq for remote learner.")

        self.port = port if port is not None else 5556
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PAIR)
        self.socket.bind("tcp://*:%s" % port)

        # launch learner
        subprocess.Popen((cmd + ' ' + str(self.port)).split())
        handshake_in = self.socket.recv()
        assert handshake_in == 'hello'  # handshake

    def next(self, inp):
        """ send to learner, and get response;

        :param inp:
        :return:
        """
        self.socket.send(str(inp))
        reply = self.socket.recv()
        return reply

    def try_reward(self, reward):
        """

        :param reward:
        """
        reward = reward if reward is not None else 0
        self.socket.send(str(reward))
