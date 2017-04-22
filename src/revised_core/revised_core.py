#!/usr/bin/env python3
#
# Copyright (c) 2017-, Stephen B. Hope
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.


class InputChannel:
    """

    """

    def __init__(self, serializer):
        """
        :param serializer:
        """
        self.serializer = serializer
        # remembers the input in binary format
        self._binary_buffer = ''
        # leftmost deserialization of the binary buffer
        self._deserialized_buffer = ''
        # remember the position until which we deserialized the binary buffer
        self._deserialized_pos = 0

        # event that gets fired for every new bit
        self.sequence_updated = Observable()
        # event that gets fired for every new character
        self.message_updated = Observable()

    def consume_bit(self, input_bit):
        """ Takes a bit into the channel, for now we are storing the input as strings (let's change this later)

        :param input_bit:
        :return:

        """
        if input_bit == 0 or input_bit == 1:
            input_bit = str(input_bit)
        # store the bit in the binary input buffer
        self._binary_buffer += input_bit
        # notify the updated sequence
        self.sequence_updated(self._binary_buffer)

        # we check if we can deserialize the final part of the sequence
        undeserialized_part = self.get_undeserialized()
        if self.serializer.can_deserialize(undeserialized_part):
            # when we do, we deserialize the chunk
            self._deserialized_buffer += \
                self.serializer.to_text(undeserialized_part)
            # we update the position
            self._deserialized_pos += len(undeserialized_part)

            self.message_updated(self._deserialized_buffer)

    def clear(self):
        """ Clears all the  buffers

        :return:

        """
        self._set_deserialized_buffer('')
        self._set_binary_buffer('')
        self._deserialized_pos = 0
        return

    def get_binary(self):
        """

        :return:
                   self._binary_buffer
        """
        return self._binary_buffer

    def set_deserialized_buffer(self, new_buffer):
        """ Replaces the deserialized part of the buffer.

        :param new_buffer:
        :return:
        """
        self._deserialized_buffer = new_buffer

    def get_undeserialized(self):
        """ Returns the yet non deserialized chunk in the input

        :return:
                 self._binary_buffer[self._deserialized_pos:]
        """
        return self._binary_buffer[self._deserialized_pos:]

    def get_text(self):
        """ Carefully raise the event only if the buffer has actually changed

        :return:
        """
        return self._deserialized_buffer

    def _set_binary_buffer(self, new_buffer):
        """

        :param new_buffer:
        :return:
        """
        if self._binary_buffer != new_buffer:
            self._binary_buffer = new_buffer
            self.sequence_updated(self._binary_buffer)

    def _set_deserialized_buffer(self, new_buffer):
        """ Carefully raise the event only if the buffer has actually changed

        :param new_buffer:
        :return:
        """
        if self._deserialized_buffer != new_buffer:
            self._deserialized_buffer = new_buffer
            self.message_updated(self._deserialized_buffer)


class OutputChannel:
    """

    """

    def __init__(self, serializer):
        """

        :param serializer:
        """
        self.serializer = serializer
        # remembers the data that has to be shipped out
        self._binary_buffer = ''
        # event that gets fired every time we change the output sequence
        self.sequence_updated = Observable()
        self.logger = logging.getLogger(__name__)

    def set_message(self, message):
        """

        :param message:
        :return:
        """
        new_binary = self.serializer.to_binary(message)
        # find the first available point from where we can insert
        # the new buffer without breaking the encoding
        insert_point = len(self._binary_buffer)
        for i in range(len(self._binary_buffer)):
            # if we can decode from insert_point on, we can replace
            # that information with the new buffer
            if self.serializer.to_text(self._binary_buffer[i:]):
                insert_point = i
                break
        if insert_point > 0:
            self.logger.debug("Inserting new contents at {0}".format(insert_point))
        self._set_buffer(self._binary_buffer[:insert_point] + new_binary)

    def add_message(self, message):
        """

        :param message:
        :return:
        """
        new_binary = self.serializer.to_binary(message)
        # append the binary encoding to the end of the current buffer
        self._set_buffer(self._binary_buffer + new_binary)

    def clear(self):
        """

        :return:
        """
        self._set_buffer('')

    def _set_buffer(self, new_buffer):
        """ Carefully raise the event only if the buffer has actually changed

        :param new_buffer:
        :return:
        """
        if self._binary_buffer != new_buffer:
            self._binary_buffer = new_buffer
            self.sequence_updated(self._binary_buffer)

    def consume_bit(self):
        """

        :return:
        """
        if len(self._binary_buffer) > 0:
            output, new_buffer = self._binary_buffer[0], self._binary_buffer[1:]
            self._set_buffer(new_buffer)
            return output

    def is_empty(self):
        """

        :return:
        """
        return len(self._binary_buffer) == 0

    def is_silent(self):
        """ Sll the bits in the output token are the result of serializing silence tokens

        :return:
        """
        buf = self._binary_buffer
        silent_bits = self.serializer.to_binary(self.serializer.SILENCE_TOKEN)
        token_size = len(silent_bits)
        while len(buf) > token_size:
            buf_suffix, buf = buf[-token_size:], buf[:-token_size]
            if buf_suffix != silent_bits:
                return False
        return len(buf) == 0 or buf == silent_bits[-len(buf):]



