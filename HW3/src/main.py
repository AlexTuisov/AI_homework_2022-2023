import itertools
import random

from dataclasses import dataclass
import hw3
import sample_agent
from copy import deepcopy
import time
import logging

CONSTRUCTOR_TIMEOUT = 60
ACTION_TIMEOUT = 5
DIMENSIONS = (10, 10)
PENALTY = 10000
DEFAULT_STEPS = 100



class Game:
    def __init__(self, an_input):
        self.ids = [hw3.ids, sample_agent.ids]
        self.state = deepcopy(self.initial_state)
        self.divide_map()
        self.score = [0, 0]
        self.agents = []

    def state_to_agent(self):
        state_as_list = []
        for i in range(DIMENSIONS[0]):
            state_as_list.append([] * DIMENSIONS[1])
            for j in range(DIMENSIONS[1]):
                state_as_list[i].append(self.state[(i + 1, j + 1)][0])
        return state_as_list

    def initiate_agent(self, module, first):
        start = time.time()
        agent = module.Agent(self.state_to_agent(), first)
        if time.time() - start > CONSTRUCTOR_TIMEOUT:
            self.handle_constructor_timeout(module.ids)
        return agent

    def get_action(self, agent):
        action = agent.act(self.state_to_agent())
        return action

    def check_if_action_legal(self, action):
        def _is_move_action_legal(move_action):
            taxi_name = move_action[1]
            if taxi_name not in self.state['taxis'].keys():
                return False
            if self.state['taxis'][taxi_name]['fuel'] == 0:
                return False
            l1 = self.state['taxis'][taxi_name]['location']
            l2 = move_action[2]
            return l2 in list(self.graph.neighbors(l1))

        def _is_pick_up_action_legal(pick_up_action):
            taxi_name = pick_up_action[1]
            passenger_name = pick_up_action[2]
            # check same position
            if self.state['taxis'][taxi_name]['location'] != self.state['passengers'][passenger_name]['location']:
                return False
            # check taxi capacity
            if self.state['taxis'][taxi_name]['capacity'] <= 0:
                return False
            # check passenger is not in his destination
            if self.state['passengers'][passenger_name]['destination'] == self.state['passengers'][passenger_name][
                'location']:
                return False
            return True

        def _is_drop_action_legal(drop_action):
            taxi_name = drop_action[1]
            passenger_name = drop_action[2]
            # check same position
            if self.state['taxis'][taxi_name]['location'] != self.state['passengers'][passenger_name][
                'destination']:
                return False
            # check passenger is in the taxi
            if self.state['passengers'][passenger_name]['location'] != taxi_name:
                return False
            return True

        def _is_action_mutex(global_action):
            assert type(global_action) == tuple, "global action must be a tuple"
            # one action per taxi
            if len(set([a[1] for a in global_action])) != len(global_action):
                return True
            # pick up the same person
            pick_actions = [a for a in global_action if a[0] == 'pick up']
            if len(pick_actions) > 1:
                passengers_to_pick = set([a[2] for a in pick_actions])
                if len(passengers_to_pick) != len(pick_actions):
                    return True
            return False

        if len(action) != len(self.state["taxis"].keys()):
            logging.error(f"You had given {len(action)} atomic commands, while there are {len(self.state['taxis'])}"
                          f" taxis in the problem!")
            return False
        for atomic_action in action:
            # illegal move action
            if atomic_action[0] == 'move':
                if not _is_move_action_legal(atomic_action):
                    logging.error(f"Move action {atomic_action} is illegal!")
                    return False
            # illegal pick action
            elif atomic_action[0] == 'pick up':
                if not _is_pick_up_action_legal(atomic_action):
                    logging.error(f"Pick action {atomic_action} is illegal!")
                    return False
            # illegal drop action
            elif atomic_action[0] == 'drop off':
                if not _is_drop_action_legal(atomic_action):
                    logging.error(f"Drop action {atomic_action} is illegal!")
                    return False
            elif atomic_action[0] != 'wait':
                return False
        # check mutex action
        if _is_action_mutex(action):
            logging.error(f"Actions {action} are mutex!")
            return False
        # check taxis collision
        if len(self.state['taxis']) > 1:
            taxis_location_dict = dict(
                [(t, self.state['taxis'][t]['location']) for t in self.state['taxis'].keys()])
            move_actions = [a for a in action if a[0] == 'move']
            for move_action in move_actions:
                taxis_location_dict[move_action[1]] = move_action[2]
            if len(set(taxis_location_dict.values())) != len(taxis_location_dict):
                logging.error(f"Actions {action} cause collision!")
                return False
        return True

    def apply_action(self, action):
        for atomic_action in action:
            self.apply_atomic_action(atomic_action)

    def apply_atomic_action(self, atomic_action):
        """
        apply an atomic action to the state
        """
        taxi_name = atomic_action[1]
        if atomic_action[0] == 'move':
            self.state['taxis'][taxi_name]['location'] = atomic_action[2]
            self.state['taxis'][taxi_name]['fuel'] -= 1
            return
        elif atomic_action[0] == 'pick up':
            passenger_name = atomic_action[2]
            self.state['taxis'][taxi_name]['capacity'] -= 1
            self.state['passengers'][passenger_name]['location'] = taxi_name
            return
        elif atomic_action[0] == 'drop off':
            passenger_name = atomic_action[2]
            self.state['passengers'][passenger_name]['location'] = self.state['taxis'][taxi_name]['location']
            self.state['taxis'][taxi_name]['capacity'] += 1
            self.score += self.state['passengers'][passenger_name]['reward']
            return
        elif atomic_action[0] == 'wait':
            return
        else:
            raise NotImplemented
    def change_state(self):
        new_state = deepcopy(self.state)
        self.state = new_state

    def handle_constructor_timeout(self, agent):
        raise Exception

    def get_legal_action(self, number_of_agent):
        start = time.time()
        action = self.get_action(self.agents[number_of_agent])
        finish = time.time()
        if finish - start > ACTION_TIMEOUT:
            self.score[number_of_agent] -= PENALTY
            print(f'agent of {self.ids[number_of_agent]} timed out on action!')
            return 'illegal'
        if not self.check_if_action_legal(action):
            self.score[number_of_agent] -= PENALTY
            print(f'agent of {self.ids[number_of_agent]} chose illegal action!')
            return 'illegal'
        return action

    def play_episode(self, swapped=False, length_of_episode=DEFAULT_STEPS):
        counter = MAXIMAL_LENGTH
        while (('S1' in self.state.values() or 'S2' in self.state.values() or 'S3' in self.state.values())
               and (counter > 0)):

            counter = counter - 1
            obs_state = self.state_to_agent()
            for line in obs_state:
                print(line)
            print()

            if not swapped:
                action = self.get_legal_action(0)
                if action == 'illegal':
                    return
                self.apply_action(action)
                print(f'player {self.ids[0]} uses {action}!')

                action = self.get_legal_action(1)
                if action == 'illegal':
                    return
                self.apply_action(action)
                print(f'player {self.ids[1]} uses {action}!')
            else:
                action = self.get_legal_action(1)
                if action == 'illegal':
                    return
                self.apply_action(action)
                print(f'player {self.ids[1]} uses {action}!')

                action = self.get_legal_action(0)
                if action == 'illegal':
                    return
                self.apply_action(action)
                print(f'player {self.ids[0]} uses {action}!')

            self.change_state()
            print('------')

    def play_game(self):
        print(f'***********  starting a first round!  ************ \n \n')
        self.agents = [self.initiate_agent(hw3, 'first'),
                       self.initiate_agent(sample_agent, 'second')]
        self.play_episode()

        print(f'***********  starting a second round!  ************ \n \n')
        self.state = deepcopy(self.initial_state)

        self.agents = [self.initiate_agent(hw3, 'second'),
                       self.initiate_agent(sample_agent, 'first')]

        self.play_episode(swapped=True)
        print(f'end of game!')
        return self.score


def main():
    an_input = {
        "turns to go": 50,
        'map': [['P', 'P', 'P', 'P', 'P'],
                ['P', 'I', 'P', 'G', 'P'],
                ['P', 'P', 'I', 'P', 'P'],
                ['P', 'P', 'P', 'I', 'P']],
        'taxis': {'taxi 1': {'location': (1, 3), 'fuel': 10, 'capacity': 3}},
        'passengers': {'Michael': {'location': (3, 4), 'destination': (2, 1),
                                   "possible_goals": ((2, 1), (3, 4))},
                       'Freyja': {'location': (0, 0), 'destination': (2, 1),
                                  "possible_goals": ((2, 1), (0, 0))}}
    },
    game = Game(an_input)
    results = game.play_game()
    print(f'Score for {hw3.ids} is {results[0]}, score for {sample_agent.ids} is {results[1]}')


if __name__ == '__main__':
    main()