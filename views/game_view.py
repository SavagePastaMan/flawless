import arcade
import utils

from constants import *
from typing import Optional
from pyglet.gl import GL_NEAREST

from entity.cabinet import Cabinet
from entity.enemy import Enemy
from entity.player import Player

from item.key import Key


class GameView(arcade.View):
    def __init__(self, window):
        super().__init__(window)
        self.wall_list: Optional[arcade.SpriteList] = None
        self.floor_list: Optional[arcade.SpriteList] = None
        self.interactable_list: Optional[arcade.SpriteList] = None
        self.enemy_list: Optional[arcade.SpriteList] = None
        self.player: Optional[Player] = None

        self.setup()

    def setup(self):

        # Set up the player

        self.load_map()

        # Set up the player
        self.player = Player()

        # Starting position of the player
        self.player.center_x, self.player.center_y = utils.center_of_tile(135, 390)

        cabinet = Cabinet(content=Key())
        cabinet.center_x, cabinet.center_y = utils.center_of_tile(135, 300)
        self.interactable_list = arcade.SpriteList()
        self.interactable_list.append(cabinet)

        enemy = Enemy(self.wall_list)
        enemy.center_x, enemy.center_y = utils.center_of_tile(135, 500)
        self.enemy_list = arcade.SpriteList()
        self.enemy_list.append(enemy)

        self.set_viewport_on_player()

    def load_map(self):

        # Process Tile Map

        tile_map = arcade.tilemap.read_tmx(f"assets/tilemaps/TestLevel.tmx")

        # Tile Layers

        self.wall_list = arcade.tilemap.process_layer(
            tile_map, "walls", TILE_SPRITE_SCALING, use_spatial_hash=True
        )

        self.floor_list = arcade.tilemap.process_layer(
            tile_map, "floor", TILE_SPRITE_SCALING, use_spatial_hash=True
        )

        # Object Layers

        self.object_layers = utils.process_objects(f"assets/tilemaps/TestLevel.tmx")

        self.guard1_locations = utils.extract_guard_locations(self.object_layers[0])

    def on_key_press(self, key: int, modifiers: int):
        if key in [arcade.key.UP, arcade.key.LEFT, arcade.key.RIGHT, arcade.key.DOWN]:
            # Record Original Pos so if collision with wall is detected, we return the
            # player to that spot before rendering, making it impassable.
            original_pos = (self.player.center_x, self.player.center_y)
            self.player.handle_user_input(key, modifiers)
            if arcade.check_for_collision_with_list(self.player, self.wall_list):
                self.player.center_x, self.player.center_y = original_pos
            else:
                self.enemy_list.update()

            self.set_viewport_on_player()
        elif key == arcade.key.ESCAPE:
            from views import PauseView

            self.window.show_view(PauseView(self))

    def set_viewport_on_player(self):
        """
        Set the viewport to be over the player. If the Viewport would display the outside blackness,
        it is clamped with the game map.
        :return:
        """
        width, height = self.window.get_size()
        clamped_x = min(width, max(0, self.player.center_x - width // 2),)
        clamped_y = min(height, max(0, self.player.center_y - height // 2),)
        arcade.set_viewport(clamped_x, width + clamped_x, clamped_y, height + clamped_y)

    def on_update(self, delta_time: float):
        for interactable in arcade.check_for_collision_with_list(
            self.player, self.interactable_list
        ):
            interactable.interact(self.player)

        self.player.update()

    def on_draw(self):
        arcade.start_render()

        # GL_NEAREST makes scaled Pixel art look cleaner
        self.wall_list.draw(filter=GL_NEAREST)
        self.floor_list.draw(filter=GL_NEAREST)
        self.interactable_list.draw(filter=GL_NEAREST)

        self.enemy_list.draw(filter=GL_NEAREST)
        self.player.draw()