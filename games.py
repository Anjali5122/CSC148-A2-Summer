from __future__ import annotations
import random
from typing import Dict, Union, Optional
import players
from trees import QuadTree, TwoDTree, OutOfBoundsError


class Game:

    def handle_collision(self, player1: str, player2: str) -> None:
        """ Perform some action when <player1> and <player2> collide """
        raise NotImplementedError

    def check_for_winner(self) -> Optional[str]:
        """ Return the name of the player or group of players that have
        won the game, or None if no player has won yet """
        raise NotImplementedError


class Tag(Game):
    """ A Tag game class which is a subclass of Game.

    == Attributes ==
    _players: A dictionary mapping the names of players to their Player instances
    field: A tree that stores the location of all players in _players
    _it: The name of the player in _players that is currently ‘it’
    _duration: The amount of time before the game eliminates some more players

    == Representation Invariants ==
    - there should be exactly n_players elements in the _players attribute
    - the _duration parameter should be set to duration
    - an empty tree that will be used to keep track of the player’s positions
    (the initializer should fill in this empty tree with the player’s positions)
     The field attribute should reference this tree.
    - randomly select a player to be ‘it’ and set the _it attribute accordingly
    - for each player, randomly set their speed to be between 1 and max_speed
    - for each player, randomly set their vision to be between 0 and max_vision
    """

    _players: Dict[str, players.Player]
    field: Union[QuadTree, TwoDTree]
    _it: str
    _duration: int

    def __init__(self, n_players: int,
                 field_type: Union[QuadTree, TwoDTree],
                 duration: int,
                 max_speed: int,
                 max_vision: int) -> None:
        """Initalize the tag game with <n_player>, <field_type>, <duration>,
        <max_speed> and <max_vision>.

        >>> t = Tag(4, TwoDTree((0,0), (200, 200)) , 3, 1, 1)
        >>> t._duration == 3
        True
        >>> t._it in t._players
        True
        >>> t._players[t._it].get_enemies()
        []
        >>> t._players[t._it].get_targets()
        ['p_0', 'p_1', 'p_2']
        """

        self.field = field_type
        temp_loc_list, temp_players_list = self._init_helper(n_players)
        self._duration = duration
        self._players = {}

        for i in range(n_players):
            vision = random.randint(0, max_vision)
            speed = random.randint(0, max_speed)
            self._players[temp_players_list[i]] = players.Player(temp_players_list[i], vision, speed, self, 'green', temp_loc_list[i])
            # temp_players_list.append(name)

        it = random.choice(temp_players_list)
        temp_players_list.remove(it)
        self._players[it].set_colour('purple')

        for item in temp_players_list:
            self._players[it].select_target(item)

        for item in self._players:
            if item != it:
                self._players[item].select_enemy(it)

        self._it = it

    def _init_helper(self, n):

        new = []
        names = []
        i = 0
        while len(new) < n:
            try:
                name = 'p_' + str(i)
                location = (random.randint(0, 500),
                            random.randint(0, 500))
                self.field.insert(name, location)
                new.append(location)
                names.append(name)
                i += 1
            except OutOfBoundsError:
                pass

        return new, names


    def check_for_winner(self) -> Optional[str]:
        """ Return the name of the player or group of players that have
        won the game, or None if no player has won yet

        >>> t = Tag(4, TwoDTree(), 3, 1, 1)
        >>> for item in t._players:
        >>>     if item != 'p_0':
        >>>         t._players[player].increase_points(10)
        >>> t.check_for_winner()
        'p_0'
        """

        if len(self._players) > 2:
            for key in self._players:
                if self._players[key].get_points() >= 1:
                    self.field.remove(key)
                    s = self._players.pop(key)

            #balance the tree

        else:
            winners = []
            for player in self._players:
                winners.append(player)

            if len(winners) == 1:
                return winners[0]
            if len(self._players) == 2:
                if winners[0] != self._it:
                    return winners[0]
                else:
                    return winners[-1]

    def handle_collision(self, player1: str, player2: str) -> None:
        """ Perform some action when <player1> and <player2> collide """

        if player1 == self._it:

            #change the self._it attribute to player 1
            self._it = player2
            #since p2 is now it, change there colour to purple
            self._players[player2].set_colour('purple')
            self._players[player2].increase_points(1) #whose points are increaseing? the new it person?

            #change p1s colour to green since they are not it anymore
            self._players[player1].set_colour('green')

            #get the list of targets for it
            its_targets = self._players[player1].get_targets()
            for item in its_targets:
                self._players[player2].select_target(item)
                self._players[player1].ignore_target(item)

            self._players[player2].select_target(player1)
            self._players[player2].ignore_enemy(player1)

            for item in self._players:
                if item != self._it:
                    self._players[item].ignore_enemy(player1)
                    self._players[item].select_enemy(player2)

        elif player2 == self._it:
            self._it = player1
            self._players[player1].set_colour('purple')
            self._players[player1].increase_points(1) #whose points are increaseing? the new it person?
            self._players[player2].set_colour('green')

            its_targets = self._players[player2].get_targets()
            for item in its_targets:
                self._players[player1].select_target(item)
                self._players[player2].ignore_target(item)

            self._players[player1].select_target(player1)
            self._players[player1].ignore_enemy(player1)

            for item in self._players:
                if item != self._it:
                    self._players[item].ignore_enemy(player2)
                    self._players[item].select_enemy(player1)

        self._players[player1].reverse_direction()
        self._players[player2].reverse_direction()


