import Simulator
# import hw3
# import sample_agent
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
        for step in range(length_of_episode):
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