class JSONConfigLoader:
    """
    Loads a set of tasks and a schedule for them from a JSON file::

        {
          "tasks":
          {
            "<task_id>": {
                "type": "<task_class>",
            },
            "<task_id>": {
                "type": "<task_class>",
                "world": "<world_id>"
            }
            "...": "..."
          },
          "worlds":
          {
            "<world_id>": {
              "type": "<world_class>",
            }
          },
          "scheduler":
            {
              "type": "<scheduler_class>",
              "args": {
                  "<scheduler_arg>": <scheduler_arg_value>,
                }
            }
        }

    The scheduler scheduler_arg_value could be a container including
    task ids, which will be replaced by the concrete tasks instances.
    """
    def create_tasks(self, tasks_config_file):
        """ Given a json configuration file, it returns a scheduler object set up as described in the file.

        :param tasks_config_file:
        :return:
        """
        config = json.load(open(tasks_config_file))
        # instantiate the worlds (typically there is only one)
        worlds = dict((world_id, self.instantiate_world(world_config['type']))
                      for world_id, world_config in config['worlds'].items())
        # map each task
        # instantiate the tasks with the world (if any)
        tasks = dict((task_id, self.instantiate_task(task_config['type'], worlds, task_config.get('world', None)))
                     for task_id, task_config in config['tasks'].items())
        # retrieve what type of scheduler we need to create
        scheduler_class = get_class(config['scheduler']['type'])
        # prepare the arguments to instantiate the scheduler
        scheduler_args = {}
        for arg_name, arg_value in config['scheduler']['args'].items():
            # all arguments that begin with the name tasks are taken as
            # collections of ids that should be mapped to the corresponding
            # tasks object
            if arg_name.startswith('tasks'):
                scheduler_args[arg_name] = map_tasks(arg_value, tasks)
            else:
                scheduler_args[arg_name] = arg_value
        # return a scheduler with its corresponding arguments
        return scheduler_class(**scheduler_args)

    def instantiate_world(self, world_class):
        """ Return a world object given the world class

        :param world_class:
        :return:
        """
        c = get_class(world_class)
        try:
            return c()
        except Exception as e:
            raise RuntimeError("Failed to instantiate world {0} ({1})".format(world_class, e))

    def instantiate_task(self, task_class, worlds, world_id=None):
        """ Returns a task object given the task class and the world where it runs (if any)

        :param task_class:
        :param worlds:
        :param world_id:
        :return:
        """
        c = get_class(task_class)
        try:
            if world_id:
                return c(worlds[world_id])
            else:
                return c()
        except Exception as e:
            raise RuntimeError("Failed to instantiate task {0} ({1})".format(task_class, e))


class PythonConfigLoader:
    """
    Loads a python file containing a stand-alone function called`create_tasks` that returns a TaskScheduler object.
    """
    def create_tasks(self, tasks_config_file):
        """ make sure we have a relative path

        :param tasks_config_file:
        :return:
        """
        tasks_config_file = os.path.relpath(tasks_config_file)
        if tasks_config_file.startswith('..'):
            raise RuntimeError("The task configuration file must be in the "
                               "same directory as the competition source.")
        # just in case, remove initial unneeded "./"
        if tasks_config_file.startswith('./'):
            tasks_config_file = tasks_config_file[2:]
        # transform the config file path into a module path
        tasks_config_module = os.path.splitext(tasks_config_file)[0].replace('/', '.')
        mod = __import__(tasks_config_module, fromlist=[''])
        return mod.create_tasks()


def get_class(name):
    """

    :param name:
    :return:
    """
    components = name.split('.')
    mod = __import__('.'.join(components[:-1]), fromlist=[components[-1]])
    mod = getattr(mod, components[-1])
    return mod


def map_tasks(arg, tasks):
    """

    :param arg:
    :param tasks:
    :return:
    """
    try:
        # if arg is a task, return the task object
        return tasks[arg]
    except KeyError:
        # arg is a hashable type, but we cannot map it to a task
        raise RuntimeError("Coudln't find task id '{0}'.".format(arg))
    # unhashable type
    except TypeError:
        # we treat arg as a collection that should be mapped
        return list(map(lambda x: map_tasks(x, tasks), arg))


