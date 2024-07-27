import random
from typing import List, Union
import math
import json
from core.action import MoveAction, ShootAction, RotateBladeAction, SwitchWeaponAction, SaveAction
from core.consts import Consts
from core.game_state import GameState, PlayerWeapon, Point
from core.map_state import MapState


class MyBot:
     """
     (fr) Cette classe représente votre bot. Vous pouvez y définir des attributs et des méthodes qui 
          seront conservées entre chaque appel de la méthode `on_tick`.

     (en) This class represents your bot. You can define attributes and methods in it that will be kept 
          between each call of the `on_tick` method.
     """
     __map_state: MapState
     name : str
     blade_rotation_angle: float
     coin_count: int
     weapon_set: bool
     
     def __init__(self):
          self.name = "CaCaBourré"
          self.pos_player = None
          self.walls = set()
          self.dodge = False
          self.temp_x = None
          self.temp_y = None
          # Define the border walls
          border_walls = [
               # Bottom border
               {('y', 0), ('x_left', 0), ('x_right', 100)},
               # Top border
               {('y', 100), ('x_left', 0), ('x_right', 100)},
               # Left border
               {('x', 0), ('y_bottom', 0), ('y_top', 100)},
               # Right border
               {('x', 100), ('y_bottom', 0), ('y_top', 100)}
          ]
          # Add the border walls to the set
          for wall in border_walls:
               self.walls.add(tuple(wall))
          self.blade_rotation_angle = 0.0
          self.weapon_set = False


     def on_tick(self, game_state: GameState) -> List[Union[MoveAction, SwitchWeaponAction, RotateBladeAction, ShootAction, SaveAction]]:
          """
          (fr)    Cette méthode est appelée à chaque tick de jeu. Vous pouvez y définir 
                    le comportement de votre bot. Elle doit retourner une liste d'actions 
                    qui sera exécutée par le serveur.

                    Liste des actions possibles:
                    - MoveAction((x, y))        permet de diriger son bot, il ira a vitesse
                                                constante jusqu'à ce point.

                    - ShootAction((x, y))       Si vous avez le fusil comme arme, cela va tirer
                                                à la coordonnée donnée.

                    - SaveAction([...])         Permet de storer 100 octets dans le serveur. Lors
                                                de votre reconnection, ces données vous seront
                                                redonnées par le serveur.

                    - SwitchWeaponAction(id)    Permet de changer d'arme. Par défaut, votre bot
                                                n'est pas armé, voici vos choix:
                                                       PlayerWeapon.PlayerWeaponNone
                                                       PlayerWeapon.PlayerWeaponCanon
                                                       PlayerWeapon.PlayerWeaponBlade
                                                       
                    - BladeRotateAction(rad)    Si vous avez la lame comme arme, vous pouver mettre votre arme
                                                à la rotation donnée en radian.

          (en)    This method is called at each game tick. You can define your bot's behavior here. It must return a 
                    list of actions that will be executed by the server.

                    Possible actions:
                    - MoveAction((x, y))        Directs your bot to move to the specified point at a constant speed.

                    - ShootAction((x, y))       If you have the gun equipped, it will shoot at the given coordinates.

                    - SaveAction([...])         Allows you to store 100 bytes on the server. When you reconnect, these 
                                                data will be provided to you by the server.

                    - SwitchWeaponAction(id)    Allows you to change your weapon. By default, your bot is unarmed. Here 
                                                are your choices:
                                                  PlayerWeapon.PlayerWeaponNone
                                                  PlayerWeapon.PlayerWeaponCanon
                                                  PlayerWeapon.PlayerWeaponBlade
                    
                    - BladeRotateAction(rad)    if you have the blade as a weapon, you can set your
                                                weapon to the given rotation in radians.

          Arguments:
               game_state (GameState): (fr): L'état de la partie.
                                        (en): The state of the game.   
          """
          print(f"Current tick: {game_state.current_tick}")
          print(self.walls)
          # Get new position
          new_pos = self.find_player_coordinates(game_state.players, self.name)
          
          actions = []

          if not self.weapon_set:
            actions.append(SwitchWeaponAction(PlayerWeapon.PlayerWeaponCanon))
            self.weapon_set = True
        
          closest_coin = self.coin_finder(game_state, self.name)
          if closest_coin:
               print(f"Moving towards coin at position ({closest_coin.pos.x}, {closest_coin.pos.y})")
               x_dest, y_dest = closest_coin.pos.x, closest_coin.pos.y
               actions.append(MoveAction((x_dest, y_dest)))

          """ rotate_action = self.rotate_blade()
          actions.append(rotate_action) """

          shoot_action = self.pistol_aimer(game_state)
          if shoot_action:
               actions.append(shoot_action)
               actions.append(MoveAction(shoot_action.target_pos))
          print("HERE")
          if self.pos_player and new_pos.x == self.pos_player.x and new_pos.y == self.pos_player.y:
               new_wall = None
               if new_pos.x % 10 <= 1:
                    new_wall = {"x": math.floor(new_pos.x), "y_bottom": math.floor(new_pos.y / 10) * 10, "y_top": math.ceil(new_pos.y / 10) * 10}
               elif new_pos.x % 10 >= 9:
                    new_wall = {"x": math.ceil(new_pos.x), "y_bottom": math.floor(new_pos.y / 10) * 10, "y_top": math.ceil(new_pos.y / 10) * 10}
               elif new_pos.y % 10 <= 1:
                    new_wall = {"y": math.floor(new_pos.x), "x_left": math.floor(new_pos.x / 10) * 10, "x_right": math.ceil(new_pos.x / 10) * 10}
               elif new_pos.y % 10 >= 9:
                    new_wall = {"y": math.ceil(new_pos.y), "x_left": math.floor(new_pos.x / 10) * 10, "x_right": math.ceil(new_pos.x / 10) * 10}    

               if new_wall:
                    wall_tuple = tuple(new_wall.items())
                    if wall_tuple not in self.walls:
                         self.walls.add(wall_tuple)
                    self.dodge = True 
                    self.temp_x, self.temp_y = self.generate_new_coords(new_pos.x, new_pos.y)

          
          self.pos_player = new_pos

          if self.are_coordinates_close(self.temp_x, self.temp_y, new_pos.x, new_pos.y):
               self.dodge = False


          if self.dodge:
               x_dest = self.temp_x
               y_dest = self.temp_y
               
          actions.append(MoveAction((x_dest, y_dest)))

          """ actions = [
               MoveAction((x_dest, y_dest)),
               ShootAction((11.2222, 13.547)),
               SwitchWeaponAction(PlayerWeapon.PlayerWeaponBlade),
               SaveAction(b"Hello World"),
          ] """
                    
          return actions
    
    
     def on_start(self, map_state: MapState):
          """
          (fr) Cette méthode est appelée une seule fois au début de la partie. Vous pouvez y définir des
               actions à effectuer au début de la partie.

          (en) This method is called once at the beginning of the game. You can define actions to be 
               performed at the beginning of the game.

          Arguments:
               map_state (MapState): (fr) L'état de la carte.
                                   (en) The state of the map.
          """
          self.__map_state = map_state
          pass


     def on_end(self):
          """
          (fr) Cette méthode est appelée une seule fois à la fin de la partie. Vous pouvez y définir des
               actions à effectuer à la fin de la partie.

          (en) This method is called once at the end of the game. You can define actions to be performed 
               at the end of the game.
          """
          """ add a save call when the game is over to store our bytes to the server """
          save_data = json.dumps({'coin_count': self.coin_count}).encode('utf-8')
          return [SaveAction(save_data)]

     """ action helpers """
     def find_player_coordinates(self, players, player_name):
          for player in players:
               if player.name == player_name:
                    return player.pos
          return None  # If player is not found

     def coin_finder(self, state, self_name):
          closest_coin = None
          dist_min = float('inf')
          pos_self = self.find_player_coordinates(state.players, self_name)
          for coin in state.coins:
               dist = self.calculate_distance(pos_self, coin.pos)
               if dist < dist_min:
                    dist_min = dist
                    closest_coin = coin
          return closest_coin
     
     def rotate_blade(self) -> RotateBladeAction:
        self.blade_rotation_angle += math.pi / 16 
        if self.blade_rotation_angle >= 2 * math.pi:
            self.blade_rotation_angle -= 2 * math.pi
        return RotateBladeAction(self.blade_rotation_angle)
     
     def pistol_aimer(self, game_state: GameState) -> Union[ShootAction, None]:
        closest_enemy = None
        dist_min = float('inf')
        pos_self = self.find_player_coordinates(game_state.players, self.name)
        for player in game_state.players:
            if player.name != self.name:
                dist = self.calculate_distance(pos_self, player.pos)
                if dist < dist_min:
                    dist_min = dist
                    closest_enemy = player

        if closest_enemy:
            return ShootAction((closest_enemy.pos.x, closest_enemy.pos.y))
        return None  

     """ utils """
     def calculate_distance(self, pos1: Point, pos2: Point) -> float:
        return math.sqrt((pos1.x - pos2.x) ** 2 + (pos1.y - pos2.y) ** 2)
     
     def generate_new_coords(self, old_x, old_y, delta=10):
          new_x = old_x + random.uniform(-delta, delta)
          new_y = old_y + random.uniform(-delta, delta)
          while self.is_wall_in_between(old_x, old_y, new_x, new_y):
               new_x = old_x + random.uniform(-delta, delta)
               new_y = old_y + random.uniform(-delta, delta)
          return new_x, new_y
     
     def are_coordinates_close(self, temp_x, temp_y, new_pos_x, new_pos_y, tolerance=1):
          distance = math.sqrt((temp_x - new_pos_x) ** 2 + (temp_y - new_pos_y) ** 2)
          return distance <= tolerance
     
     def is_wall_in_between(self, old_x, old_y, new_x, new_y):
        for wall in self.walls:
            wall_dict = dict(wall)
            if 'x' in wall_dict:
                wall_x = wall_dict['x']
                y_bottom = wall_dict['y_bottom']
                y_top = wall_dict['y_top']
                if min(old_x, new_x) <= wall_x <= max(old_x, new_x) and min(old_y, new_y) <= y_top and max(old_y, new_y) >= y_bottom:
                    return True
            if 'y' in wall_dict:
                wall_y = wall_dict['y']
                x_left = wall_dict['x_left']
                x_right = wall_dict['x_right']
                if min(old_y, new_y) <= wall_y <= max(old_y, new_y) and min(old_x, new_x) <= x_right and max(old_x, new_x) >= x_left:
                    return True
        return False
        