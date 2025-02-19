from abc import abstractmethod
from os import path
from v002 import Enviroment_with_agents, pl
import numpy as np

from v002.Enviroment import Orientation


class WumpusWorld(Enviroment_with_agents):
    class _Hidden_Agent2(Enviroment_with_agents._Hidden_Agent):
        def _stop(self):
            self._send_message({'type': 'Fin',
                                'Description': 'Termina el juego'})
            self._should_stop = True

        def shoot(self):
            my_laberinth = self._Hidden_Agent__laberinth
            disparos = self.get_shoots()
            for i in list(my_laberinth._Enviroment_with_agents__objects_pointers):
                if type(i) == WumpusWorld.Wumpus:
                    wumpus = i
                    break
            if disparos >= 1:
                print("Has disparado una flecha")
                successful_shot = False

                # print(self.__dict__.keys())

                position_below = [wumpus.pos_y - 1, wumpus.pos_x]
                position_above = [wumpus.pos_y + 1, wumpus.pos_x]
                position_left = [wumpus.pos_y, wumpus.pos_x - 1]
                position_right = [wumpus.pos_y, wumpus.pos_x + 1]

                if wumpus.is_alive():
                    if self._get_position() == position_below and self.get_orientation() == Orientation.UP:
                        successful_shot = True
                    if self._get_position() == position_above and self.get_orientation() == Orientation.DOWN:
                        successful_shot = True
                    if self._get_position() == position_left and self.get_orientation() == Orientation.RIGHT:
                        successful_shot = True
                    if self._get_position() == position_right and self.get_orientation() == Orientation.LEFT:
                        successful_shot = True

                    if successful_shot:
                        print("La flecha SI le ha dado al Wumpus")
                        wumpus.die()
                        #self._environment._winner = agents[i]
                        #self._should_stop = True

                    if not successful_shot:
                        print("La flecha NO le ha dado al Wumpus")

                self._shoots -= 1
                print("Flechas restantes: " + str(self._shoots))

            else:
                if wumpus.is_alive():
                    print("NO has disparado una flecha. NO hay disparos suficientes")
                else:
                    print("NO has disparado una flecha. WUMPUS ya está muerto")

        def take_arrow(self):
            my_laberinth = self._Hidden_Agent__laberinth

            for i in list(my_laberinth._Enviroment_with_agents__objects_pointers):
                if type(i) == WumpusWorld.Arrow:
                    arrow = i
                    break
            if arrow._is_active == True:
                arrow.pick_up()
                self._arrow = True
                if self._arrow:
                    self._shoots += 1
                    print("+1 Flecha")

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
            self.__my_avatar = pl.imread(path.join("images",
                                                   "exit_image.jpg"))  # https://www.rawpixel.com/image/5917811/exit-sign-free-public-domain-cc0-photo

        def _exit(self, agent):
            hiden_agent = self._environment._Enviroment_with_agents__get_hidden_agent(agent, self)
            position = hiden_agent._get_position()
            if position[1] == self._pos_x and \
                    position[0] == self._pos_y:
                self._environment._exit_found = True
                self._environment._winner = hiden_agent
                hiden_agent._should_stop = True
                hiden_agent._send_message({'type': 'WIN', 'Description': '¡Has salido del laberinto!'})

        def plot(self):
            pl.plot(self._pos_x + 0.5, self._pos_y + 0.5, 'ro')
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

    class Wumpus(Enviroment_with_agents._Object):
        def __init__(self, pos_x, pos_y, environment):
            super().__init__(pos_x, pos_y, environment)
            self.__my_avatar = pl.imread(path.join("images", "Wumpus.png"))
            self.__my_avatar2 = pl.imread(path.join("images", "wumpus2.png"))
            self._alive = True

        def is_alive(self):
            if self._alive:
                return True
            else:
                return False

        def die(self):
            self._alive = False

        def get_alive(self):
            return self._alive

        def plot(self):
            if self.is_alive():
                pl.gca().imshow(self.__my_avatar,
                                extent=[self._pos_x + 0.2, self._pos_x + 0.8,
                                        self._pos_y + 0.2, self._pos_y + 0.8])
            else:
                pl.gca().imshow(self.__my_avatar2,
                                extent=[self._pos_x + 0.2, self._pos_x + 0.8,
                                        self._pos_y + 0.2, self._pos_y + 0.8])

        def _notify_time_iteration(self):
            agents = self._environment._Enviroment_with_agents__hidden_agents
            for i in agents:
                if agents[i]._Hidden_Agent__position == [self.pos_y, self.pos_x] and self._alive:
                    agents[i]._send_message({'type': 'Game Over', 'Description': 'El Wumpus te ha deborado'})
                    agents[i]._should_stop = True

        def _get_info(self):
            return {'type': 'wumpus', 'Description': 'Te has topado con el Wumpus y te ha deborado'}

    class _Hole(Enviroment_with_agents._Object):
        def __init__(self, pos_x, pos_y, environment):
            super().__init__(pos_x, pos_y, environment)
            self.__my_avatar = pl.imread(path.join("images", "hoyo.png"))

        def plot(self):
            pl.gca().imshow(self.__my_avatar,
                            extent=[self._pos_x + 0.2, self._pos_x + 0.8,
                                    self._pos_y + 0.2, self._pos_y + 0.8])

        def _notify_time_iteration(self):
            agents = self._environment._Enviroment_with_agents__hidden_agents
            for i in agents:
                if agents[i]._Hidden_Agent__position == [self.pos_y, self.pos_x]:
                    agents[i]._send_message({'type': 'Game Over', 'Description': 'Has caído en un hoyo sin fondo.'})
                    agents[i]._should_stop = True

        def _get_info(self):
            return {'type': 'hole', 'Description': 'Has caido en un agujero'}

    class _Wind(Enviroment_with_agents._Object):
        def __init__(self, pos_x, pos_y, environment):
            super().__init__(pos_x, pos_y, environment)
            self.__my_avatar = pl.imread(path.join("images", "wind.jpg"))

        def plot(self):
            pl.gca().imshow(self.__my_avatar,
                            extent=[self._pos_x + 0.2, self._pos_x + 0.8,
                                    self._pos_y + 0.2, self._pos_y + 0.8], alpha=0.5)

        def _notify_time_iteration(self):
            agents = self._environment._Enviroment_with_agents__hidden_agents
            for i in agents:
                if agents[i]._Hidden_Agent__position == [self.pos_y, self.pos_x]:
                    agents[i]._send_message({'type': 'Viento', 'Description': 'Se percibe viento en esta casilla. Debe de haber un hoyo cerca.'})

        def _get_info(self):
            return {'type': 'wind', 'Description': 'Hay un agujero cerca'}

    class _Stench(Enviroment_with_agents._Object):
        def __init__(self, pos_x, pos_y, environment):
            super().__init__(pos_x, pos_y, environment)
            self.__my_avatar = pl.imread(path.join("images", "stench.png"))

        def plot(self):
            pl.gca().imshow(self.__my_avatar,
                            extent=[self._pos_x + 0.2, self._pos_x + 0.8,
                                    self._pos_y + 0.2, self._pos_y + 0.8], alpha=0.5)

        def _notify_time_iteration(self):
            agents = self._environment._Enviroment_with_agents__hidden_agents
            for i in agents:
                if agents[i]._Hidden_Agent__position == [self.pos_y, self.pos_x]:
                    agents[i]._send_message({'type': 'Hedor', 'Description': 'Se percibe hedor en esta casilla. El Wumpus debe estar cerca.'})

        def _get_info(self):
            return {'type': 'stench', 'Description': 'Está el wumpus cerca'}

    class Arrow(Enviroment_with_agents._Object):
        def __init__(self, pos_x, pos_y, environment):
            super().__init__(pos_x, pos_y, environment)
            self.__my_avatar = pl.imread(path.join("images", "arrow.png"))
            self.__my_avatar2 = pl.imread(path.join("images", "transparent.png"))
            self._is_active = True

        def is_active(self):
            return self._is_active

        def pick_up(self):
            self._is_active = False

        def _notify_time_iteration(self):
            agents = self._environment._Enviroment_with_agents__hidden_agents
            for i in agents:
                if agents[i]._Hidden_Agent__position == [self.pos_y, self.pos_x] and self.is_active():
                    #self.__is_active = False
                    #agents[i]._arrow = True
                    agents[i]._send_message({'type': 'Flecha', 'Description': 'Has recogido una flecha del suelo'})

        def plot(self):
            if self.is_active():
                pl.gca().imshow(self.__my_avatar,
                                extent=[self._pos_x + 0.2, self._pos_x + 0.8,
                                        self._pos_y + 0.2, self._pos_y + 0.8], alpha=0.5)
            else:
                pl.gca().imshow(self.__my_avatar2,
                                extent=[self._pos_x + 0.2, self._pos_x + 0.8,
                                        self._pos_y + 0.2, self._pos_y + 0.8], alpha=0.5)

        def _get_info(self):
            return {'type': 'arrow', 'Description': 'Hay una flecha en el suelo'}

    class _Treasure(_Exit):
        def __init__(self, pos_x, pos_y, environment):
            super().__init__(pos_x, pos_y, environment)
            self.__my_avatar = pl.imread(path.join("images", "chest.png"))

        def plot(self):
            pl.gca().imshow(self.__my_avatar,
                            extent=[self._pos_x + 0.2, self._pos_x + 0.8,
                                    self._pos_y + 0.2, self._pos_y + 0.8])

    def __init__(self, size, laberinth, entry_at_border=True, exit_at_border=False, plot_run='every epoch',
                 move_protection=True, remove_walls_prob=0):
        moves_per_turn = 10 * size * size
        super().__init__(size, max_moves_per_turn=moves_per_turn,
                         no_adjacents_in_cluster=True,
                         show_construction=False,
                         food_ratio=0,
                         food_period=100000,
                         move_protection=move_protection,
                         plot_run=plot_run,
                         remove_walls_prob=remove_walls_prob)
        self.__laberinth = laberinth
        self._entry_at_border = entry_at_border
        self._exit_at_border = exit_at_border
        self._start_orientation = Orientation.UP
        self._exit_found = False
        self.times_visited = np.zeros((self._size[0], self._size[1]))

        pos_x = np.random.randint(self._size[0])
        pos_y = np.random.randint(self._size[1])

        num_wumpus = 1
        #num_holes = 1
        num_arrow = 1
        num_holes = np.random.randint(1, size / 2 - 1)

        if self._entry_at_border:
            axis = np.random.choice([0, 1])
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

        while True:
            pos_x, pos_y = self.random_position()
            wumpus_pos_x, wumpus_pos_y = self.random_position()
            hole_pos_x, hole_pos_y = self.random_position()
            arrow_pos_x, arrow_pos_y = self.random_position()

            if (pos_x, pos_y) != (wumpus_pos_x, wumpus_pos_y) and \
                    (pos_x, pos_y) != (hole_pos_x, hole_pos_y) and \
                    (pos_x, pos_y) != (arrow_pos_x, arrow_pos_y) and \
                    (pos_x, pos_y) != (self.entry.pos_x, self.entry.pos_y) and \
                    (wumpus_pos_x, wumpus_pos_y) != (hole_pos_x, hole_pos_y) and \
                    (wumpus_pos_x, wumpus_pos_y) != (arrow_pos_x, arrow_pos_y) and \
                    (wumpus_pos_x, wumpus_pos_y) != (self.entry.pos_x, self.entry.pos_y) and \
                    (hole_pos_x, hole_pos_y) != (arrow_pos_x, arrow_pos_y) and \
                    (hole_pos_x, hole_pos_y) != (self.entry.pos_x, self.entry.pos_y) and \
                    (arrow_pos_x, arrow_pos_y) != (self.entry.pos_x, self.entry.pos_y):
                break

        for i in range(num_wumpus):
            wumpus = self.Wumpus(wumpus_pos_x, wumpus_pos_y, self)
            self.addObject(wumpus, wumpus_pos_x, wumpus_pos_y)
            self.add_stench(wumpus_pos_x, wumpus_pos_y)
            wumpus_pos_x, wumpus_pos_y = self.random_position()
        for i in range(num_holes):
            hole = self._Hole(hole_pos_x, hole_pos_y, self)
            self.addObject(hole, hole_pos_x, hole_pos_y)
            self.add_wind(hole_pos_x, hole_pos_y)
            hole_pos_x, hole_pos_y = self.random_position()
        for i in range(num_arrow):
            arrow = self.Arrow(arrow_pos_x, arrow_pos_y, self)
            self.addObject(arrow, arrow_pos_x, arrow_pos_y)

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

    def random_position(self):
        x = np.random.randint(0, self._size[0] - 1)
        y = np.random.randint(0, self._size[1] - 1)
        return x, y

    def add_stench(self, pos_x, pos_y):
        right_stench_pos_x, right_stench_pos_y = pos_x + 1, pos_y
        down_stench_pos_x, down_stench_pos_y = pos_x, pos_y - 1
        left_stench_pos_x, left_stench_pos_y = pos_x - 1, pos_y
        up_stench_pos_x, up_stench_pos_y = pos_x, pos_y + 1

        right_stench = self._Stench(right_stench_pos_x, right_stench_pos_y, self)
        down_stench = self._Stench(down_stench_pos_x, down_stench_pos_y, self)
        left_stench = self._Stench(left_stench_pos_x, left_stench_pos_y, self)
        up_stench = self._Stench(up_stench_pos_x, up_stench_pos_y, self)

        if not self.exists_upperWall(pos_x, pos_y) and self.is_inTopLimit(up_stench_pos_x, up_stench_pos_y):
            self.addObject(up_stench, up_stench_pos_x, up_stench_pos_y)
        if not self.exists_bottomWall(pos_x, pos_y) and self.is_inBottomLimit(down_stench_pos_x, down_stench_pos_y):
            self.addObject(down_stench, down_stench_pos_x, down_stench_pos_y)
        if not self.exists_rightWall(pos_x, pos_y) and self.is_inRightLimit(right_stench_pos_x, right_stench_pos_y):
            self.addObject(right_stench, right_stench_pos_x, right_stench_pos_y)
        if not self.exists_leftWall(pos_x, pos_y) and self.is_inLeftLimit(left_stench_pos_x, left_stench_pos_y):
            self.addObject(left_stench, left_stench_pos_x, left_stench_pos_y)

    def add_wind(self, pos_x, pos_y):
        right_wind_pos_x, right_wind_pos_y = pos_x + 1, pos_y
        down_wind_pos_x, down_wind_pos_y = pos_x, pos_y - 1
        left_wind_pos_x, left_wind_pos_y = pos_x - 1, pos_y
        up_wind_pos_x, up_wind_pos_y = pos_x, pos_y + 1

        right_wind = self._Wind(right_wind_pos_x, right_wind_pos_y, self)
        down_wind = self._Wind(down_wind_pos_x, down_wind_pos_y, self)
        left_wind = self._Wind(left_wind_pos_x, left_wind_pos_y, self)
        up_wind = self._Wind(up_wind_pos_x, up_wind_pos_y, self)

        if not self.exists_upperWall(pos_x, pos_y) and self.is_inTopLimit(up_wind_pos_x, up_wind_pos_y):
            self.addObject(up_wind, up_wind_pos_x, up_wind_pos_y)
        if not self.exists_bottomWall(pos_x, pos_y) and self.is_inBottomLimit(down_wind_pos_x, down_wind_pos_y):
            self.addObject(down_wind, down_wind_pos_x, down_wind_pos_y)
        if not self.exists_rightWall(pos_x, pos_y) and self.is_inRightLimit(right_wind_pos_x, right_wind_pos_y):
            self.addObject(right_wind, right_wind_pos_x, right_wind_pos_y)
        if not self.exists_leftWall(pos_x, pos_y) and self.is_inLeftLimit(left_wind_pos_x, left_wind_pos_y):
            self.addObject(left_wind, left_wind_pos_x, left_wind_pos_y)

    '''Comprobamos si en las casillas adyacentes hay paredes o no'''

    def exists_upperWall(self, pos_x, pos_y):
        return self.__laberinth._top_panel_at(self, pos_y, pos_x)

    def exists_bottomWall(self, pos_x, pos_y):
        return self.__laberinth._top_panel_at(self, pos_y - 1, pos_x)

    def exists_leftWall(self, pos_x, pos_y):
        return self.__laberinth._east_panel_at(self, pos_y, pos_x - 1)

    def exists_rightWall(self, pos_x, pos_y):
        return self.__laberinth._east_panel_at(self, pos_y, pos_x)

    '''Controlamos que siempre estén dentro de los limites del laberinto'''

    def is_inTopLimit(self, up_pos_x, up_pos_y):
        if 0 <= up_pos_x < self._size[0] and 0 <= up_pos_y < self._size[1]:
            return True

    def is_inBottomLimit(self, down_pos_x, down_pos_y):
        if 0 <= down_pos_x < self._size[0] and 0 <= down_pos_y < self._size[1]:
            return True

    def is_inLeftLimit(self, left_pos_x, left_pos_y):
        if 0 <= left_pos_x < self._size[0] and 0 <= left_pos_y < self._size[1]:
            return True

    def is_inRightLimit(self, right_pos_x, right_pos_y):
        if 0 <= right_pos_x < self._size[0] and 0 <= right_pos_y < self._size[1]:
            return True

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

            if self._plot_run == 'every epoch':
                print(num_cells_visited)

        return len(self._Enviroment_with_agents__living_agent_ids) <= 0 or self._exit_found or \
            np.max([num_cells_visited[i] for i in num_cells_visited]) >= self._size[0] * self._size[
                1]

    def create_agent(self, name, shoots, agent_class):
        agent = WumpusWorld._Hidden_Agent2
        new_agent = super().create_agent(agent, name, shoots, agent_class,
                             self.entry.pos_y,
                             self.entry.pos_x,
                             self._start_orientation)

        return new_agent