class Environment:
    """ The Environment is the one that communicates with the Learner, interpreting its output and reacting to it.
    The interaction is governed by an ongoing task which is picked by a TaskScheduler object.

        :param serializer: a Serializer object that translates text into binary and back.

        :param task_scheduler: a TaskScheduler object that determines which task is going to be run next.

        :param scramble: if True, the words outputted by the tasks are randomly scrambled.

        :param max_reward_per_task: maximum amount of reward that a learner can receive for a given task.
    """
    def __init__(self, serializer, task_scheduler, scramble=False,
                 max_reward_per_task=10):
        """ save parameters into member variables

        :param serializer:
        :param task_scheduler:
        :param scramble:
        :param max_reward_per_task:
        """
        self._task_scheduler = task_scheduler
        self._serializer = serializer
        self._max_reward_per_task = max_reward_per_task
        # cumulative reward per task
        self._reward_per_task = defaultdict(int)
        # the event manager is the controller that dispatches
        # changes in the environment (like new inputs or state changes)
        # to handler functions in the tasks that tell the environment
        # how to react
        self.event_manager = EventManager()
        # intialize member variables
        self._current_task = None
        self._current_world = None
        # we hear to our own output
        self._output_channel_listener = InputChannel(serializer)
        if scramble:
            serializer = ScramblingSerializerWrapper(serializer)
        # output channel
        self._output_channel = OutputChannel(serializer)
        # input channel
        self._input_channel = InputChannel(serializer)
        # priority of ongoing message
        self._output_priority = 0
        # reward that is to be given at the learner at the end of the task
        self._reward = None
        # Current task time
        self._task_time = None
        # Task deinitialized
        self._current_task_deinitialized = False
        # Internal logger
        self.logger = logging.getLogger(__name__)

        # signals
        self.world_updated = Observable()
        self.task_updated = Observable()
        self.reward_given = Observable()

        # Register channel observers
        self._input_channel.sequence_updated.register(
                self._on_input_sequence_updated)
        self._input_channel.message_updated.register(
                self._on_input_message_updated)
        self._output_channel_listener.sequence_updated.register(
                self._on_output_sequence_updated)
        self._output_channel_listener.message_updated.register(
                self._on_output_message_updated)

    def next(self, learner_input):
        '''Main loop of the Environment. Receives one bit from the learner and
        produces a response (also one bit)'''
        # Make sure we have a task
        if not self._current_task:
            self._switch_new_task()
        # If the task has not reached the end by either Timeout or
        # achieving the goal
        if not self._current_task.has_ended():
            # Check if a Timeout occurred
            self._current_task.check_timeout(self._task_time)
            # Process the input from the learner and raise events
            if learner_input is not None:
                # record the input from the learner and deserialize it
                # TODO this bit is dropped otherwise on a timeout...
                self._input_channel.consume_bit(learner_input)

            # fill the output buffer if the task hasn't produced any output
            if self._output_channel.is_empty():
                # demand for some output from the task (usually, silence)
                self._output_channel.set_message(
                        self._current_task.get_default_output())
            # We are in the middle of the task, so no rewards are given
            reward = None
        else:
            # If the task has ended and there is nothing else to say,
            # deinitialize the task and if there is still nothing more to
            # say, move to the next task
            if self._output_channel.is_empty() \
                    and not self._current_task_deinitialized:
                # this triggers the Ended event on the task
                self._current_task.deinit()
                self._current_task_deinitialized = True

            if self._output_channel.is_empty():
                self._reward = self._reward if self._reward is not None else 0
                reward = self._allowable_reward(self._reward)

                self._task_scheduler.reward(reward)
                self.reward_given(self._current_task, reward)

                self._current_task_deinitialized = False
                self._switch_new_task()
            else:
                # Do Nothing until the output channel is empty
                reward = None

        # Get one bit from the output buffer and ship it
        output = self._output_channel.consume_bit()

        # we hear to ourselves (WARNING: this can still generate behavior
        # in the task via the OutputMessageUpdated event)
        self._output_channel_listener.consume_bit(output)

        # advance time
        self._task_time += 1

        return output, reward

    def get_reward_per_task(self):
        '''
        Returns a dictonary that contains the cumulative reward for each
        task.
        '''
        return self._reward_per_task

    def _allowable_reward(self, reward):
        '''Checks if the reward is allowed within the limits of the
        `max_reward_per_task` parameter, and resets it to 0 if not.'''
        task_name = self._current_task.get_name()
        if self._reward_per_task[task_name] < self._max_reward_per_task:
            self._reward_per_task[task_name] += reward
            return reward
        else:
            return 0

    def is_silent(self):
        '''
        Tells if the environment is sending any information through the output
        channel.
        '''
        return self._output_channel.is_silent()

    def _on_input_sequence_updated(self, sequence):
        if self.event_manager.raise_event(SequenceReceived(sequence)):
            self.logger.debug("Sequence received by running task: '{0}'".format(
                    sequence))

    def _on_input_message_updated(self, message):
        # send the current received message to the task
        if self.event_manager.raise_event(MessageReceived(
                message)):
            self.logger.debug("Message received by running task: '{0}'".format(
                    message))

    def _on_output_sequence_updated(self, sequence):
        self.event_manager.raise_event(OutputSequenceUpdated(sequence))

    def _on_output_message_updated(self, message):
        self.event_manager.raise_event(OutputMessageUpdated(message))

    def set_reward(self, reward, message='', priority=0):
        '''Sets the reward that is going to be given
        to the learner once the task has sent all the remaining message'''
        self._reward = reward
        self.logger.debug('Setting reward {0} with message "{1}"'
                          ' and priority {2}'
                          .format(reward, message, priority))
        self.set_message(message, priority)

    def add_message(self, message):
        self.logger.debug('Appending message "{0}" with priority {1}'
                          .format(message, self._output_priority))
        self._output_channel.add_message(message)

    def set_message(self, message, priority=0):
        ''' Saves the message in the output buffer so it can be delivered
        bit by bit. It overwrites any previous content.
        '''
        if self._output_channel.is_empty() or priority >= self._output_priority:
            self.logger.debug('Setting message "{0}" with priority {1}'
                              .format(message, priority))
            self._output_channel.set_message(message)
            self._output_priority = priority
        else:
            self.logger.info(
                    'Message "{0}" blocked because of '
                    'low priority ({1}<{2}) '.format(
                            message, priority, self._output_priority)
            )

    def raise_event(self, event):
        return self.event_manager.raise_event(event)

    def raise_state_changed(self):
        '''
            This rases a StateChanged Event, meaning that something
            in the state of the world or the tasks changed (but we
            don't keep track what)
        '''
        # state changed events can only be raised if the current task is
        # started
        if self._current_task and self._current_task.has_started():
            # tasks that have a world should also take the world state as
            # an argument
            if self._current_world:
                self.raise_event(StateChanged(
                        self._current_world.state, self._current_task.state))
            else:
                self.raise_event(StateChanged(self._current_task.state))
            return True
        return False

    def _deregister_current_task(self):
        # deregister previous event managers
        if self._current_task:
            self._deregister_task_triggers(self._current_task)
            self._current_task.ended_updated.deregister(self._on_task_ended)

    def _on_task_ended(self, task):
        assert (task == self._current_task)
        # when a task ends, it doesn't process any more events
        self._deregister_current_task()

    def _switch_new_task(self):
        '''
        Asks the task scheduler for a new task,
        reset buffers and time, and registers the event handlers
        '''
        # pick a new task
        self._current_task = self._task_scheduler.get_next_task()
        # register to the ending event
        self._current_task.ended_updated.register(self._on_task_ended)
        try:
            # This is to check whether the user didn't mess up in instantiating
            # the class
            self._current_task.get_world()
        except TypeError:
            raise RuntimeError("The task {0} is not correctly instantiated. "
                               "Are you sure you are not forgetting to "
                               "instantiate the class?".format(
                    self._current_task))
        self.logger.debug("Starting new task: {0}".format(self._current_task))

        # check if it has a world:
        if self._current_task.get_world() != self._current_world:
            # if we had an ongoing world, end it.
            if self._current_world:
                self._current_world.end()
                self._deregister_task_triggers(self._current_world)
            self._current_world = self._current_task.get_world()
            if self._current_world:
                # register new event handlers for the world
                self._register_task_triggers(self._current_world)
                # initialize the new world
                self._current_world.start(self)
            self.world_updated(self._current_world)
        # reset state
        self._task_time = 0
        self._reward = None
        self._input_channel.clear()
        self._output_channel.clear()
        self._output_channel_listener.clear()
        # register new event handlers
        self._register_task_triggers(self._current_task)
        # start the task, sending the current environment
        # so it can interact by sending back rewards and messages
        self._current_task.start(self)
        self.task_updated(self._current_task)

    def _deregister_task_triggers(self, task):
        for trigger in task.get_triggers():
            try:
                self.event_manager.deregister(task, trigger)
            except ValueError:
                # if the trigger was not registered, we don't worry about it
                pass
            except KeyError:
                # if the trigger was not registered, we don't worry about it
                pass
        task.clean_dynamic_handlers()

    def _register_task_triggers(self, task):
        for trigger in task.get_triggers():
            self._register_task_trigger(task, trigger)

    def _register_task_trigger(self, task, trigger):
        self.event_manager.register(task, trigger)


# When a task is started, it will register a set of triggers
# which, for a specific kind of event (see below) and a further given
# filtering condition, it will call the specified event_handler function
Trigger = namedtuple('Trigger', ('type', 'condition', 'event_handler'))


