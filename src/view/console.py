#!/usr/bin/env python3
#
# Copyright (c) 2017-, Stephen B. Hope
# All rights reserved.
#
# CommAI-env source files, Copyright (c) 2016-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the LICENSE.md file in the root directory of this
# source tree. An additional grant of patent rights can be found in the PATENTS file in the same directory.

# TODO fix revised_core.channels import
import curses
import curses.textpad
import logging
import locale
from revised_core.channels import InputChannel

locale.setlocale(locale.LC_ALL, '')
code = locale.getpreferredencoding()


class BaseView(object):
    """ observe basic high level information about the session and environment

    """

    def __init__(self, env, session):
        """Observe basic high level information about session and  env,  Save information for display later

        :param env:
        :param session:
        """
        # TODO: Move environment and session outside of the class
        self._env = env
        self._session = session
        env.task_updated.register(self.on_task_updated)
        session.total_reward_updated.register(self.on_total_reward_updated)
        session.total_time_updated.register(self.on_total_time_updated)
        self.logger = logging.getLogger(__name__)
        self.info = {'reward': 0, 'time': 0, 'current_task': 'None'}

    def on_total_reward_updated(self, reward):
        """

        :param reward:
        :return:
        """
        self.info['reward'] = reward
        self.paint_info_win()

    def on_total_time_updated(self, time):
        """

        :param time:
        :return:
        """
        self.info['time'] = time
        self.paint_info_win()
        self._stdscr.nodelay(1)
        key = self._stdscr.getch()
        if key == ord('+'):
            self._session.add_sleep(-0.001)
        elif key == ord('-'):
            self._session.add_sleep(0.001)
        if key == ord('0'):
            self._session.reset_sleep()

    def on_task_updated(self, task):
        """

        :param task:
        :return:
        """
        if 'current_task' in self.info:
            self.info['current_task'] = task.get_name()
            self.paint_info_win()

    def paint_info_win(self):
        """

        :return:
        """
        self._info_win.addstr(0, 0, 'Total time: {0}'.format(self.info['time']))
        self._info_win.clrtobot()
        self._info_win.addstr(1, 0, 'Total reward: {0}'.format(self.info['reward']))
        self._info_win.clrtobot()
        if 'current_task' in self.info:
            self._info_win.addstr(2, 0, 'Current Task: {0}'.format(self.info['current_task']))
            self._info_win.clrtobot()
        self._info_win.refresh()

    def initialize(self):
        """ initialize curses. self._info_win_width = 20.  create info box with reward and time.

        :return:
        """
        self._stdscr = curses.initscr()
        # TODO generalize this
        # TODO _info_win_height, height width, _win, _info_win def outside __init__
        begin_x = 0
        begin_y = 0
        self._info_win_height = 4
        self.height, self.width = self._stdscr.getmaxyx()
        self._win = self._stdscr.subwin(self.height, self.width, begin_y, begin_x)
        self._info_win = self._win.subwin(self._info_win_height, self.width, 0, 0)
        curses.noecho()
        curses.cbreak()

    def finalize(self):
        # TODO static
        """

        :return:
        """
        curses.nocbreak()
        curses.echo()
        curses.endwin()


