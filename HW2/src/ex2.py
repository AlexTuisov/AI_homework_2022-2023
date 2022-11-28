import random
from copy import deepcopy
from itertools import product

ids = ["111111111", "222222222"]


class Action:
    def __init__(self, name, arguments=[]):
        self.name = name
        self.arguments = tuple(arguments)
        self.taxi = self.arguments[0] if arguments else None

    def __str__(self):
        return self.name + str(self.arguments)

    def get_action(self):
        if self.arguments:
            return tuple([self.name] + list(self.arguments))
        else:
            return self.name


class State:
    def __init__(self, state):
        self.state_as_dict = deepcopy(state)


def location_is_legal(n, m, state):
    max_n = len(state['map']) - 1
    max_m = len(state['map'][0]) - 1
    return (n >= 0) and (n <= max_n) and (m >= 0) and (m <= max_m) and state['map'][n][m] != 'I'


def get_all_passengers_the_taxi_can_pick(taxi_name, state):
    if state['taxis'][taxi_name]['capacity'] == 0:
        return []
    else:
        return [passenger_name for passenger_name, passenger_dict in state['passengers'].items()
                if passenger_dict['location'] == state['taxis'][taxi_name]['location']
                and passenger_dict['location'] != passenger_dict['destination']]


def get_all_passengers_the_taxi_can_drop(taxi_name, state):
    return [passenger_name for passenger_name, passenger_dict in state['passengers'].items()
            if passenger_dict['location'] == taxi_name and
            passenger_dict['destination'] == state['taxis'][taxi_name]['location']]


def get_all_atomic_actions(state):
    actions = []
    for t_name, t_dict in state['taxis'].items():
        n, m = t_dict['location']
        if t_dict['fuel'] > 0:
            neighbors = [(x, y) for (x, y) in [(n + 1, m), (n - 1, m), (n, m + 1), (n, m - 1)] if
                         location_is_legal(x, y, state)]
            actions.extend([Action('move', [t_name, (x, y)]) for x, y in neighbors])
        # pick
        actions.extend([Action('pick up', [t_name, passenger_name]) for
                        passenger_name in get_all_passengers_the_taxi_can_pick(t_name, state)])
        # drop
        actions.extend([Action('drop off', [t_name, passenger_name]) for
                        passenger_name in get_all_passengers_the_taxi_can_drop(t_name, state)])
        # refuel
        if state['map'][n][m] == 'G':
            actions.append(Action('refuel', [t_name]))
        # wait
        actions.append(Action('wait', [t_name]))
    return actions


def is_action_mutex(action):
    # not atomic action
    if type(action) == Action:
        return False
    # one action per taxi
    action = tuple([a.get_action() for a in action])
    if len(set([a[1] for a in action])) != len(action):
        return True
    # pick up the same person
    pick_actions = [a for a in action if a[0] == 'pick up']
    if len(pick_actions) > 1:
        passengers_to_pick = set([a[2] for a in pick_actions])
        if len(passengers_to_pick) != len(pick_actions):
            return True
    return False


def get_all_actions(state):
    actions = []
    # reset
    actions.append(Action('reset'))
    # terminate
    actions.append(Action('terminate'))
    # get atomic actions
    all_atomic_actions = get_all_atomic_actions(state)
    # compute all possible atomic actions combinations
    taxi_action_dict = dict(
        [(taxi_name, [a for a in all_atomic_actions if a.taxi == taxi_name]) for taxi_name in state['taxis'].keys()])
    all_combinations = list(product(*list(taxi_action_dict.values())))
    # filter out mutex actions
    all_combinations = [c for c in all_combinations if not is_action_mutex(c)]
    actions.extend(all_combinations)
    return actions


class TaxiAgent:
    def __init__(self, initial):
        self.initial = initial
        self.taxi_person_dict = {}
        for p in self.initial['passengers'].keys():
            t = random.choice(list(self.initial['taxis'].keys()))
            self.taxi_person_dict[t] = p

    def act(self, state):
        all_actions = get_all_actions(state)
        if random.random() < 0.5:
            chosen_action = random.choice(all_actions)
        else:
            action_heuristic = [heuristic(state, a) for a in all_actions]
            max_heuristic = max(action_heuristic)
            if max_heuristic > 0:
                chosen_action = all_actions[action_heuristic.index(max_heuristic)]
            else:
                chosen_action = random.choice(all_actions)
        if isinstance(chosen_action, tuple):
            return tuple([a.get_action() for a in chosen_action])
        elif isinstance(chosen_action, Action):
            return chosen_action.get_action()


def heuristic(state, action):
    if type(action) == tuple:
        return sum([heuristic(state, a) for a in action])
    elif type(action) == Action:
        if action.name == 'pick up':
            return 1
        elif action.name == 'drop off':
            return 1
        else:
            return 0  # move, refuel, wait, reset, terminate