class EventManager:
    def __init__(self):
        self.triggers = {}
        self.logger = logging.getLogger(__name__)

    def register(self, observer, trigger):
        '''
        Register a trigger (a tuple containing an
        ActivationCondition -a function/functor- and an EventHandler
        - another function/functor-)
        '''
        # initialize a list for each type of event (it's just an optimizaiton)
        if trigger.type not in self.triggers:
            self.triggers[trigger.type] = []
        self.logger.debug(
                "Registering Trigger for {0} event with handler {1} of object of "
                "type {2}".format(trigger.type.__name__, trigger.event_handler,
                                  observer.__class__.__name__))
        # save the trigger
        self.triggers[trigger.type].append((observer, trigger))

    def deregister(self, observer, trigger):
        self.triggers[trigger.type].remove((observer, trigger))

    def clear(self):
        '''
        Deregisters all triggers
        '''
        self.triggers.clear()

    def raise_event(self, event):
        handled = False
        # check if we have any trigger at all of this type of event
        if event.__class__ in self.triggers:
            # for all the triggers registered for this type of event
            for observer, trigger in self.triggers[event.__class__]:
                # check if the filtering condition is a go
                condition_outcome = trigger.condition(event)
                if condition_outcome:
                    # save, if the event expects it, the outcome of the
                    # condition checking
                    try:
                        event.condition_outcome = condition_outcome
                    except AttributeError:
                        self.logger.debug("Couldn't save condition outcome for "
                                          "event {0}".format(event))
                    self.logger.debug('{0} handled by {1}'.format(
                            event, trigger.event_handler))
                    # call the event handler
                    trigger.event_handler(observer, event)
                    # remember we handled the event and
                    # keep on processing other events
                    handled = True
        return handled


class RandomTaskScheduler:
    '''
    A Scheduler provides new tasks every time is asked.
    This is a random scheduler
    '''

    def __init__(self, tasks):
        self.tasks = tasks

    def get_next_task(self):
        # pick a random task
        return random.choice(self.tasks)

    def reward(self, reward):
        # whatever
        pass


class SequentialTaskScheduler:
    '''
    A Scheduler provides new tasks every time is asked.
    This is a random scheduler
    '''

    def __init__(self, tasks):
        self.tasks = tasks
        self.i = 0

    def get_next_task(self):
        # pick a random task
        ret = self.tasks[self.i]
        self.i = (self.i + 1) % len(self.tasks)
        return ret

    def reward(self, reward):
        # whatever
        pass


class IncrementalTaskScheduler:
    '''
    Switches to the next task type sequentially
    After the current task was successfully learned N times
    '''

    def __init__(self, tasks, success_threshold=2):
        self.tasks = tasks
        self.task_ptr = 0
        self.reward_count = 0
        self.success_threshold = success_threshold

    def get_next_task(self):
        if self.reward_count == self.success_threshold:
            self.reward_count = 0
            self.task_ptr = (self.task_ptr + 1) % len(self.tasks)
        return self.tasks[self.task_ptr]

    def reward(self, reward):
        self.reward_count += reward


# TODO: Create a BatchedScheduler that takes as an argument another
#       scheduler and just repeats the given tasks N times.


class DependenciesTaskScheduler:
    '''
    Takes a dependency graph between the tasks and randomly allocates between
    the ones that are at the root, or are dependent on other tasks that
    have been solved (based on a threshold)
    '''

    def __init__(self, tasks, tasks_dependencies, unlock_threshold=10):
        '''
        Args:
            tasks: a list of Task objects
            tasks_dependencies: list of ordered pairs of Task objects (t1,t2)
                if t2 depends on t1 to be completed.
            unlock_threshold: total cumulative reward needed for a
                task to be considered solved.
        '''
        self.tasks = tasks
        # a dictionary containing rewards per task
        self.rewards = defaultdict(int)
        # saves the last task that has been given to the learner
        self.last_task = None
        self.unlock_threshold = unlock_threshold
        self.solved_tasks = set()
        self.tasks_dependencies = tasks_dependencies
        # set of the tasks that are available to the learner
        self.available_tasks = set()
        # initially these are the tasks that have no dependencies on them
        self.find_available_tasks()

    def get_next_task(self):
        self.last_task = self.pick_new_task()
        return self.last_task

    def reward(self, reward):
        # remember the amount of times we have solved the task
        # using the name of the class to have a hashable value
        task_name = self.get_task_id(self.last_task)
        self.rewards[task_name] += reward
        if self.rewards[task_name] >= self.unlock_threshold:
            self.solved_tasks.add(task_name)
            # refresh the list of available tasks
            self.find_available_tasks()

    def get_task_id(self, task):
        return task.__class__.__name__

    def solved(self, task):
        return self.get_task_id(task) in self.solved_tasks

    def find_available_tasks(self):
        for t in self.tasks:
            task_available = True
            for t1, t2 in self.tasks_dependencies:
                if t2 == t and not self.solved(t1):
                    task_available = False
                    break
            if task_available:
                self.available_tasks.add(t)

    def pick_new_task(self):
        return random.sample(self.available_tasks, 1)[0]


class IdentitySerializer:
    '''
    Skips the serialization and just returns the text as-is.
    '''

    def __init__(self):
        self.SILENCE_TOKEN = ' '
        self.logger = logging.getLogger(__name__)

    def to_binary(self, message):
        return message

    def to_text(self, data):
        return data

    def can_deserialize(self, data):
        return data


