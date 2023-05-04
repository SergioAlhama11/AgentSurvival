import sys
from abc import ABC, abstractmethod
from os import path

from matplotlib import pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

from v002 import Enviroment_with_agents, pl
import numpy as np

from v002.Enviroment import Orientation


class WumpusWorld(Enviroment_with_agents):

    class _Entry(Enviroment_with_agents._Object):
        def __init__(self, pos_x, pos_y, environment):
            super().__init__(pos_x, pos_y, environment)

        def plot(self):
            pl.plot(self._pos_x + 0.5, self._pos_y + 0.5, 'go')  # punto verde

        def _get_info(self):
            return {'type': 'entry', 'Description': 'This is the entry of the laberinth'}

    class _Exit(Enviroment_with_agents._Object):
        def __init__(self, pos_x, pos_y, environment):
            super().__init__(pos_x, pos_y, environment)
            self.__my_avatar = pl.imread(path.join("images","exit_image.jpg")) # https://www.rawpixel.com/image/5917811/exit-sign-free-public-domain-cc0-photo

        def _exit(self, agent):
            hiden_agent = self._environment._Enviroment_with_agents__get_hidden_agent2(agent)
            position = hiden_agent._get_position()
            if position[1] == self._pos_x and \
                    position[0] == self._pos_y:
                self._environment._exit_found = True
                self._environment._winner = hiden_agent
                hiden_agent._should_stop = True
                hiden_agent._send_message({'type': 'success laberinth',
                                           'Description': 'You exited from the laberinth'})

        def plot(self):
            # pl.plot(self._pos_x + 0.5, self._pos_y + 0.5, 'ro') #punto rojo
            pl.gca().imshow(self.__my_avatar,
                            extent=[self._pos_x + 0.1, self._pos_x + 0.9,
                                    self._pos_y + 0.1, self._pos_y + 0.9])

        def _get_info(self):
            return {'type': 'exit', 'Description': 'This is the exit of the laberinth. '
                                                   'To finish, invoke the function in the field '
                                                   'exit_function with yourself as argument:'
                                                   '<this_dictionary>[\'exit_function\'](self). You\'d be sent a success message '
                                                   ' in '
                                                   'case you do it right. You would not, otherwise',
                    'exit_function': self._exit}

    class _GameOver(Enviroment_with_agents._Object):
        def __init__(self, pos_x, pos_y, environment):
            super().__init__(pos_x, pos_y, environment)
            self.__my_avatar = pl.imread(path.join("images","wumpus.png")) # https://www.rawpixel.com/image/5917811/exit-sign-free-public-domain-cc0-photo

        def _die(self, agent):
            hiden_agent = self._environment._Enviroment_with_agents__get_hidden_agent2(agent)
            position = hiden_agent._get_position()
            if position[1] == self._pos_x and \
                    position[0] == self._pos_y:
                self._environment._died = True
                self._environment._winner = hiden_agent
                hiden_agent._should_stop = True
                hiden_agent._send_message({'type': 'unsuccess laberinth',
                                           'Description': 'You died'})

        def plot(self):
            # pl.plot(self._pos_x + 0.5, self._pos_y + 0.5, 'ro') #punto rojo
            pl.gca().imshow(self.__my_avatar,
                            extent=[self._pos_x + 0.1, self._pos_x + 0.9,
                                    self._pos_y + 0.1, self._pos_y + 0.9])

        def _get_info(self):
            return {'type': 'gameOver', 'Description': 'This is the end of the game. '
                                                   'To finish, invoke the function in the field '
                                                   'exit_function with yourself as argument:'
                                                   '<this_dictionary>[\'exit_function\'](self). You\'d be sent a success message '
                                                   ' in '
                                                   'case you do it right. You would not, otherwise',
                    'die_function': self._die}

    class _Treasure(_Exit):
        def __init__(self, pos_x, pos_y, environment):
            super().__init__(pos_x, pos_y, environment)
            self.__my_avatar = pl.imread(path.join("images","chest.png"))

        def plot(self):
            # https://www.rawpixel.com/image/7371573
            pl.gca().imshow(self.__my_avatar,
                            extent=[self._pos_x + 0.2, self._pos_x + 0.8,
                                    self._pos_y + 0.2, self._pos_y + 0.8])

    def __init__(self, size, entry_at_border=True, exit_at_border=True, plot_run='every epoch',
                 move_protection = True,remove_walls_prob=0):
        moves_per_turn = 10*size*size
        super().__init__(size, max_moves_per_turn=moves_per_turn,
                         no_adjacents_in_cluster = True,
                         show_construction = False,
                         # entry_at_border = True,
                         # treasure_at_border = True,
                         food_ratio = 0.,
                         food_period = 100000,
                         move_protection = move_protection,
                         plot_run=plot_run,
                         remove_walls_prob=remove_walls_prob)

        self._entry_at_border = entry_at_border
        self._exit_at_border = exit_at_border
        self._start_orientation = Orientation.UP
        self._exit_found = False
        self.times_visited = np.zeros((self._size[0], self._size[1]))
        self.__objects = {}
        self.__objects_pointers = set()

        pos_x = np.random.randint(self._size[0])
        pos_y = np.random.randint(self._size[1])

        if self._entry_at_border:
            axis = np.random.choice([0,1])
            if axis == 0:
                pos_x = np.random.choice([0, self._size[axis] - 1])
                if pos_x == 0:
                    self._start_orientation = Orientation.RIGHT
                else:
                    self._start_orientation = Orientation.LEFT
            else:
                pos_y = np.random.choice([0, self._size[axis] - 1])
                if pos_y == 0:
                    self._start_orientation = Orientation.UP
                else:
                    self._start_orientation = Orientation.DOWN

        self.entry = self._Entry(pos_x, pos_y, self)
        self.addObject(self.entry, pos_x, pos_y)
        pos_x = np.random.randint(self._size[0])
        pos_y = np.random.randint(self._size[0])

        wumpus_pos_x = np.random.randint(self._size[0])
        wumpus_pos_y = np.random.randint(self._size[1])

        gameOver = self._GameOver(wumpus_pos_x, wumpus_pos_y, self)
        self.addObject(gameOver,wumpus_pos_x, wumpus_pos_y)

        if exit_at_border != 'no exit':
            if self._exit_at_border:
                axis = np.random.choice([0, 1])

                if axis == 0:
                    pos_x = np.random.choice([0, self._size[axis] - 1])
                else:
                    pos_y = np.random.choice([0, self._size[axis] - 1])

                exit = self._Exit(pos_x, pos_y, self)
                self.addObject(exit, pos_x, pos_y)
            else:
                treasure = self._Treasure(pos_x, pos_y, self)
                self.addObject(treasure, pos_x, pos_y)

        for i in range(self._size[0]):
            self.__objects[i] = {}
            for j in range(self._size[1]):
                self.__objects[i][j] = []

                if np.random.rand() < 0.3:
                    new_object = self.__Food(i, j, 10, self)
                    new_object = self.__Hole(i, j, self)
                    self.__objects_pointers.add(new_object)
                    self.__objects[i][j].append(new_object)


    def stop_condition(self):
        num_cells_visited = {'null': 0}
        if self._exit_at_border == 'no exit':
            agents = self._Enviroment_with_agents__hidden_agents
            first_agent_path = agents[list(agents.keys())[0]]._Hidden_Agent__path

            for i in range(self._size[0]):
                for j in range(self._size[1]):
                    self.times_visited[i][j] = np.sum([cell[0] == i + 0.5 and cell[1] == j + 0.5
                                           for cell in first_agent_path])

            num_cells_visited = {agents[i]._name:
                                     len(np.unique([str(j[0]) + str(j[1])
                                                    for j in agents[i]._Hidden_Agent__path]))
                                 for i in agents}

            if  self._plot_run == 'every epoch':
                print(num_cells_visited)


        return len(self._Enviroment_with_agents__living_agent_ids) <= 0 or self._exit_found or\
               np.max([num_cells_visited[i] for i in num_cells_visited]) >= self._size[0] * self._size[1]#(self._epoch > 10 * self._size[0] * self._size[1]) or self._exit_found

    def create_agent(self, name, agent_class, life=None):
        if life is None and self._exit_at_border == 'no exit':
            life = 10* self._size[0] * self._size[1]
        elif life is None:
            life = 10* self._size[0] * self._size[1]
        super().create_agent(name, agent_class,
                             self.entry._pos_y,
                             self.entry._pos_x,
                             self._start_orientation,
                             life=life)

    def plot(self, clear=True, time_interval=0.01):
        if clear:
            self._clear_plot()

        super().plot(False, time_interval, None)
        for ii in self.__objects:
            for jj in self.__objects[ii]:
                for kk in self.__objects[ii][jj]:
                    kk.plot()

        pl.gca().autoscale();
        if clear:
            self._show_plot(time_interval=time_interval)

    class _Object(ABC):
        def __init__(self, pos_x, pos_y, environment):
            self._pos_x = pos_x
            self._pos_y = pos_y
            self._environment = environment

        @abstractmethod
        def _get_info(self):
            pass

        @abstractmethod
        def plot(self):
            pass

        def _notify_time_iteration(self):
            pass

    class __Food(_Object):
        def __init__(self, pos_x, pos_y, period, environment):
            super().__init__(pos_x, pos_y, environment)
            self._period = period
            self._current_nutrients = period + 1
            self.__nutrients = period - 1
            self.__my_avatar = pl.imread("images/PixelTomato.bmp")
            self.__my_avatar_2 = pl.imread("images/PixelNoTomato.bmp")
            self.__is_active = True

        def is_active(self):
            if self.__is_active and self._current_nutrients > 0:
                return True
            elif self.__is_active:
                self.__is_active = False

            # No haya nutrientes o esté inactivo, se devuelve Falso
            return False


        def plot(self):
            if self.is_active():
                # pl.plot(self._pos_x + 0.5, self._pos_y + 0.5, 'go', markersize=3)
                pl.gca().imshow(self.__my_avatar,
                                extent=[self._pos_x + 0.2, self._pos_x + 0.8,
                                        self._pos_y + 0.2, self._pos_y + 0.8])
            else:
                pl.gca().imshow(self.__my_avatar_2,
                                extent=[self._pos_x + 0.2, self._pos_x + 0.8,
                                        self._pos_y + 0.2, self._pos_y + 0.8])

        def _eat(self, agent):
            hiden_agent = self._environment._Enviroment_with_agents__get_hidden_agent(agent, self)
            hiden_agent._check_and_increase_moves_per_turn() # This line should stop this function with an exception if too much moves have been consumed
            position = hiden_agent._get_position()
            num_moves = hiden_agent._get_num_moves()
            if position[1] == self._pos_x and \
                    position[0] == self._pos_y:
                    # and num_moves < self._environment._max_moves_per_turn:

                if self.is_active():
                    self._current_nutrients -= 1
                    hiden_agent._increase_life(1)#self.__nutrients)
                    hiden_agent._send_message({'type': 'life_bonus', 'amount': 1,#self.__nutrients,
                                               'Description': 'You have been given ' +
                                                              str(1) + #str(self.__nutrients) +
                                                              ' life points, because you have eaten food'})
                    return 1
                else:
                    hiden_agent._send_message({'type': 'life_bonus', 'amount': 0,
                                               'Description': 'You have been given ' + str(0) + ' life points, because you have eaten food'})
                    return 0

        def _notify_time_iteration(self):
            if not self.is_active():
                self._current_nutrients += 1

                if self._current_nutrients >= self.__nutrients:
                    self.__is_active = True

        def _get_info(self):
            if self.is_active():
                return {'type': 'food type 1',
                        'Description': 'This is a piece of food from a fixed source of food.'
                                                              ' You eat the food and 1) you get life points, and '
                                                              '2) in case you empty it, there will not be food for a number of epochs. '
                                                              'To eat it, you have to '
                                                              'invoke the function in the field eat_function with yourself as argument:'
                                                              '<this_dictionary>[\'eat_function\'](self). You\'d be sent a message '
                                                              'about the life_bonus in '
                                                              'case you do it right, You would not, otherwise. In addition,'
                                       'this function returns 1 in case of success, or 0 in case there is not more food',
                        'eat_function': self._eat}
            else:
                return None

    class __Hole(_Object):
        def __init__(self, pos_x, pos_y, environment):
            super().__init__(pos_x, pos_y, environment)
            self.__my_avatar = pl.imread("images/hole.png")

        def plot(self):
            pl.gca().imshow(self.__my_avatar,
                            extent=[self._pos_x + 0.2, self._pos_x + 0.8,
                                    self._pos_y + 0.2, self._pos_y + 0.8])

        def _die(self, agent):
            hidden_agent = self._environment._Enviroment_with_agents__get_hidden_agent(agent, self)
            hidden_agent._check_and_increase_moves_per_turn()  # This line should stop this function with an exception if too much moves have been consumed
            position = hidden_agent._get_position()
            num_moves = hidden_agent._get_num_moves()
            if position[1] == self._pos_x and position[0] == self._pos_y:
                print("AGUJERO!!!")

        def _notify_time_iteration(self):
            pass

        def _get_info(self):
            return {'type': 'hole', 'Description': 'Has caido en un agujero', 'hole_function': self._die}


class No_Walls_Laberinth(WumpusWorld):
    def __init__(self, size, plot_run = 'every epoch', move_protection=True):
        super().__init__(size, entry_at_border=False, exit_at_border=False,
                         plot_run=plot_run,
                         move_protection=move_protection)
        self._h_panels = np.zeros(self._size)
        self._v_panels = np.zeros(self._size)
        self._h_panels[self._size[0]-1,:] = 1
        self._v_panels[:,self._size[1]-1] = 1

    def _initClusters(self):
        return [], None, None