class ZombieTag(Game):
    _humans: Dict[str, players.Player]
    _zombies: Dict[str, players.Player]
    field: Union[QuadTree, TwoDTree]
    _duration: int

    def __init__(self, n_players: int,
                 field_type: Union[QuadTree, TwoDTree],
                 duration: int,
                 max_speed: int,
                 max_vision: int) -> None:

        self.field = field_type
        temp_loc_list, temp_players_list = self._init_helper(n_players)
        self._humans = {}
        self._zombies = {}
        self._duration = duration

        self._zombies[temp_players_list[-1]] = players.Player(temp_players_list[-1], max_vision, 1, self, 'purple', temp_loc_list[-1])

        for i in range(n_players):
            name = "p_" + str(i)
            vision = random.randint(0, max_vision)
            speed = random.randint(0, max_speed)
            # location = (random.randint(min_loc[0], max_loc[0]),
            #              random.randint(min_loc[1], max_loc[1]))
            # self.field.insert(name, location)
            self._humans[name] = players.Player(temp_players_list[i], vision, speed, self, 'green', temp_loc_list[i])
            self._humans[name].select_enemy(temp_players_list[-1])

        for item in temp_players_list:
            self._zombies[temp_players_list[-1]].select_target(item)

    def _init_helper(self, n):

        new = []
        i = 0
        names = []
        while len(new) < n+1:
            try:
                name = 'p_' + str(i)
                location = (random.randint(0, 500),
                            random.randint(0, 500))
                self.field.insert(name, location)
                new.append(location)
                names.append(name)
                i += 1
            except OutOfBoundsError:
                pass

        return new, names

    def handle_collision(self, player1: str, player2: str) -> None:
        """ Perform some action when <player1> and <player2> collide """

        if player1 in self._zombies and player2 in self._humans:
            self._zombies[player1].reverse_direction()
            self._humans[player2].reverse_direction()

            new_zombie = self._humans.pop(player2)
            self._zombies[player2] = new_zombie
            self._zombies[player2].set_speed(1)

            #updating all humans enemies
            new_targets = []
            for item in self._humans:
                self._humans[item].select_enemy(player2)
                new_targets.append(item)

            #setting new zombies new targets
            for item in new_targets:
                self._zombies[player2].select_target(item)

            #removing all enemies of new_zombie
            remove_enemies = self._zombies[player2].get_enemies()
            for item in remove_enemies:
                self._zombies[player2].ignore_enemy(item)

        elif player2 in self._zombies and player1 in self._humans:
            self._zombies[player2].reverse_direction()
            self._humans[player1].reverse_direction()

            new_zombie = self._humans.pop(player1)
            self._zombies[player1] = new_zombie
            self._zombies[player1].set_speed(1)

            # updating all humans enemies
            new_targets = []
            for item in self._humans:
                self._humans[item].select_enemy(player1)
                new_targets.append(item)

            # setting new zombies new targets
            for item in new_targets:
                self._zombies[player1].select_target(item)

            # removing all enemies of new_zombie
            remove_enemies = self._zombies[player1].get_enemies()
            for item in remove_enemies:
                self._zombies[player1].ignore_enemy(item)

        else:
            if player1 in self._zombies:
                self._zombies[player1].reverse_direction()
                self._zombies[player2].reverse_direction()
            else:
                self._humans[player1].reverse_direction()
                self._humans[player2].reverse_direction()

    def check_for_winner(self) -> Optional[str]:
        """ Return the name of the player or group of players that have
        won the game, or None if no player has won yet """

        if len(self._humans) > 0:
            return 'humans'
        return "zombies"