class ScramblingSerializerWrapper:
    '''
    This is wrapper for any serializer that, on top of the serialization step,
    scrambles the words so they are unintelligible to human readers.
    Note: the scrambling process has two steps: a forward (during to_binary)
    where a new word is assigned to each input token and a backward (during
    to_text) where the word is translated back to its original form.
    If a word that has not been generated during the forward pass is sent to
    the backward pass, this word is left unchanged. As a consequence, if the
    learner uses a word (e.g "apple") before it has been uttered by the
    environment, it will go through unchanged. If at any point, the environment
    starts using this word, it will get assigned a new scrambled string (e.g.
    "vsdsf"), and now "apple" that was going through unchanged before, it's
    being mapped to a new string.
    '''

    def __init__(self, serializer, readable=True):
        '''
        Args:
            serialzer: underlying serializer that will get the calls forwarded.
        '''
        # the underlying serializer
        self._serializer = serializer
        self.SILENCE_TOKEN = serializer.SILENCE_TOKEN
        # 'vowels' and 'consonants' (to be alternated if readable = true)
        self.readable = readable
        self.V = 'aeiouy'
        self.C = ''.join([i for i in string.ascii_lowercase if i not in self.V])
        # a mapping of real words to scrambled words an back
        self.word_mapping = {}
        self.inv_word_mapping = {}
        self.logger = logging.getLogger(__name__)

    def to_binary(self, message):
        self.logger.debug("Tokenizing message '{0}'".format(message))
        # get all the parts of the message without cutting the spaces out
        tokens = self.tokenize(message)
        self.logger.debug("Scrambling message '{0}'".format(tokens))
        # transform each of the pieces (if needed) and merge them together
        scrambled_message = ''.join(self.scramble(t) for t in tokens)
        self.logger.debug("Returning scrambled message '{0}'".format(
                scrambled_message))
        # pass it on to the real serializer
        return self._serializer.to_binary(scrambled_message)

    def to_text(self, data):
        # get the scrambled message back from the bits
        scrambled_message = self._serializer.to_text(data)
        # split into tokens, including spaces and punctuation marks
        self.logger.debug("Tokenizing {0}".format(scrambled_message))
        tokens = self.tokenize(scrambled_message)
        self.logger.debug("Unscrambling {0}".format(tokens))
        # unmask the words in it
        return ''.join(self.unscramble(t) for t in tokens)

    def can_deserialize(self, data):
        if not self._serializer.can_deserialize(data):
            return False
        # get the scrambled message back from the bits
        scrambled_message = self._serializer.to_text(data)
        # split into tokens, including spaces and punctuation marks
        tokens = self.tokenize(scrambled_message)
        # to deserialize we have to be at the end of a word.
        return tokens and tokens[-1][1] != 'WORD'

    def scramble(self, token):
        word, pos = token
        if pos == 'SILENCE' or pos == 'PUNCT':
            # if this is a space or a punctuation sign, don't do anything
            return word
        else:
            if word.lower() not in self.word_mapping:
                # if we don't have a pseudo-word already assigned
                # generate a new pseudo-word
                pseudo_word = self.gen_pseudo_word(len(word))
                self.word_mapping[word.lower()] = pseudo_word
                self.inv_word_mapping[pseudo_word] = word.lower()
            return self.capitalize(word, self.word_mapping[word.lower()])

    def capitalize(self, word, scrambled_word):
        if len(scrambled_word) == len(word):
            # if the two words have the same length, we preverve capitalization
            return ''.join(scrambled_word[i].upper()
                           if word[i] in string.ascii_uppercase
                           else scrambled_word[i] for i in range(len(word)))
        else:
            # just capitalize the first letter
            return (scrambled_word[0].upper()
                    if word[0] in string.ascii_uppercase
                    else scrambled_word[0]) + scrambled_word[1:]

    def unscramble(self, token):
        scrambled_word, pos = token
        if pos == 'SILENCE' or pos == 'PUNCT':
            # if this is a space or a punctuation sign, don't do anything
            return scrambled_word
        else:
            # say that we have apple -> qwerty
            # if the word is qwerty, we return apple
            if scrambled_word.lower() in self.inv_word_mapping:
                return self.capitalize(scrambled_word,
                                       self.inv_word_mapping[
                                           scrambled_word.lower()])
            # conversely, if the word is apple, we return qwerty
            # so we have a bijection between the scrambled and normal words
            elif scrambled_word.lower() in self.word_mapping:
                return self.capitalize(scrambled_word, self.word_mapping[
                    scrambled_word.lower()])
            else:
                # otherwise we just return the word as is
                return scrambled_word

    def gen_pseudo_word(self, L=None):
        if not L:
            L = random.randint(1, 8)
        # generate one word that we hadn't used before
        while True:
            if self.readable:
                # alternating between vowels and consonants, sampled with repl.
                _choice, _range = random.choice, range(int(math.ceil(L / 2)))
                v = [_choice(self.V) for i in _range]
                c = [_choice(self.C) for i in _range]
                zipped = zip(v, c) if random.getrandbits(1) else zip(c, v)
                pseudo_word = ''.join([a for b in zipped for a in b])[:L]
            else:
                pseudo_word = ''.join(random.sample(
                        string.ascii_lowercase, L))
            if pseudo_word not in self.inv_word_mapping:
                return pseudo_word

    def tokenize(self, message):
        '''
        Simplified tokenizer that splits a message over spaces and punctuation.
        '''
        punct = ",.:;'\"?"
        silence_token = self._serializer.SILENCE_TOKEN
        tokenized_message = []
        tokens = re.split('(\W)', message)
        for t in tokens:
            if not t:
                # re.split can return empty strings between consecutive
                # separators: ignore them.
                continue
            # separate intial punctuation marks
            if t in punct:
                tokenized_message.append((t, 'PUNCT'))
            elif t == silence_token:
                tokenized_message.append((t, 'SILENCE'))
            else:
                tokenized_message.append((t, 'WORD'))
        return tokenized_message


class StandardSerializer:
    '''
    Transforms text into bits and back using UTF-8 format.
    '''

    def __init__(self):
        self.SILENCE_TOKEN = ' '
        self.SILENCE_ENCODING = u' '
        self.logger = logging.getLogger(__name__)

    def to_binary(self, message):
        '''
        Given a text message, returns a binary string (still represented as a
        character string).
        '''
        # All spaces are encoded as null bytes:
        message = message.replace(self.SILENCE_TOKEN, self.SILENCE_ENCODING)
        # handle unicode
        message = codecs.encode(message, 'utf-8')
        data = []
        for c in message:
            # get the numeric value of the character
            try:
                c = ord(c)
            except TypeError:
                # already an int (Python 3)
                pass
            # convert to binary
            bin_c = bin(c)
            # remove the '0b' prefix
            bin_c = bin_c[2:]
            # pad with zeros
            bin_c = bin_c.zfill(8)
            data.append(bin_c)
        return ''.join(data)

    def to_text(self, data, strict=False):
        '''Transforms a binary string into text.

        Given a binary string, returns the UTF-8 encoded text. If the
        string cannot be deserialized, returns None. It can also try to
        recover from meaningless data by skipping a few bytes in the beginning.

        Args:
            data: the binary string to deserialze.
            strict: if False, the initial bytes can be skipped in order to
            find a valid character. This allows to recover from randomly
            produced bit strings.

        Returns: A string with containing the decoded text.
        '''
        # if we are not in strict mode, we can skip bytes to find a message
        for skip in range(int(len(data) / 8) if not strict else 1):
            try:
                # convert data to a byte-stream
                message = bytearray()
                sub_data = data[skip * 8:]
                for i in range(int(len(sub_data) / 8)):
                    b = sub_data[i * 8:(i + 1) * 8]
                    message.append(int(b, 2))
                message = codecs.decode(message, 'utf-8')
                message = message.replace(self.SILENCE_ENCODING,
                                          self.SILENCE_TOKEN)
                if skip > 0:
                    self.logger.debug("Skipping {0} bytes to find a valid "
                                      "unicode character".format(skip))

                return message
            except UnicodeDecodeError:
                pass

        return None

    def can_deserialize(self, data):
        if len(data) < 8:
            return False
        return self.to_text(data) is not None