class ConsoleView(BaseView):
    """

    """

    def __init__(self, env, session, serializer, show_world=False):
        """ for visualization purposes, we keep an internal buffer of the input and output stream so when they are
        cleared from task to task, we can keep the history intact. Record what learner says.  Record what environment
        says.  Listen to updates.  Register a handle to plot world if show_world active.  Connect channe;s with
        observed input bits.

        :param env:
        :param session:
        :param serializer:
        :param show_world:
        """
        super(ConsoleView, self).__init__(env, session)
        self.input_buffer = ''
        self.output_buffer = ''
        self.panic = 'SKIP'
        self._learner_channel = InputChannel(serializer)
        self._env_channel = InputChannel(serializer)
        self._learner_channel.sequence_updated.register(self.on_learner_sequence_updated)
        self._learner_channel.message_updated.register(self.on_learner_message_updated)
        self._env_channel.sequence_updated.register(self.on_env_sequence_updated)
        self._env_channel.message_updated.register(self.on_env_message_updated)
        if show_world:
            env.world_updated.register(self.on_world_updated)
        session.env_token_updated.register(self.on_env_token_updated)
        session.learner_token_updated.register(self.on_learner_token_updated)
        del self.info['current_task']

    def on_env_token_updated(self, token):
        """

        :param token:
        :return:
        """
        self._env_channel.consume_bit(token)

    def on_learner_token_updated(self, token):
        """

        :param token:
        :return:
        """
        self._learner_channel.consume_bit(token)

    def on_learner_message_updated(self, message):
        # TODO message not used
        """ we use the fact that messages arrive character by character

        :param message:
        :return:
        """
        if self._learner_channel.get_text():
            self.input_buffer += self._learner_channel.get_text()[-1]
            self.input_buffer = self.input_buffer[-self._scroll_msg_length:]
            learner_input = self.channel_to_str(self.input_buffer, self._learner_channel.get_undeserialized())
            self._win.addstr(self._learner_seq_y, 0, learner_input.encode(code))
            self._win.refresh()

    def on_learner_sequence_updated(self, sequence):
        # TODO sequence not used
        """

        :param sequence:
        :return:
        """
        learner_input = self.channel_to_str(self.input_buffer, self._learner_channel.get_undeserialized())
        self._win.addstr(self._learner_seq_y, 0, learner_input.encode(code))
        self._win.refresh()

    def on_env_message_updated(self, message):
        # TODO message not used
        """

        :param message:
        :return:
        """
        if self._env_channel.get_text():
            self.output_buffer += self._env_channel.get_text()[-1]
            self.output_buffer = self.output_buffer[-self._scroll_msg_length:]
            env_output = self.channel_to_str(self.output_buffer, self._env_channel.get_undeserialized())
            self._win.addstr(self._teacher_seq_y, 0, env_output.encode(code))
            self._win.refresh()

    def on_env_sequence_updated(self, sequence):
        # TODO sequence not used
        """

        :param sequence:
        :return:
        """
        env_output = self.channel_to_str(self.output_buffer, self._env_channel.get_undeserialized())
        self._win.addstr(self._teacher_seq_y, 0, env_output.encode(code))
        self._win.refresh()

    def on_world_updated(self, world):
        """

        :param world:
        :return:
        """
        if world:
            world.state_updated.register(self.on_world_state_updated)
            self._worldwin.addstr(0, 0, str(world))
            self._worldwin.refresh()
        else:
            self._worldwin.clear()
        self._worldwin.refresh()

    def on_world_state_updated(self, world):
        """

        :param world:
        :return:
        """
        self._worldwin.addstr(0, 0, str(world))
        self._worldwin.refresh()

    def initialize(self):
        """ initialize curses, create info box with reward and time

        :return:
        """
        # TODO _stdscr, _teascher_seq_y, _learner_seq_y, _world_win_y, _world_win_x, _info_win_width,
        # TODO line 2 _info_win_height, _user_input_win_y, _user_input_win_x, height, _scroll_msg_length,
        # TODO line 3 _win, _worldwin, _info_win, _user_input_win, _user_input_label_win defined outside __init__
        self._stdscr = curses.initscr()
        begin_x = 0
        begin_y = 0
        self._teacher_seq_y = 0
        self._learner_seq_y = 1
        self._world_win_y = 3
        self._world_win_x = 0
        self._info_win_width = 20
        self._info_win_height = 2
        self._user_input_win_y = 2
        self._user_input_win_x = 10
        self.height, self.width = self._stdscr.getmaxyx()
        self._scroll_msg_length = self.width - self._info_win_width - 1
        self._win = self._stdscr.subwin(self.height, self.width, begin_y, begin_x)
        self._worldwin = self._win.subwin(self.height - self._world_win_y, self.width - self._world_win_x,
                                          self._world_win_y, self._world_win_x)
        self._info_win = self._win.subwin(self._info_win_height, self._info_win_width, 0,
                                          self.width - self._info_win_width)
        self._user_input_win = self._win.subwin(1, self.width - self._user_input_win_x, self._user_input_win_y,
                                                self._user_input_win_x)
        self._user_input_label_win = self._win.subwin(1, self._user_input_win_x - 1, self._user_input_win_y, 0)
        curses.noecho()
        curses.cbreak()

    def get_input(self):
        """

        :return:
        """
        self._user_input_label_win.addstr(0, 0, 'input:')
        self._user_input_label_win.refresh()
        curses.echo()
        user_input = self._user_input_win.getstr(0, 0, self.width - self._user_input_win_x).decode(code)
        curses.noecho()
        self._user_input_win.clear()
        if user_input == self.panic:
            user_input = ''
            self._env._task_time = float('inf')
        return user_input

    def channel_to_str(self, text, bits):
        """

        :param text:
        :param bits:
        :return:
        """
        length = self._scroll_msg_length - 10
        return "{0:_>{length}}[{1: <8}]".format(text[-length:], bits[-7:], length=length)


class PlainView(object):
    """

    """

    def __init__(self, env, session):
        """ observe basic high level information about the session and environment.  Save information for display.

        :param env:
        :param session:
        """
        # TODO: Move environment and session outside of the class
        self._env = env
        self._session = session
        env.task_updated.register(self.on_task_updated)
        session.total_reward_updated.register(self.on_total_reward_updated)
        session.total_time_updated.register(self.on_total_time_updated)
        self.logger = logging.getLogger(__name__)
        self.info = {'reward': 0, 'time': 0, 'current_task': 'None'}

    def on_total_reward_updated(self, reward):
        """

        :param reward:
        :return:
        """
        self.info['reward'] = reward
        print('reward', reward)

    def on_total_time_updated(self, time):
        """

        :param time:
        :return:
        """
        self.info['time'] = time

    def on_task_updated(self, task):
        """

        :param task:
        :return:
        """
        if 'current_task' in self.info:
            self.info['current_task'] = task.get_name()
            print('\n', task.get_name())

    def paint_info_win(self):
        # TODO static function
        """

        :return:
        """
        return

    def initialize(self):
        # TODO static function
        """

        :return:
        """
        return

    def finalize(self):
        # TODO static function
        """

        :return:
        """
        return
