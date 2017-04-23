#!/usr/bin/env python3
#
# Copyright (c) 2017-, Stephen B. Hope
# All rights reserved.
#
# CommAI-env source files, Copyright (c) 2016-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the# LICENSE file in the root directory of this
# source tree. An additional grant of patent rights can be found in the PATENTS file in the same directory.

from core.task import Task, on_message


class BaseTask(Task):
    """
    Base task for other tasks in the competition implementing behaviour that should be shared by most of the tasks.
    """
    def __init__(self, *args, **kwargs):
        """

        :param args:
        :param kwargs:
        """
        super(BaseTask, self).__init__(*args, **kwargs)

    @on_message()
    def on_any_message(self, event):
        """ ignore anything the learner says while the teacher is speaking if the environment is speaking

        :param event:
        :return:
        """
        if not self._env.is_silent():
            # and the last message was not a silence
            if event.message[-1] != ' ':
                # i will ignore what the learner just said by forgetting it
                self.ignore_last_char()

    def deinit(self):
        """ send out a silence to separate tasks if needed

        :return:
        """
        silence = self.get_default_output()
        output_text = self._env._output_channel_listener.get_text()
        task_separator_issued = output_text.endswith(silence)
        if not task_separator_issued:
            self.add_message(silence)