class GeneralSerializer:
    '''
    Transforms text into bits and back using specified mapping.
    Expects an index to symbol mapping `i2s`.
    silence_idx is which index in mapping is silence, defaults to 0
    '''

    def __init__(self, i2s, silence_idx):
        self.SILENCE_TOKEN = ' '
        self.SILENCE_ENCODING = silence_idx if silence_idx is not None else 0

        self.i2s = i2s
        self.s2i = {}
        for k, v in self.i2s.items:
            self.s2i[v] = k

        self.L = math.ceil(math.log(len(self.i2s), 2))

        # pad end of dictionary with silence
        for k in range(len(self.i2s), math.pow(2, self.L)):
            self.i2s[k] = self.SILENCE_TOKEN

        assert i2s[self.SILENCE_ENCODING] == self.SILENCE_TOKEN, \
            'mapping conflict for silence'

        self.logger = logging.getLogger(__name__)

    def to_binary(self, message):
        '''
        Given a text message, returns a binary string (still represented as a
        character string).
        '''
        message = codecs.encode(message, 'ascii')

        data = []
        for c in message:
            c = self.s2i[c]
            bin_c = bin(c)[2:]
            bin_c = bin_c.zfill(self.L)
            data.append(bin_c)

        return ''.join(data)

    def to_text(self, data):
        '''Transforms a binary string into text.

        Given a binary string, returns the encoded text. If the
        string cannot be deserialized, returns None.

        Args:
            data: the binary string to deserialze.

        Returns: A string with containing the decoded text.
        '''
        buff = codecs.encode(data, 'ascii')
        text = u''
        while buff != "":
            idx = int(buff[:self.L], 2)
            text = text + self.i2s[idx]
            buff = buff[self.L:]
        return text

    def can_deserialize(self, data):
        if len(data) < self.L:
            return False
        return self.to_text(data) is not None


class ASCIISerializer:
    '''
    Transforms text into bits and back according to ASCII format.
    '''

    def __init__(self):
        i2s = {}
        for k in range(0, 255):
            i2s[k] = chr(k)

        return GeneralSerializer(i2s, ord(' '))


class Session:
    def __init__(self, environment, learner,
                 default_sleep=0.01):
        # internal initialization
        self._env = environment
        self._learner = learner
        self._default_sleep = default_sleep
        self._sleep = self._default_sleep
        # listen to changes in the currently running task
        self._env.task_updated.register(self.on_task_updated)
        # observable status
        self.env_token_updated = Observable()
        self.learner_token_updated = Observable()
        self.total_reward_updated = Observable()
        self.total_time_updated = Observable()
        # -- accounting --
        # total time
        self._total_time = 0
        # total cumulative reward
        self._total_reward = 0
        # keep track of how many times we have tried each task
        self._task_count = defaultdict(int)
        # keep track of how much time we have spent on each task
        self._task_time = defaultdict(int)

    def run(self):
        # initialize a token variable
        token = None
        # send out initial values of status variables
        self.total_time_updated(self._total_time)
        self.total_reward_updated(self._total_reward)
        # loop until stopped
        self._stop = False

        while not self._stop:
            # first speaks the environment one token (one bit)
            token, reward = self._env.next(token)
            self.env_token_updated(token)
            # reward the learner if it has been set
            self._learner.try_reward(reward)
            self.accumulate_reward(reward)

            # allow some time before processing the next iteration
            if self._sleep > 0:
                time.sleep(self._sleep)

            # then speaks the learner one token
            token = self._learner.next(token)
            self.learner_token_updated(token)

            # and we loop
            self._total_time += 1
            self._task_time[self._current_task.get_name()] += 1
            self.total_time_updated(self._total_time)

    def stop(self):
        self._stop = True

    def get_total_time(self):
        return self._total_time

    def get_total_reward(self):
        return self._total_reward

    def get_reward_per_task(self):
        return self._env.get_reward_per_task()

    def get_task_count(self):
        return self._task_count

    def get_task_time(self):
        return self._task_time

    def accumulate_reward(self, reward):
        '''Records the reward if the learner hasn't exceeded the maximum
        possible amount of reward allowed for the current task.'''
        if reward is not None:
            self._total_reward += reward
            if reward != 0:
                self.total_reward_updated(self._total_reward)

    def on_task_updated(self, task):
        self._current_task = task
        self._task_count[self._current_task.get_name()] += 1

    def set_sleep(self, sleep):
        if sleep < 0:
            sleep = 0
        self._sleep = sleep

    def get_sleep(self):
        return self._sleep

    def add_sleep(self, dsleep):
        self.set_sleep(self.get_sleep() + dsleep)

    def reset_sleep(self):
        self._sleep = self._default_sleep


# These are the possible types of events (with their parameters, if any)
Start = namedtuple('Start', ())
Ended = namedtuple('Ended', ())
WorldStart = namedtuple('WorldStart', ())
Timeout = namedtuple('Timeout', ())

SequenceReceived = namedtuple('SequenceReceived', ('sequence',))
OutputSequenceUpdated = namedtuple('OutputSequenceUpdated',
                                   ('output_sequence',))
OutputMessageUpdated = namedtuple('OutputMessageUpdated',
                                  ('output_message',))


# horrible way of making second_state optional
class StateChanged(namedtuple('StateChanged', ('state', 'second_state'))):
    """
    Event that is triggered when some member variable within the
    state object of a Task or a World is changed.
    """

    def __new__(cls, state, second_state=None):
        return super(StateChanged, cls).__new__(cls, state, second_state)