class EliminationTag(Game):
    _players: Dict[str, Player]
    field: Union[QuadTree, TwoDTree]

    def __init__(self, n_players: int,
                 field_type: Union[QuadTree, TwoDTree],
                 max_speed: int,
                 max_vision: int) -> None:

        self.field = field_type
        temp_loc_list, temp_players_list = self._init_helper(n_players)
        self._players = {}

        # if isinstance(self.field, TwoDTree):
        #     max_loc = self.field._se
        #     min_loc = self.field._nw
        # else:
        #     max_loc = (self.field._centre * 2, self.field._centre *2)
        #     min_loc = (0,0)

        for i in range(n_players):

            vision = random.randint(0, max_vision)
            speed = random.randint(0, max_speed)
            # location = (random.randint(min_loc[0], max_loc[0]),
            #              random.randint(min_loc[1], max_loc[1]))
            # self.field.insert(name, location)
            self._players[temp_players_list[i]] = players.Player(temp_players_list[i], vision, speed, self, 'random', temp_loc_list[i])

            if i != n_players - 1:
                target = temp_players_list[i+1]
                self._players[temp_players_list[i]].select_target(target)
            if i != 0:
                enemy = temp_players_list[i-1]
                self._players[temp_players_list[i]].select_enemy(enemy)

        self._players[temp_players_list[0]].select_enemy(temp_players_list[-1])
        self._players[temp_players_list[-1]].select_target(temp_players_list[0])

    def _init_helper(self, n):

        new = []
        i = 0
        names = []
        while len(new) < n:
            try:
                name = 'p_' + str(i)
                location = (random.randint(0, 500),
                            random.randint(0, 500))
                self.field.insert(name, location)
                new.append(location)
                names.append(name)
                i += 1
            except OutOfBoundsError:
                pass

        return new, names

    def handle_collision(self, player1: str, player2: str) -> None:
        """ Perform some action when <player1> and <player2> collide """

        if player1 in self._players[player2].get_targets():
            self._players[player2].ignore_target(player1)
            new_target = self._players[player1].get_targets()
            self._players[player2].select_target(new_target[0])
            self._players[player2].increase_points(1)
            s = self._players.pop(player1)      #by elimination they mean remove from players list?

        elif player2 in self._players[player1].get_targets():
            self._players[player1].ignore_target(player2)
            new_target = self._players[player2].get_targets()
            self._players[player1].select_target(new_target[0])
            self._players[player1].increase_points(1)
            s = self._players.pop(player2)

        else:
            self._players[player1].reverse_direction()
            self._players[player2].reverse_direction()

    def check_for_winner(self) -> Optional[str]:
        """ Return the name of the player or group of players that have
        won the game, or None if no player has won yet """

        winners = []        #docstring says something different then the document of the assignment
        max_points = 0
        for item in self._players:
            temp = self._players[item].get_points()
            if temp > max_points:
                max_points = temp

        for item in self._players:
            temp = self._players[item].get_points()
            if temp == max_points:
                winners.append(item)

        if len(winners) == 1:
            return winners[0]


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(
        config={'extra-imports': ['random', 'typing', 'players', 'trees']})
