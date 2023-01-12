from copy import deepcopy
import logging


class Simulator:
    def __init__(self, initial_state):
        self.state = deepcopy(initial_state)
        self.score = [0, 0]
        self.dimensions = (len(self.state['map']), len(self.state['map'][0]))

    def neighbors(self, location):
        """
        return the neighbors of a location
        """
        y, x = location[0], location[1]
        neighbors = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
        for neighbor in neighbors:
            if neighbor[0] < 0 or neighbor[0] >= self.dimensions[1] or neighbor[1] < 0 or neighbor[1] >= self.dimensions[0] or self.state['map'][neighbor] != 'P':
                    neighbors.remove(neighbor)
        return neighbors

    def check_if_action_legal(self, action):
        def _is_move_action_legal(move_action):
            taxi_name = move_action[1]
            if taxi_name not in self.state['taxis'].keys():
                return False
            if self.state['taxis'][taxi_name]['fuel'] == 0:
                return False
            l1 = self.state['taxis'][taxi_name]['location']
            l2 = move_action[2]
            return l2 in self.neighbors(l1)

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
            self._apply_atomic_action(atomic_action)

    def _apply_atomic_action(self, atomic_action):
        """
        apply an atomic action to the state
        """
        taxi_name = atomic_action[1]
        if atomic_action[0] == 'move':
            self.state['taxis'][taxi_name]['location'] = atomic_action[2]
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

    def act(self, action):
        if self.check_if_action_legal(action):
            self.apply_action(action)
        else:
            raise ValueError(f"Illegal action {action}!")

    def print_scores(self):
        print(f"Scores: player 1: {self.score[0]}, player 2: {self.score[1]}")

    def print_state(self):
        print(f"State: {self.state}")

    def set_state(self, state):
        self.state = state