# helper methods for handling received messages
class MessageReceived():
    '''A message received event. It has some useful helpers'''

    def __init__(self, message):
        self.message = message
        # this instance variable gets assigned the outcome of the
        # trigger's condition
        self.condition_outcome = None

    def is_message(self, msg, suffix=''):
        '''Checks if the received message matches the one in the parameter'''
        # if the suffix is empty we need, the semantics that would be
        # reasonable for 0 have to be expressed with None
        if len(suffix) > 0:
            is_match = self.message[-(len(msg) + len(suffix)):
            -len(suffix)] == msg and \
                       suffix == self.message[-len(suffix):]
        else:
            is_match = self.message[-len(msg):] == msg
        return is_match

    def is_message_exact(self, msg, suffix=''):
        '''Checks if the received message exactly matches the one in the parameter'''
        preffix = self.message[0:-(len(msg) + len(suffix))]
        m = re.search("^\s*$", preffix)
        return self.message[-(len(msg) + len(suffix)):-len(suffix)] == msg and \
               suffix == self.message[-len(suffix):] and m

    def get_match(self, ngroup=0):
        '''If the regular expression in the Trigger condition had groups,
        it can retreive what they captured.'''
        return self.condition_outcome.group(ngroup)

    def get_match_groups(self):
        '''If the regular expression in the Trigger condition had groups,
        it retreives all of them.'''
        return self.condition_outcome.groups()


# Event handlers are annotated through decorators and are automatically
# registered by the environment on Task startup

# Implementation trick to remember the type of event and the filtering condition
# that is informed through the decorators.
# We map the annotated methods to their corresponding triggers, so when we start
# a task, we can scan through its memebers and find the trigger here.
global_event_handlers = {}


def method_to_func(f):
    """
    Converts a bound method to an unbound function.
    """
    try:
        return f.im_func
    except AttributeError:  # Python 3
        try:
            return f.__func__
        except AttributeError:  # not a method
            return f


# Decorator for the Start of Task event handler
def on_start():
    """
    Start event decorator
    """

    def register(f):
        f = method_to_func(f)
        # The filtering condition is always True
        global_event_handlers[f] = Trigger(Start, lambda e: True, f)
        return f

    return register


# Decorator for the End of Task event handler
def on_ended():
    """Denitialization event decorator"""

    def register(f):
        f = method_to_func(f)
        # The filtering condition is always True
        global_event_handlers[f] = Trigger(Ended, lambda e: True, f)
        return f

    return register


# Decorator for the World Start event handler
def on_world_start():
    """
    WorldStart event decorator
    """

    def register(f):
        f = method_to_func(f)
        # The filtering condition is always True
        global_event_handlers[f] = Trigger(WorldStart, lambda e: True, f)
        return f

    return register


# Decorator for the StateChanged event handler
def on_state_changed(condition):
    '''
    Decorator to capture a StateChanged event. Its condition is a function
    that takes the tasks state (or the world state and the task state, in that
    order, if the task has a world parameter) and checks for any condition
    on those state variables. Notice that the argument is the `state` instance
    variable within the task and not the task itself.
    '''

    def register(f):
        f = method_to_func(f)
        # The filtering condition is given as an argument.
        # There could be one or two state objects (corresponding to the
        # world state). So we check if we need to call the condition with
        # one or two arguments.
        global_event_handlers[f] = Trigger(
                StateChanged, lambda e: e.second_state and
                                        condition(e.state, e.second_state) or
                                        (not e.second_state and condition(e.state)), f)
        return f

    return register


def on_message(target_message=None):
    """
    Decorator to capture the reception of a message from the Learner. It
    optionally receives a regular expression to be matched against the message.
    """

    def register(f):
        f = method_to_func(f)
        # If a target message is given, interpret it as a regular expression
        if target_message:
            cmessage = re.compile(target_message)
        else:
            cmessage = None
        # The filtering condition applied the target message expression
        # to the event message
        global_event_handlers[f] = Trigger(
                MessageReceived,
                lambda e: cmessage is None or cmessage.search(e.message), f)
        return f

    return register


def on_output_message(target_message=None):
    """
    Decorator to capture a message that it has been outputted by the
    Environment.
    """

    def register(f):
        f = method_to_func(f)
        # If a target message is given, interpret it as a regular expression
        if target_message:
            cmessage = re.compile(target_message)
        else:
            cmessage = None
        # The filtering condition applied the target message expression
        # to the event message
        global_event_handlers[f] = Trigger(
                OutputMessageUpdated,
                lambda e: cmessage is None or cmessage.search(e.output_message), f)
        return f

    return register


def on_sequence(target_sequence=None):
    """
    Decorator to capture the reception of a bit sequence from the Learner.
    """

    def register(f):
        f = method_to_func(f)
        if target_sequence:
            csequence = re.compile(target_sequence)
        else:
            csequence = None
        # The filtering condition is either the target bit itself or nothing
        global_event_handlers[f] = Trigger(
                SequenceReceived,
                lambda e: csequence is None or csequence.search(e.sequence), f)
        return f

    return register


def on_output_sequence(target_sequence=None):
    """
    Decorator to capture a bit sequence that it has been outputted by the
    Environment.
    """

    def register(f):
        f = method_to_func(f)
        if target_sequence:
            csequence = re.compile(target_sequence)
        else:
            csequence = None
        # The filtering condition is either the target bit itself or nothing
        global_event_handlers[f] = Trigger(
                OutputSequenceUpdated,
                lambda e: csequence is None or csequence.search(e.output_sequence),
                f)
        return f

    return register


def on_timeout():
    """
    Decorator to capture the Timeout event.
    """

    def register(f):
        f = method_to_func(f)
        # There is no filtering condition (it always activates if registered)
        global_event_handlers[f] = Trigger(Timeout, lambda e: True, f)
        return f

    return register


def handler_to_trigger(f):
    '''checks whether f is a function and it was registered to a Trigger.
    If so, it returns the trigger.
    '''
    try:
        if f in global_event_handlers:
            return global_event_handlers[f]
        else:
            return None
    except TypeError:
        # if f is unhashable, it's definetly not a function
        return None


