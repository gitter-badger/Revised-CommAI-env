#!/usr/bin/env python3
#
# Copyright (c) 2017-, Stephen B. Hope
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the LICENSE.md file in the root directory of this
# source tree. An additional grant of patent rights can be found in the PATENTS file in the same directory.

# TODO fix imports

class InputChannel:
    """ remembers the inout in binary format. leftmost deserialization if the binary buffer.  remember the position
    until which we deserialized the binary buffer. event that gets fired for every new bit. event that gets fired for
    every new character

    """

    def __init__(self, serializer):
        # TODO unresolved ref Observable
        """
        :param serializer:
        """
        self.serializer = serializer
        self._binary_buffer = ''
        self._deserialized_buffer = ''
        self._deserialized_pos = 0
        self.sequence_updated = Observable()
        self.message_updated = Observable()

    def consume_bit(self, input_bit):
        """ Takes a bit into the channel, for now we are storing the input as strings (let's change this later).
        Store the but in the binary input buffer.  Notify the updated sequence.  check if we can deserialize the
        final part of sequence.  Deserialize the chunk. Update the position

        :param input_bit:
        :return:

        """
        if input_bit == 0 or input_bit == 1:
            input_bit = str(input_bit)
        self._binary_buffer += input_bit
        self.sequence_updated(self._binary_buffer)
        undeserialized_part = self.get_undeserialized()
        if self.serializer.can_deserialize(undeserialized_part):
            self._deserialized_buffer += self.serializer.to_text(undeserialized_part)
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
        """ Remembers the data to be shipped out.  Event fired every time output sequence changes

        :param serializer:
        """
        self.serializer = serializer
        self._binary_buffer = ''
        self.sequence_updated = Observable()
        self.logger = logging.getLogger(__name__)

    def set_message(self, message):
        """ find the first available point from where we can insert the new buffer without breaking the encoding.  if
        we can decode from insert_point on, we can replace that information with the new buffer

        :param message:
        :return:
        """
        new_binary = self.serializer.to_binary(message)
        insert_point = len(self._binary_buffer)
        for i in range(len(self._binary_buffer)):
            if self.serializer.to_text(self._binary_buffer[i:]):
                insert_point = i
                break
        if insert_point > 0:
            self.logger.debug("Inserting new contents at {0}".format(insert_point))
        self._set_buffer(self._binary_buffer[:insert_point] + new_binary)

    def add_message(self, message):
        """ Append the binary encoding to end of buffer

        :param message:
        :return:
        """
        new_binary = self.serializer.to_binary(message)
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

        {"tasks":{"<task_id>": {"type": "<task_class>", }, "<task_id>": "type": "<task_class>", "world": "<world_id>"}
         "...": "..."}, "worlds": {"<world_id>": {"type": "<world_class>", }}, "scheduler": {"type":
         "<scheduler_class>", "args": {"<scheduler_arg>": <scheduler_arg_value>, }}}

    The scheduler scheduler_arg_value could be a container including task ids, which will be replaced by the concrete
    tasks instances.
    """
    def create_tasks(self, tasks_config_file):
        """ Given a json configuration file, it returns a scheduler object set up as described in the file.
        instantiate the worlds (typically there is only one).  map each task instantiate the tasks with the world (if
        any).  retrieve what type of scheduler we need to create. prepare the arguments to instantiate the scheduler.
        all arguments that begin with the name tasks are taken as collections of ids that should be mapped to the
        corresponding tasks object. return a scheduler with its corresponding arguments.

        :param tasks_config_file:
        :return:
        """
        config = json.load(open(tasks_config_file))
        worlds = dict((world_id, self.instantiate_world(world_config['type']))
                      for world_id, world_config in config['worlds'].items())
        tasks = dict((task_id, self.instantiate_task(task_config['type'], worlds, task_config.get('world', None)))
                     for task_id, task_config in config['tasks'].items())
        scheduler_class = get_class(config['scheduler']['type'])
        scheduler_args = {}
        for arg_name, arg_value in config['scheduler']['args'].items():
            if arg_name.startswith('tasks'):
                scheduler_args[arg_name] = map_tasks(arg_value, tasks)
            else:
                scheduler_args[arg_name] = arg_value
        return scheduler_class(**scheduler_args)

    def instantiate_world(self, world_class):
        # TODO static method
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
        # TODO static method
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
    """ Loads a python file containing a stand-alone function called`create_tasks` that returns a TaskScheduler object.
    transform the config file path into a module path.
    """
    def create_tasks(self, tasks_config_file):
        """ make sure we have a relative path. just in case, remove initial unneeded "./".

        :param tasks_config_file:
        :return:
        """
        tasks_config_file = os.path.relpath(tasks_config_file)
        if tasks_config_file.startswith('..'):
            raise RuntimeError("The task configuration file must be in the "
                               "same directory as the competition source.")
        # TODO fix
        if tasks_config_file.startswith('./'):
            tasks_config_file = tasks_config_file[2:]
        tasks_config_module = os.path.splitext(tasks_config_file)[0].replace('/', '.')
        mod = __import__(tasks_config_module, fromlist = [''])
        return mod.create_tasks()


def get_class(name):
    """

    :param name:
    :return:
    """
    components = name.split('.')
    mod = __import__('.'.join(components[:-1]), fromlist = [components[-1]])
    mod = getattr(mod, components[-1])
    return mod


def map_tasks(arg, tasks):
    """ if arg is a task, return the task object.  arg is hashable, type cannot map to task. treat arg as a
    collection that should be mapped. Un-hashable type

    :param arg:
    :param tasks:
    :return:
    """
    try:
        return tasks[arg]
    except KeyError:
        # TODO fix
        raise RuntimeError("Couldn't find task id '{0}'.".format(arg))
    except TypeError:
        return list(map(lambda x: map_tasks(x, tasks), arg))


class Environment:
    """ The Environment is the one that communicates with the Learner, interpreting its output and reacting to it.
    The interaction is governed by an ongoing task which is picked by a TaskScheduler object.

        :param serializer: a Serializer object that translates text into binary and back.
        :param task_scheduler: a TaskScheduler object that determines which task is going to be run next.
        :param scramble: if True, the words outputted by the tasks are randomly scrambled.
        :param max_reward_per_task: maximum amount of reward that a learner can receive for a given task.
    """
    def __init__(self, serializer, task_scheduler, scramble=False, max_reward_per_task=10):
        """ save parameters into member variables. cumulative reward per task.  the event manager is the controller
        that dispatches changes in the environment (like new inputs or state changes) to handler functions in the
        tasks that tell the environment how to react.  initialize member variables.  we hear to our own output.
        Output channel.  Input channel.  priority of ongoing message.  Reward to be given to learner at end of task.
        Current task time.  Task deintialize.  Internal logger.  signals.  Register channel observers

        :param serializer:
        :param task_scheduler:
        :param scramble:
        :param max_reward_per_task:
        """
        # TODO unresolved refs defaultdict, Observable, logging, _on_input_sequence_updated, _on_input_message_updated,
        # TODO line 2 _on_output_sequence_updated, _on_output_message_updated
        self._task_scheduler = task_scheduler
        self._serializer = serializer
        self._max_reward_per_task = max_reward_per_task
        self._reward_per_task = defaultdict(int)
        self.event_manager = EventManager()
        self._current_task = None
        self._current_world = None
        self._output_channel_listener = InputChannel(serializer)
        if scramble:
            serializer = ScramblingSerializerWrapper(serializer)
        self._output_channel = OutputChannel(serializer)
        self._input_channel = InputChannel(serializer)
        self._output_priority = 0
        self._reward = None
        self._task_time = None
        self._current_task_deinitialized = False
        self.logger = logging.getLogger(__name__)
        self.world_updated = Observable()
        self.task_updated = Observable()
        self.reward_given = Observable()
        self._input_channel.sequence_updated.register(self._on_input_sequence_updated)
        self._input_channel.message_updated.register(self._on_input_message_updated)
        self._output_channel_listener.sequence_updated.register(self._on_output_sequence_updated)
        self._output_channel_listener.message_updated.register(self._on_output_message_updated)

    def next(self, learner_input):
        # TODO rewrite
        """ Main loop of the Environment. Receives one bit from the learner and produces a response (also one bit).
        Make sure we have a task.  Task not reached end by Timeout OR achieving goal.  Check if timeout occurred.
         Process the input from the learner and raise events.  Record the input from the leaner and deserialize it.
         Fill output buffer, if task not produced any output. Demand output from task.  If the task has ended and
         there is nothing else to say, de-initialize the task and if there is still nothing more to say, move to the
         next task. task in process, no reward given.  Triggers the Ended event on the task.  Do nothing until output
         channel is empty. Get one bit from output buffer and ship it we hear to ourselves(WARNING: this can still
         generate behavior in the task via the OutputMessageUpdated event)

        :param learner_input:
        :return:
        """
        # TODO var reward not used, unresolved ref _allowable_reward, _switch_new_task
        if not self._current_task:
            self._switch_new_task()
        if not self._current_task.has_ended():
            self._current_task.check_timeout(self._task_time)
            if learner_input is not None:  #
                advance
                time
                # TODO this bit is dropped otherwise on a timeout...
                self._input_channel.consume_bit(learner_input)
            if self._output_channel.is_empty():  #
                self._output_channel.set_message(self._current_task.get_default_output())
            reward = None
        else:
            if self._output_channel.is_empty() and not self._current_task_deinitialized:
                self._current_task.deinit()  #
                self._current_task_deinitialized = True
            if self._output_channel.is_empty():
                self._reward = self._reward if self._reward is not None else 0
                reward = self._allowable_reward(self._reward)
                self._task_scheduler.reward(reward)
                self.reward_given(self._current_task, reward)
                self._current_task_deinitialized = False
                self._switch_new_task()
            else:
                reward = None
        output = self._output_channel.consume_bit()
                self._output_channel_listener.consume_bit(output)
        self._task_time += 1
    # TODO return outside function, reward unresolved
        return output, reward

    def get_reward_per_task(self):
        """ Returns a dictionary that contains the cumulative reward for each
        task.

        :return:
        """
        return self._reward_per_task

    def _allowable_reward(self, reward):
        """ Checks if the reward is allowed within the limits of the `max_reward_per_task` parameter, and resets it
        to 0 if not.

        :param reward:
        :return:
        """
        task_name = self._current_task.get_name()
        if self._reward_per_task[task_name] < self._max_reward_per_task:
            self._reward_per_task[task_name] += reward
            return reward
        else:
            return 0

    def is_silent(self):
        """ Tells if the environment is sending any information through the output channel.

        :return:
        """
        return self._output_channel.is_silent()

    def _on_input_sequence_updated(self, sequence):
        """

        :param sequence:
        :return:
        """
        if self.event_manager.raise_event(SequenceReceived(sequence)):
            self.logger.debug("Sequence received by running task: '{0}'".format(sequence))

    def _on_input_message_updated(self, message):
        """ send the current received message to the task

        :param message:
        :return:
        """
        if self.event_manager.raise_event(MessageReceived(                message)):
            self.logger.debug("Message received by running task: '{0}'".format(message))

    def _on_output_sequence_updated(self, sequence):
        """

        :param sequence:
        :return:
        """
        self.event_manager.raise_event(OutputSequenceUpdated(sequence))

    def _on_output_message_updated(self, message):
        """

        :param message:
        :return:
        """
        self.event_manager.raise_event(OutputMessageUpdated(message))

    def set_reward(self, reward, message='', priority=0):
        """ Sets the reward that is going to be given to the learner once the task has sent all the remaining message


        :param self:
        :param reward:
        :param message:
        :param priority:
        :return:
        """
        self._reward = reward
        self.logger.debug('Setting reward {0} with message "{1}"' ' and priority {2}'.format(reward, message, priority))
        self.set_message(message, priority)

    def add_message(self, message):
        """

        :param self:
        :param message:
        :return:
        """
        self.logger.debug('Appending message "{0}" with priority {1}' .format(message, self._output_priority))
        self._output_channel.add_message(message)

    def set_message(self, message, priority=0):
        """ Saves the message in the output buffer so it can be delivered bit by bit. It overwrites any previous
        content.

        :param self:
        :param message:
        :param priority:
        :return:
        """

        if self._output_channel.is_empty() or priority >= self._output_priority:
            self.logger.debug('Setting message "{0}" with priority {1}' .format(message, priority))
            self._output_channel.set_message(message)
            self._output_priority = priority
        else:
            self.logger.info('Message "{0}" blocked because of ' 'low priority ({1}<{2}) '
                            .format(message, priority, self._output_priority))

    def raise_event(self, event):
        """

        :param event:
        :return:
        """
        return self.event_manager.raise_event(event)

    def raise_state_changed(self):
        """ This raises a StateChanged Event, meaning that something in the state of the world or the tasks changed
        (but we don't keep track what) state changed events can only be raised if the current task is started.  Tasks
        with world should take world state as an argument

        :return:
        """
        if self._current_task and self._current_task.has_started():
            if self._current_world:
                self.raise_event(StateChanged(self._current_world.state, self._current_task.state))
            else:
                self.raise_event(StateChanged(self._current_task.state))
            return True
        return False

    def _deregister_current_task(self):
        """ de-register previous event managers

        :return:
        """
        if self._current_task:
            self._deregister_task_triggers(self._current_task)
            self._current_task.ended_updated.deregister(self._on_task_ended)

    def _on_task_ended(self, task):
        """ when a task ends, it doesn't process any more events

        :param task:
        :return:
        """
        assert (task == self._current_task)
        self._deregister_current_task()

    def _switch_new_task(self):
        """ Asks the task scheduler for a new task, reset buffers and time, and registers the event handlers
        pick a new task.  Register to ending event.  Check for user error initiating the class.  Check if task has
        world if we have an ongoing world end it.  Register new event handlers for the world.  Initialize the new world.
         Reset state. Register new event handlers. start the task, sending the current environment so it can interact
         by sending back rewards and messages

        :return:

        """
        self._current_task = self._task_scheduler.get_next_task()
        self._current_task.ended_updated.register(self._on_task_ended)
        try:
            self._current_task.get_world()
        except TypeError:
            raise RuntimeError("The task {0} is not correctly instantiated.  "
                               "Are you sure you are not forgetting to " "instantiate the class?"
                               .format(self._current_task))
        self.logger.debug("Starting new task: {0}".format(self._current_task))
        if self._current_task.get_world() != self._current_world:
            if self._current_world:
                self._current_world.end()
                self._deregister_task_triggers(self._current_world)
            self._current_world = self._current_task.get_world()
            if self._current_world:
                self._register_task_triggers(self._current_world)
                self._current_world.start(self)
            self.world_updated(self._current_world)
        self._task_time = 0
        self._reward = None
        self._input_channel.clear()
        self._output_channel.clear()
        self._output_channel_listener.clear()
        self._register_task_triggers(self._current_task)
        self._current_task.start(self)
        self.task_updated(self._current_task)

    def _deregister_task_triggers(self, task):
        """ If the trigger was not registered, disregard it.  If the trigger was not registered, discard it.

        :param task:
        :return:
        """
        for trigger in task.get_triggers():
            try:
                self.event_manager.deregister(task, trigger)
            except ValueError:
                pass
            except KeyError:
                pass
        task.clean_dynamic_handlers()

    def _register_task_triggers(self, task):
        """

        :param task:
        :return:
        """
        for trigger in task.get_triggers():
            self._register_task_trigger(task, trigger)

    def _register_task_trigger(self, task, trigger):
        """

        :param task:
        :param trigger:
        :return:
        """
        self.event_manager.register(task, trigger)

""" When a task is started, it will register a set of triggers which, for a specific kind of event (see below) and a
further given filtering condition, it will call the specified event_handler function
"""
Trigger = namedtuple('Trigger', ('type', 'condition', 'event_handler'))


class EventManager:
    """

    """
    def __init__(self):
        """

        """
        self.triggers = {}
        self.logger = logging.getLogger(__name__)

    def register(self, observer, trigger):
        # TODO rewrite
        """ Register a trigger (a tuple containing an ActivationCondition -a function/functor- and an
        EventHandler - another function/functor-) initialize a list for each type of event (it's just an optimization).
         Save the trigger

        :param observer:
        :param trigger:

        :return:
        """
        if trigger.type not in self.triggers:
            self.triggers[trigger.type] = []
        self.logger.debug(
                "Registering Trigger for {0} event with handler {1} of object of "
                "type {2}".format(trigger.type.__name__, trigger.event_handler, observer.__class__.__name__))
        self.triggers[trigger.type].append((observer, trigger))

    def deregister(self, observer, trigger):
        """

        :param observer:
        :param trigger:
        :return:
        """
        self.triggers[trigger.type].remove((observer, trigger))

    def clear(self):
        """ clears all triggers

        :return:
        """
        self.triggers.clear()

    def raise_event(self, event):
        """ Check for trigger for event type.  For all registered triggers for event type.  check if filtering
        condition is a go.  Save if event expects it, outcome of the condition checking.  Call event handler.
        Remember handling the event, proceed with processing events

        :param event:
        :return:
        """
        handled = False
        if event.__class__ in self.triggers:
            for observer, trigger in self.triggers[event.__class__]:
                condition_outcome = trigger.condition(event)
                if condition_outcome:
                    try:
                        event.condition_outcome = condition_outcome
                    except AttributeError:
                        self.logger.debug("Couldn't save condition outcome for " "event {0}".format(event))
                    self.logger.debug('{0} handled by {1}'.format(
                            event, trigger.event_handler))
                    trigger.event_handler(observer, event)
                    handled = True
        return handled


class RandomTaskScheduler:
    """
    A Scheduler provides new tasks every time is asked. This is a random scheduler
    """
    def __init__(self, tasks):
        """

        :param tasks:
        """
        self.tasks = tasks

    def get_next_task(self):
        """ pick a random task

        :return:
        """
        return random.choice(self.tasks)

    def reward(self, reward):
        # TODO static func
        """ whatever

        :param reward:
        :return:
        """
        pass


class SequentialTaskScheduler:
    """
    A Scheduler provides new tasks every time is asked. This is a random scheduler
    """
    def __init__(self, tasks):
        """

        :param tasks:
        """
        self.tasks = tasks
        self.i = 0

    def get_next_task(self):
        """ pick a random task

        :return:
        """
        ret = self.tasks[self.i]
        self.i = (self.i + 1) % len(self.tasks)
        return ret

    def reward(self, reward):
        # TODO static
        """ whatever

        :param reward:
        :return:
        """
        #
        pass


class IncrementalTaskScheduler:
    """
    Switches to the next task type sequentially After the current task was successfully learned N times
    """
    def __init__(self, tasks, success_threshold=2):
        """

        :param tasks:
        :param success_threshold:
        """
        self.tasks = tasks
        self.task_ptr = 0
        self.reward_count = 0
        self.success_threshold = success_threshold

    def get_next_task(self):
        """

        :return:
        """
        if self.reward_count == self.success_threshold:
            self.reward_count = 0
            self.task_ptr = (self.task_ptr + 1) % len(self.tasks)
        return self.tasks[self.task_ptr]

    def reward(self, reward):
        self.reward_count += reward


# TODO: Create a BatchedScheduler that takes as an argument another
class DependenciesTaskScheduler:
    """ scheduler and just repeats the given tasks N times. Takes a dependency graph between the tasks and randomly
    allocates between the ones that are at the root, or are dependent on other tasks that have been solved
    (based on a threshold)
    """
    def __init__(self, tasks, tasks_dependencies, unlock_threshold=10):
        """ Dictionary containing rewards per task.  Saves the last task given to the learner.  Set of tasks
        available to learner.  Initially these are tasks with no dependencies.

        :param tasks: a list of Task objects
        :param tasks_dependencies: ist of ordered pairs of Task objects (t1,t2) if t2 depends on t1 to be completed.
        :param unlock_threshold: total cumulative reward needed for a task to be considered solved.
        """
        self.tasks = tasks
        # TODO unresolved ref defaultdict
        self.rewards = defaultdict(int)
        self.last_task = None
        self.unlock_threshold = unlock_threshold
        self.solved_tasks = set()
        self.tasks_dependencies = tasks_dependencies
        self.available_tasks = set()
        self.find_available_tasks()

    def get_next_task(self):
        """

        :return:
        """
        self.last_task = self.pick_new_task()
        return self.last_task

    def reward(self, reward):
        """ remember the amount of times we have solved the task using the name of the class to have a hashable value.
         Refresh list of available tasks

        :param reward:
        :return:
        """
        task_name = self.get_task_id(self.last_task)
        self.rewards[task_name] += reward
        if self.rewards[task_name] >= self.unlock_threshold:
            self.solved_tasks.add(task_name)
            self.find_available_tasks()

    def get_task_id(self, task):
        """

        :param task:
        :return:
        """
        return task.__class__.__name__

    def solved(self, task):
        """

        :param task:
        :return:
        """
        return self.get_task_id(task) in self.solved_tasks

    def find_available_tasks(self):
        """

        :return:
        """
        for t in self.tasks:
            task_available = True
            for t1, t2 in self.tasks_dependencies:
                if t2 == t and not self.solved(t1):
                    task_available = False
                    break
            if task_available:
                self.available_tasks.add(t)

    def pick_new_task(self):
        """

        :return:
        """
        return random.sample(self.available_tasks, 1)[0]



class IdentitySerializer:
    """
    Skips the serialization and just returns the text as-is.
    """
    def __init__(self):
        # TODO unresolved ref logging
        """

        """
        self.SILENCE_TOKEN = ' '
        self.logger = logging.getLogger(__name__)

    def to_binary(self, message):
        """

        :param message:
        :return:
        """
        return message

    def to_text(self, data):
        """

        :param data:
        :return:
        """
        return data

    def can_deserialize(self, data):
        """

        :param data:
        :return:
        """
        return data


class ScramblingSerializerWrapper:
    """ This is wrapper for any serializer that, on top of the serialization step, scrambles the words so they are
    unintelligible to human readers. Note: the scrambling process has two steps: a forward (during to_binary) where
    a new word is assigned to each input token and a backward (during to_text) where the word is translated back to
    its original form. If a word that has not been generated during the forward pass is sent to the backward pass,
    this word is left unchanged. As a consequence, if the learner uses a word (e.g "apple") before it has been
    uttered by the environment, it will go through unchanged. If at any point, the environment starts using this
    word, it will get assigned a new scrambled string (e.g. "vsdsf"), and now "apple" that was going through
    unchanged before, it's being mapped to a new string.
    """
    def __init__(self, serializer, readable=True):
        """ the underlying serializer.  'vowels' and 'consonants' (to be alternated if readable = true.  Mapping real
        words to scrambled words and back

        :param serializer: underlying serializer that will get the calls forwarded.
        :param readable:
        """
        self._serializer = serializer
        self.SILENCE_TOKEN = serializer.SILENCE_TOKEN
        self.readable = readable
        self.V = 'aeiouy'
        self.C = ''.join([i for i in string.ascii_lowercase if i not in self.V])
        self.word_mapping = {}
        self.inv_word_mapping = {}
        self.logger = logging.getLogger(__name__)

    def to_binary(self, message):
        """ Get all parts of message without removing spaces. Transform each piece (if needed) and merge.  Return it
        to the real serializer

        :param message:
        :return:
        """
        self.logger.debug("Tokenizing message '{0}'".format(message))
        # TODO unresolved attrib ,tokenize class ScramblingSerializerWrapper
        tokens = self.tokenize(message)
        self.logger.debug("Scrambling message '{0}'".format(tokens))
        scrambled_message = ''.join(self.scramble(t) for t in tokens)
        self.logger.debug("Returning scrambled message '{0}'".format(scrambled_message))
        return self._serializer.to_binary(scrambled_message)


    def to_text(self, data):
        # TODO unrelsolved attrib ,tokenize class ScramblingSerializerWrapper
        """ get the scrambled message back from the bits.  split into tokens, including spaces and punctuation marks.
         unmask the words in it

        :param data:
        :return:
        """
        scrambled_message = self._serializer.to_text(data)
        self.logger.debug("Tokenizing {0}".format(scrambled_message))
        tokens = self.tokenize(scrambled_message)
        self.logger.debug("Unscrambling {0}".format(tokens))
        return ''.join(self.unscramble(t) for t in tokens)

    def can_deserialize(self, data):
        """ Get scrambled message back from the bits.  Split into tokens, including spaces and punctuation.
        Deserialize, need to be at end of a word.

        :param data:
        :return:
        """
        # TODO unresolved attrib ,tokenize class ScramblingSerializerWrapper
        if not self._serializer.can_deserialize(data):
            return False
        scrambled_message = self._serializer.to_text(data)
        tokens = self.tokenize(scrambled_message)
        return tokens and tokens[-1][1] != 'WORD'

    def scramble(self, token):
        """ If is a space or a punctuation sign, don't do anything.  Generate psuedo word if needed.

        :param token:
        :return:
        """
        word, pos = token
        if pos == 'SILENCE' or pos == 'PUNCT':
            return word
        else:
            if word.lower() not in self.word_mapping:
                # TODO unresolved attrib ,gen_pseudo_word class ScramblingSerializerWrapper
                pseudo_word = self.gen_pseudo_word(len(word))
                self.word_mapping[word.lower()] = pseudo_word
                self.inv_word_mapping[pseudo_word] = word.lower()
            return self.capitalize(word, self.word_mapping[word.lower()])

    def capitalize(self, word, scrambled_word):
        # TODO static, unresolved ref to string
        """ Preserve capitalization in words with same length.  Capitalize first letter.

        :param word:
        :param scrambled_word:
        :return:
        """
        if len(scrambled_word) == len(word):
            return ''.join(scrambled_word[i].upper()

                           if word[i] in string.ascii_uppercase
                           else scrambled_word[i] for i in range(len(word)))
        else:
            return (scrambled_word[0].upper()
                    if word[0] in string.ascii_uppercase
                    else scrambled_word[0]) + scrambled_word[1:]

    def unscramble(self, token):
        """ Check if space or punctuation, if so no action.  say that we have apple -> qwerty if the word is qwerty,
        we return apple conversely, if the word is apple, we return qwerty so we have a bit-injection between the
        scrambled and normal words.  Return word as is.

        :param token:
        :return:
        """
        scrambled_word, pos = token
        if pos == 'SILENCE' or pos == 'PUNCT':
            return scrambled_word
        else:
            if scrambled_word.lower() in self.inv_word_mapping:
                return self.capitalize(scrambled_word, self.inv_word_mapping[scrambled_word.lower()])
            elif scrambled_word.lower() in self.word_mapping:
                return self.capitalize(scrambled_word, self.word_mapping[
                    scrambled_word.lower()])
            else:
                return scrambled_word

    def gen_pseudo_word(self, L=None):
        # TODO arg name to lower case, unresolved ref random, math
        """ generate one word that we hadn't used before.  alternating between vowels and consonants, sampled with repl.

        :param L:
        :return:
        """
        if not L:
            L = random.randint(1, 8)
        while True:
            if self.readable:
                _choice, _range = random.choice, range(int(math.ceil(L / 2)))
                v = [_choice(self.V) for i in _range]
                c = [_choice(self.C) for i in _range]
                zipped = zip(v, c) if random.getrandbits(1) else zip(c, v)
                pseudo_word = ''.join([a for b in zipped for a in b])[:L]
            else:
                pseudo_word = ''.join(random.sample(string.ascii_lowercase, L))
            if pseudo_word not in self.inv_word_mapping:
                return pseudo_word

    def tokenize(self, message):
        """ Simplified tokenizer that splits a message over spaces and punctuation. re.split can return empty
        strings between consecutive separators: ignore them.  separate initial punctuation marks.

        :param message:
        :return:
        """
        punct = ",.:;'\"?"
        silence_token = self._serializer.SILENCE_TOKEN
        tokenized_message = []
        tokens = re.split('(\W)', message)
        for t in tokens:
            if not t:
                continue
            if t in punct:
                tokenized_message.append((t, 'PUNCT'))
            elif t == silence_token:
                tokenized_message.append((t, 'SILENCE'))
            else:
                tokenized_message.append((t, 'WORD'))
        return tokenized_message


class StandardSerializer:
    """
    Transforms text into bits and back using UTF-8 format.
    """
    def __init__(self):
        # TODO unresolved ref logging
        """

        """
        self.SILENCE_TOKEN = ' '
        self.SILENCE_ENCODING = u' '

        self.logger = logging.getLogger(__name__)

    def to_binary(self, message):
        """ Given a text message, returns a binary string(still represented as a character string). All spaces are
        encoded as null bytes: Get numeric value of the character.  Already an int python3.  convert to binary.
        remove the '0b' prefix.  pad with zeros. handle unicode.

        :param message:
        :return:
        """
        message = message.replace(self.SILENCE_TOKEN, self.SILENCE_ENCODING)
        message = codecs.encode(message, 'utf-8')
        data = []
        # TODO fix for python 3
        for c in message:
            try:
                c = ord(c)
            except TypeError:
                pass
            bin_c = bin(c)
            bin_c = bin_c[2:]
            bin_c = bin_c.zfill(8)
            data.append(bin_c)
        return ''.join(data)

    def to_text(self, data, strict=False):
        """ Transforms a binary string into text. Given a binary string, returns the UTF-8 encoded text. If the
        string cannot be deserialized, returns None. It can also try to recover from meaningless data by skipping a
        few bytes in the beginning. if we are not in strict mode, we can skip bytes to find a message.  convert data
        to a byte-stream.

        :param data:  the binary string to de-serialize.
        :param strict:  if False, the initial bytes can be skipped in order to find a valid character. This allows
        to recover from randomly produced bit strings.

        :return: A string with containing the decoded text.
        """
        # TODO replace
        for skip in range(int(len(data) / 8) if not strict else 1):
            try:
                message = bytearray()
                sub_data = data[skip * 8:]
                for i in range(int(len(sub_data) / 8)):
                    b = sub_data[i * 8:(i + 1) * 8]
                    message.append(int(b, 2))
                message = codecs.decode(message, 'utf-8')
                message = message.replace(self.SILENCE_ENCODING, self.SILENCE_TOKEN)
                if skip > 0:
                    self.logger.debug("Skipping {0} bytes to find a valid " "unicode character".format(skip))
                return message
            except UnicodeDecodeError:
                pass
        return None

    def can_deserialize(self, data):
        """

        :param data:
        :return:
        """
        if len(data) < 8:
            return False
        return self.to_text(data) is not None


class GeneralSerializer:
    """
    Transforms text into bits and back using specified mapping. Expects an index to symbol mapping `i2s`.
    silence_idx is which index in mapping is silence, defaults to 0.
    """
    def __init__(self, i2s, silence_idx):
        """ Pad end of dictionary with silence

        :param i2s:
        :param silence_idx:
        """
        self.SILENCE_TOKEN = ' '
        self.SILENCE_ENCODING = silence_idx if silence_idx is not None else 0
        self.i2s = i2s
        self.s2i = {}
        for k, v in self.i2s.items:
            self.s2i[v] = k
            # TODO unresovled ref to math, logging
        self.L = math.ceil(math.log(len(self.i2s), 2))
        for k in range(len(self.i2s), math.pow(2, self.L)):
            self.i2s[k] = self.SILENCE_TOKEN
        assert i2s[self.SILENCE_ENCODING] == self.SILENCE_TOKEN, 'mapping conflict for silence'
        self.logger = logging.getLogger(__name__)

    def to_binary(self, message):
        """ Given a text message, returns a binary string (still represented as a character string).

        :param message:
        :return:
        """
        message = codecs.encode(message, 'ascii')

        data = []
        for c in message:
            c = self.s2i[c]
            bin_c = bin(c)[2:]
            bin_c = bin_c.zfill(self.L)
            data.append(bin_c)

        return ''.join(data)

    def to_text(self, data):
        """ Transforms a binary string into text. Given a binary string, returns the encoded text. If the
        string cannot be deserialized, returns None.

        :param data: the binary string to deserialze.

        :return: A string with containing the decoded text.
        """
        # TODO unresolved ref to codecs
        buff = codecs.encode(data, 'ascii')
        text = u''
        while buff != "":
            idx = int(buff[:self.L], 2)
            text = text + self.i2s[idx]
            buff = buff[self.L:]
        return text

    def can_deserialize(self, data):
        """

        :param data:
        :return:
        """
        if len(data) < self.L:
            return False
        return self.to_text(data) is not None


class ASCIISerializer:
    """
    Transforms text into bits and back according to ASCII format.
    """
    def __init__(self):
        i2s = {}
        for k in range(0, 255):
            i2s[k] = chr(k)
            # TODO can not return a value from __inti__
        return GeneralSerializer(i2s, ord(' '))


class Session:
    """

    """
    def __init__(self, environment, learner, default_sleep=0.01):
        # TODO unresolved ref to Observable, defaultdict
        """ internal initialization.  Listen to changes in current running task.  observable status.  -- accounting
        -- total time.  Total cumulative reward.  keep track of how many attempts per task.  Keep track of how much
        time we have spend on each track

        :param environment:
        :param learner:
        :param default_sleep:
        """
        self._env = environment
        self._learner = learner
        self._default_sleep = default_sleep
        self._sleep = self._default_sleep
        self._env.task_updated.register(self.on_task_updated)
        self.env_token_updated = Observable()
        self.learner_token_updated = Observable()
        self.total_reward_updated = Observable()
        self.total_time_updated = Observable()
        self._total_time = 0
        self._total_reward = 0
        self._task_count = defaultdict(int)
        self._task_time = defaultdict(int)

    def run(self):
        """ initialize a token variable.  Send out intial values of status variables.  Loop until stopped.  first
        speaks the environment, one token (one bit).  Reward the learner if set. Allow some time before processing the
        next iteration.  Leaner speaks one token.

        :return:
        """
        # TODO fix
        token = None
        self.total_time_updated(self._total_time)
        self.total_reward_updated(self._total_reward)
        self._stop = False
        while not self._stop:
            token, reward = self._env.next(token)
            self.env_token_updated(token)
            self._learner.try_reward(reward)
            self.accumulate_reward(reward)
            if self._sleep > 0:
                time.sleep(self._sleep)
            token = self._learner.next(token)
            self.learner_token_updated(token)
            self._total_time += 1
            self._task_time[self._current_task.get_name()] += 1
            self.total_time_updated(self._total_time)

    def stop(self):
        """

        :return:
        """
        # TODO def outside __init__
        self._stop = True

    def get_total_time(self):
        """

        :return:
        """
        return self._total_time

    def get_total_reward(self):
        """

        :return:
        """
        return self._total_reward

    def get_reward_per_task(self):
        """

        :return:
        """
        return self._env.get_reward_per_task()

    def get_task_count(self):
        """

        :return:
        """
        return self._task_count

    def get_task_time(self):
        """

        :return:
        """
        return self._task_time

    def accumulate_reward(self, reward):
        """ Records the reward if the learner hasn't exceeded the maximum possible amount of reward allowed for the
        current task.

        :param reward:
        :return:
        """
        if reward is not None:
            self._total_reward += reward
            if reward != 0:
                self.total_reward_updated(self._total_reward)

    def on_task_updated(self, task):
        """

        :param task:
        :return:
        """
        # TODO def _current_task, outside __init__
        self._current_task = task
        self._task_count[self._current_task.get_name()] += 1

    def set_sleep(self, sleep):
        """

        :param sleep:
        :return:
        """
        if sleep < 0:
            sleep = 0
        self._sleep = sleep

    def get_sleep(self):
        """

        :return:
        """
        return self._sleep

    def add_sleep(self, dsleep):
        """

        :param dsleep:
        :return:
        """
        self.set_sleep(self.get_sleep() + dsleep)

    def reset_sleep(self):
        """

        :return:
        """
        self._sleep = self._default_sleep

""" These are the possible types of events (with their parameters, if any)
"""
# TODO unresolved ref namedtuple
Start = namedtuple('Start', ())
Ended = namedtuple('Ended', ())
WorldStart = namedtuple('WorldStart', ())
Timeout = namedtuple('Timeout', ())
SequenceReceived = namedtuple('SequenceReceived', ('sequence',))
OutputSequenceUpdated = namedtuple('OutputSequenceUpdated', ('output_sequence',))
OutputMessageUpdated = namedtuple('OutputMessageUpdated', ('output_message',))


# TODO 'horrible way of making second_state optional' authors words
class StateChanged(namedtuple('StateChanged', ('state', 'second_state'))):
    """
    Event that is triggered when some member variable within the state object of a Task or a World is changed.
    """
    def __new__(cls, state, second_state=None):
        return super(StateChanged, cls).__new__(cls, state, second_state)


class MessageReceived():
    """
    A message received event. It has some useful helpers helper methods for handling received messages
    """
    def __init__(self, message):
        """ this instance variable gets assigned the outcome of the trigger's condition

        :param message:
        """
        self.message = message
        self.condition_outcome = None

    def is_message(self, msg, suffix=''):
        """ Checks if the received message matches the one in the parameter if the suffix is empty we need, the
        semantics that would be reasonable for 0 have to be expressed with None

        :param msg:
        :param suffix:
        :return:
        """
        if len(suffix) > 0:
            is_match = self.message[-(len(msg) + len(suffix)):
            -len(suffix)] == msg and suffix == self.message[-len(suffix):]
        else:
            is_match = self.message[-len(msg):] == msg
        return is_match

    def is_message_exact(self, msg, suffix=''):
        """ Checks if the received message exactly matches the one in the parameter

        :param msg:
        :param suffix:
        :return:
        """
        preffix = self.message[0:-(len(msg) + len(suffix))]
        m = re.search("^\s*$", preffix)
        return self.message[
               -(len(msg) + len(suffix)):-len(suffix)] == msg and  suffix == self.message[-len(suffix):] and m

    def get_match(self, ngroup=0):
        """ If the regular expression in the Trigger condition had groups, it can retrieve what they captured.

        :param ngroup:
        :return:
        """
        return self.condition_outcome.group(ngroup)

    def get_match_groups(self):
        """ If the regular expression in the Trigger condition had groups, it retrieves all of them.

        :return:
        """
        return self.condition_outcome.groups()

""" Event handlers are annotated through decorators and are automatically registered by the environment on Task startup.
Implementation trick to remember the type of event and the filtering condition that is informed through the decorators.
We map the annotated methods to their corresponding triggers, so when we start a task, we can scan through its
members and find the trigger here.
"""
global_event_handlers = {}

def method_to_func(f):
    """ Converts a bound method to an unbound function. not a method.

    :param f:
    :return:
    """
    # TODO fix for python 3
    try:
        return f.im_func
    except AttributeError:
        try:
            return f.__func__
        except AttributeError:
            return f

def on_start():
    """ Decorator for the Start of Task event handler

    :return:
    """
    def register(f):
        """ Filtering condition always True

        :param f:
        :return:
        """
        f = method_to_func(f)
        global_event_handlers[f] = Trigger(Start, lambda e: True, f)
        return f

    return register

def on_ended():
    """ Decorator for the End of Task event handler, De-initialization event decorator"""

    def register(f):
        """ Filtering condition always True

        :param f:
        :return:
        """
        f = method_to_func(f)
        global_event_handlers[f] = Trigger(Ended, lambda e: True, f)
        return f

    return register

def on_world_start():
    """ Decorator for the World Start event handler

    :return:
    """
    def register(f):
        """ The filtering condition is always True

        :param f:
        :return:
        """
        f = method_to_func(f)
        global_event_handlers[f] = Trigger(WorldStart, lambda e: True, f)
        return f

    return register


#
def on_state_changed(condition):
    """ Decorator for the StateChanged event handler  Decorator to capture a StateChanged event. Its condition is a
    function that takes the tasks state (or the world state and the task state, in that order, if the task has a
    world parameter) and checks for any condition on those state variables. Notice that the argument is the `state`
    instance variable within the task and not the task itself.

    :param condition:
    :return:
    """
    def register(f):
        """ The filtering condition is given as an argument. There could be one or two state objects (corresponding to
        the world state). So we check if we need to call the condition with one or two arguments.

        :param f:
        :return:
        """
        f = method_to_func(f)
        global_event_handlers[f] = Trigger(
                StateChanged, lambda e: e.second_state and condition(e.state, e.second_state) or
                                        (not e.second_state and condition(e.state)), f)
        return f
    return register


def on_message(target_message=None):
    """ Decorator to capture the reception of a message from the Learner. It optionally receives a regular expression
    to be matched against the message. The filtering condition applied the target message expression to the event
    message

    :param target_message:
    :return:
    """
    def register(f):
        # TODO unresolved ref re
        """ If a target message is given, interpret it as a regular expression

        :param f:
        :return:
        """
        f = method_to_func(f)
        if target_message:
            cmessage = re.compile(target_message)
        else:
            cmessage = None
        global_event_handlers[f
        ] = Trigger(MessageReceived, lambda e: cmessage is None or cmessage.search(e.message), f)
        return f

    return register


def on_output_message(target_message=None):
    """ Decorator to capture a message that it has been outputted by the Environment.

    :param target_message:
    :return:
    """
    def register(f):
        """ If a target message is given, interpret it as a regular expression.  The filtering condition applied the
        target message expression to the event message

        :param f:
        :return:
        """
        f = method_to_func(f)
        if target_message:
            cmessage = re.compile(target_message)
        else:
            cmessage = None
        global_event_handlers[f] = Trigger(
                OutputMessageUpdated, lambda e: cmessage is None or cmessage.search(e.output_message), f)
        return f

    return register


def on_sequence(target_sequence=None):
    """ Decorator to capture the reception of a bit sequence from the Learner.

    :param target_sequence:
    :return:
    """
    def register(f):
        """ The filtering condition is either the target bit itself or nothing

        :param f:
        :return:
        """
        # TODO unresloved ref re
        f = method_to_func(f)
        if target_sequence:
            csequence = re.compile(target_sequence)
        else:
            csequence = None
        global_event_handlers[f] = Trigger(
                SequenceReceived, lambda e: csequence is None or csequence.search(e.sequence), f)
        return f
    return register


def on_output_sequence(target_sequence=None):
    """ Decorator to capture a bit sequence that it has been outputted by the Environment. The filtering condition is
    either the target bit itself or nothing

    :param target_sequence:
    :return:
    """

    def register(f):
        """

        :param f:
        :return:
        """
        f = method_to_func(f)
        if target_sequence:
            csequence = re.compile(target_sequence)
        else:
            csequence = None
        global_event_handlers[f] = Trigger(
                OutputSequenceUpdated, lambda e: csequence is None or csequence.search(e.output_sequence), f)
        return f

    return register


def on_timeout():
    """
    Decorator to capture the Timeout event.
    """

    def register(f):
        """ There is no filtering condition (it always activates if registered)

        :param f:
        :return:
        """
        f = method_to_func(f)
        global_event_handlers[f] = Trigger(Timeout, lambda e: True, f)
        return f

    return register


def handler_to_trigger(f):
    """ checks whether f is a function and it was registered to a Trigger. If so, it returns the trigger. If not
    hashable, it's not a function

    :param f:
    :return:
    """
    try:
        if f in global_event_handlers:
            return global_event_handlers[f]
        else:
            return None
    except TypeError:
        return None


class StateTrackingDefaultdictWrapper(defaultdict):
    # TODO unresolved ref defaultdict
    """
    This is a wrapper for variables stored in a State object so if something in them change, the original State also
    gets changed
    """
    def __init__(self, obj, owner):
        """ owner here is the State or a parent StateVariable

        :param obj:
        :param owner:
        """
        super(StateTrackingDefaultdictWrapper, self).__init__(obj.default_factory, obj)
        self._owner = owner

    def __setitem__(self, name, value):
        """

        :param name:
        :param value:
        :return:
        """
        super(StateTrackingDefaultdictWrapper, self).__setitem__(name, value)
        self._raise_state_changed()

    def _raise_state_changed(self):
        """ recursively forwards the call to the owner

        :return:
        """
        return self._owner._raise_state_changed()


class StateTrackingDictionaryWrapper(dict):
    """
    This is a wrapper for variables stored in a State object so if something in them change, the original State also
    gets changed
    """
    def __init__(self, obj, owner):
        """ owner here is the State or a parent StateVariable

        :param obj:
        :param owner:
        """
        super(StateTrackingDictionaryWrapper, self).__init__(obj)
        self._owner = owner

    def __setitem__(self, name, value):
        # TODO access to protected member of class
        """

        :param name:
        :param value:
        :return:
        """
        super(StateTrackingDictionaryWrapper, self).__setitem__(name, value)
        self._raise_state_changed()

    def _raise_state_changed(self):
        # TODO _owner._raise_state_changed access to protected member of class
        """ recursively forwards the call to the owner

        :return:
        """
        return self._owner._raise_state_changed()


class State(object):
    """
    Holds the state variables for a Task or a world and raises events when they change
    """
    def __init__(self, owner):
        # TODO unresolved ref logging
        """ owner is the Tasks or World whose state we keep track of

        :param owner:
        """
        super(State, self).__setattr__('_owner', owner)
        super(State, self).__setattr__('logger', logging.getLogger(__name__))

    def __setattr__(self, name, value):
        """ intercept every time a value is updated to raise the associated event wrap the variable in an
        StateVariable to report whether it changes. Apply the assignment operation.  Raise a StateChanged

        :param name:
        :param value:
        :return:
        """
        # TODO unresoveled refs to defaultdict, logger
        if isinstance(value, defaultdict):
            self.logger.debug("Wrapping variable {0} as a defaultdict".format(value))
            value = StateTrackingDefaultdictWrapper(value, self)
        elif isinstance(value, dict):
            self.logger.debug("Wrapping variable {0} as a dict".format(value))
            value = StateTrackingDictionaryWrapper(value, self)
        super(State, self).__setattr__(name, value)
        self._raise_state_changed()

    def _raise_state_changed(self):
        """

        :return:
        """
        # TODO access to _owner protected member of class
        return self._owner._raise_state_changed()


class ScriptSet(object):
    """
    Base class for the World and the Task. It contains all of its common behavior.
    """

    def __init__(self):
        """ The environment is set when the script is started.  Observable events.  a bit ugly, but there are worse
        things in life.  remember dynamically register handlers to destroy their triggers
        """
        self._env = None
        self._started = False
        self._ended = False
        # TODO unresolved ref Obserable
        self.ended_updated = Observable()
        self.state_updated = Observable()
        self.dyn_handlers = set()

    def clean_dynamic_handlers(self):
        """

        :return:
        """
        for h in self.dyn_handlers:
            del global_event_handlers[h]
        self.dyn_handlers = set()

    def has_started(self):
        """

        :return:
        """
        return self._started

    def has_ended(self):
        """

        :return:
        """
        return self._ended

    def start(self, env):
        # TODO state def outside __init__
        """ this is where all the state variables should be kept

        :param env:
        :return:
        """
        self._env = env
        self._ended = False
        self._started = False
        self.state = State(self)

    def end(self):
        """

        :return:
        """
        self._ended = True
        self.ended_updated(self)

    def get_triggers(self):
        # TODO fix for python 3
        """ Returns the set of triggers that have been registered for this task We try to extract the function object
        that was registered

        :return:
        """
        triggers = []
        for fname in dir(self):
            try:
                #
                try:
                    f = getattr(self, fname).im_func
                except AttributeError:
                    f = getattr(self, fname).__func__
                trigger = handler_to_trigger(f)
                if trigger:
                    triggers.append(trigger)
            except AttributeError:
                pass
        return triggers

    def get_name(self):
        """ Some unique identifier of the task

        :return:
        """
        return self.__class__.__name__

    def add_handler(self, handler):
        # TODO access to protected member of class _env._register_task_trigger
        """ Adds and registers a handler dynamically during a task runtime.

        :param handler:
        :return:
        """
        trigger = handler_to_trigger(handler)
        if trigger:
            self._env._register_task_trigger(self, trigger)
            self.dyn_handlers.add(handler)

    def _raise_state_changed(self):
        """ notify (outside) observers

        :return:
        """
        ret = self._env.raise_state_changed()
        if self.has_started():
            self.state_updated(self)
        return ret

    def __str__(self):
        """

        :return:
        """
        return str(self.__class__.__name__)

    def set_reward(self, reward, message='', priority=0):
        """ API for the scripts

        :param reward:
        :param message:
        :param priority:
        :return:
        """
        self._reward = reward
        self._env.set_reward(reward, message, priority)
        self.end()

    def set_message(self, message, priority=0):
        """

        :param message:
        :param priority:
        :return:
        """
        self._env.set_message(message, priority)

    def add_message(self, message):
        """

        :param message:
        :return:
        """
        self._env.add_message(message)

    def ignore_last_char(self):
        # TODO access to protected member of class _env._input_channel _env._serializer
        """ Replaces the last character in the input channel with a silence.

        :return:
        """
        self._env._input_channel.set_deserialized_buffer\
            (self._env._input_channel.get_text()[:-1] + self._env._serializer.SILENCE_TOKEN)


class World(ScriptSet):
    def __init__(self):
        super(World, self).__init__()

    def start(self, env):
        """

        :param env:
        :return:
        """
        super(World, self).start(env)
        self._env.raise_event(WorldStart())
        self._started = True


class Task(ScriptSet):
    """
    Base class for tasks
    """
    def __init__(self, max_time, world=None):
        super(Task, self).__init__()
        self._world = world
        self._max_time = max_time

    def get_world(self):
        return self._world

    def check_timeout(self, t):
        """ if we are still in the process of outputting a message, let it finish

        :param t:
        :return:
        """
        # TODO access to protected member of class _env._output_channel
        if t >= self._max_time and self._env._output_channel.is_empty():
            self._env.event_manager.raise_event(Timeout())
            self.end()
            return True
        return False

    def start(self, env):
        """

        :param env:
        :return:
        """
        super(Task, self).start(env)
        self._env.raise_event(Start())
        self._started = True

    def end(self):
        """

        :return:
        """
        super(Task, self).end()
        self._env.raise_event(Ended())

    def deinit(self):
        """ You can override this function to do anything just before the task is de-allocated
        """
        # TODO static
        pass

"""
API for the scripts
"""

    def get_time(self):
        # TODO access to protected member of class _env._task_time
        """ Gets the environment's task time

        :return:
        """
        return self._env._task_time


    def set_reward(self, reward, message='', priority=1):
        # TODO shadowing set_reward, redeclaired set_reward without use
        """ Assigns a reward to the learner and ends the task.

        :param self:
        :param reward: numerical reward given to the learner
        :param message: optional message to be given with the reward
        :param priority: the priority of the message. If there is another message on the output stream and the
        priority is lower than it, the message will be blocked.
        :return:
        """
        super(Task, self).set_reward(reward, message, priority)


    def set_message(self, message, priority=1):
        # TODO shadowing set_message
        """ Sets the message that is going to be sent to the learner over the next time steps.

            :param self:
            :param message:  message to be sent.
            :param priority: the priority of the message. If there is another message on the output stream and the
            priority is lower than it, the message will be blocked.
    :return:
    """
        super(Task, self).set_message(message, priority)

    def get_default_output(self):
        # TODO access to protected member of class self._env._serializer
        """ Returns the token that should be spoken by the task whenever there is no content in buffer.

        :return:
        """
        return self._env._serializer.SILENCE_TOKEN