class StateTrackingDefaultdictWrapper(defaultdict):
    '''This is a wrapper for variables stored in a State object so
    if something in them change, the original State also gets changed'''

    def __init__(self, obj, owner):
        '''owner here is the State or a parent StateVariable'''
        super(StateTrackingDefaultdictWrapper, self).__init__(
                obj.default_factory, obj)
        self._owner = owner

    def __setitem__(self, name, value):
        super(StateTrackingDefaultdictWrapper, self).__setitem__(name, value)
        self._raise_state_changed()

    def _raise_state_changed(self):
        '''recursively forwards the call to the owner'''
        return self._owner._raise_state_changed()


class StateTrackingDictionaryWrapper(dict):
    '''This is a wrapper for variables stored in a State object so
    if something in them change, the original State also gets changed'''

    def __init__(self, obj, owner):
        '''owner here is the State or a parent StateVariable'''
        super(StateTrackingDictionaryWrapper, self).__init__(obj)
        self._owner = owner

    def __setitem__(self, name, value):
        super(StateTrackingDictionaryWrapper, self).__setitem__(name, value)
        self._raise_state_changed()

    def _raise_state_changed(self):
        '''recursively forwards the call to the owner'''
        return self._owner._raise_state_changed()


class State(object):
    '''Holds the state variables for a Task or a world and raises events when
    they change'''

    def __init__(self, owner):
        '''owner is the Taks or World whose state we keep track of'''
        super(State, self).__setattr__('_owner', owner)
        super(State, self).__setattr__('logger',
                                       logging.getLogger(__name__))

    def __setattr__(self, name, value):
        '''intercept every time a value is updated to raise the associated event
        '''
        # wrap the variable in an StateVariable to report whether it changes
        if isinstance(value, defaultdict):
            self.logger.debug("Wrapping variable {0} as a defaultdict"
                              .format(value))
            value = StateTrackingDefaultdictWrapper(value, self)
        elif isinstance(value, dict):
            self.logger.debug("Wrapping variable {0} as a dict".format(value))
            value = StateTrackingDictionaryWrapper(value, self)
        # apply the assignment operation
        super(State, self).__setattr__(name, value)
        # raise a StateChanged
        self._raise_state_changed()

    def _raise_state_changed(self):
        return self._owner._raise_state_changed()


class ScriptSet(object):
    """
    Base class for the World and the Task. It contains all of its common
    behavior.
    """

    def __init__(self):
        # The environment is set when the script is started
        self._env = None
        self._started = False
        self._ended = False
        # observable events
        self.ended_updated = Observable()
        # a bit ugly, but there are worse things in life
        self.state_updated = Observable()
        # remember dynamically register handlers to destroy their triggers
        self.dyn_handlers = set()

    def clean_dynamic_handlers(self):
        for h in self.dyn_handlers:
            del global_event_handlers[h]
        self.dyn_handlers = set()

    def has_started(self):
        return self._started

    def has_ended(self):
        return self._ended

    def start(self, env):
        self._env = env
        self._ended = False
        self._started = False
        # this is where all the state variables should be kept
        self.state = State(self)

    def end(self):
        self._ended = True
        self.ended_updated(self)

    def get_triggers(self):
        '''Returns the set of triggers that have been registered for this
        task
        '''
        triggers = []
        for fname in dir(self):
            try:
                # We try to extract the function object that was registered
                try:
                    f = getattr(self, fname).im_func
                except AttributeError:  # Python 3
                    f = getattr(self, fname).__func__
                trigger = handler_to_trigger(f)
                if trigger:
                    triggers.append(trigger)
            except AttributeError:
                pass
        return triggers

    def get_name(self):
        '''Some unique identifier of the task'''
        return self.__class__.__name__

    def add_handler(self, handler):
        '''
        Adds and registers a handler dynamically during a task runtime.
        '''
        trigger = handler_to_trigger(handler)
        if trigger:
            self._env._register_task_trigger(self, trigger)
            self.dyn_handlers.add(handler)

    def _raise_state_changed(self):
        ret = self._env.raise_state_changed()
        if self.has_started():
            # notify (outside) observers
            self.state_updated(self)
        return ret

    def __str__(self):
        return str(self.__class__.__name__)

    # ### API for the scripts ###
    def set_reward(self, reward, message='', priority=0):
        self._reward = reward
        self._env.set_reward(reward, message, priority)
        self.end()

    def set_message(self, message, priority=0):
        self._env.set_message(message, priority)

    def add_message(self, message):
        self._env.add_message(message)

    def ignore_last_char(self):
        '''
        Replaces the last character in the input channel with a silence.
        '''
        self._env._input_channel.set_deserialized_buffer(
                self._env._input_channel.get_text()[:-1] +
                self._env._serializer.SILENCE_TOKEN
        )


class World(ScriptSet):
    def __init__(self):
        super(World, self).__init__()

    def start(self, env):
        super(World, self).start(env)
        self._env.raise_event(WorldStart())
        self._started = True


# Base class for tasks
class Task(ScriptSet):
    def __init__(self, max_time, world=None):
        super(Task, self).__init__()
        self._world = world
        self._max_time = max_time

    def get_world(self):
        return self._world

    def check_timeout(self, t):
        # if we are still in the process of outputting a message,
        # let it finish
        if t >= self._max_time and self._env._output_channel.is_empty():
            self._env.event_manager.raise_event(Timeout())
            self.end()
            return True
        return False

    def start(self, env):
        super(Task, self).start(env)
        self._env.raise_event(Start())
        self._started = True

    def end(self):
        super(Task, self).end()
        self._env.raise_event(Ended())

    def deinit(self):
        '''You can override this function to do anything just before the task
        is deallocated'''
        pass

    # ### API for the scripts ###
    def get_time(self):
        '''Gets the environment's task time'''
        return self._env._task_time

    def set_reward(self, reward, message='', priority=1):
        '''Assigns a reward to the learner and ends the task.

        :param reward: numerical reward given to the learner
        :param message: optional message to be given with the reward
        :param priotity: the priority of the message. If there is another
            message on the output stream and the priority is lower than it,
            the message will be blocked.
        '''
        super(Task, self).set_reward(reward, message, priority)

    def set_message(self, message, priority=1):
        '''Sets the message that is going to be sent to the learner over
        the next time steps.

        :param message: message to be sent.
        :param priotity: the priority of the message. If there is another
            message on the output stream and the priority is lower than it,
            the message will be blocked.
        '''
        super(Task, self).set_message(message, priority)

    def get_default_output(self):
        '''Returns the token that should be spoken by the task whenever there
        is no content in buffer.
        '''
        return self._env._serializer.SILENCE_TOKEN
