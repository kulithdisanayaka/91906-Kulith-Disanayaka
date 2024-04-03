"""
Platformer Game
"""
import arcade

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
SCREEN_TITLE = "Platformer"

# Constants used to scale our sprites from their original size
CHARACTER_SCALING = 1
TILE_SCALING = 1.5
COIN_SCALING = 0.5
SPRITE_PIXEL_SIZE = 32
GRID_PIXEL_SIZE = SPRITE_PIXEL_SIZE * TILE_SCALING

# Movement speed of player, in pixels per frame
PLAYER_MOVEMENT_SPEED = 8
GRAVITY = 1.4
PLAYER_JUMP_SPEED = 20

player_on_ladder = False


# Player starting position

PLAYER_START_X = 64

PLAYER_START_Y = 450

# Constants used to track if the player is facing left or right
RIGHT_FACING = 0
LEFT_FACING = 1


# Layer Names from our TileMap

LAYER_NAME_PLATFORMS = "Platforms"

LAYER_NAME_COINS = "Coins"

LAYER_NAME_BACKGROUND = "Background"

LAYER_NAME_DONT_TOUCH = "Don't Touch"

LAYER_NAME_LADDERS = "Ladder"

LAYER_NAME_PLAYER = "Player"


def load_texture_pair(filename):
    """
    Load a texture pair, with the second being a mirror image.
    """
    return [
        arcade.load_texture(filename),
        arcade.load_texture(filename, flipped_horizontally=True),
    ]


class Player_Character(arcade.Sprite):
    """Player Sprite"""

    def __init__(self):

        # Set up parent class
        super().__init__()

        # Default to face-right
        self.character_face_direction = RIGHT_FACING

        # Used for flipping between image sequences
        self.cur_texture = 0
        self.scale = CHARACTER_SCALING

        # Track our state
        self.jumping = False
        self.climbing = False
        self.is_on_ladder = False

        # --- Load Textures ---

        # Images from Kenney.nl's Asset Pack 3
        main_path = "Character/"

         # Load initial texture for idle standing
        self.idle_texture_pair = load_texture_pair(
            f"{main_path}idle/idle (1).png"
        )

        # load texture for idle stand
        self.idle_textures = []
        for i in range(6):
            texture = load_texture_pair(f"{main_path}\idle\idle ({i}).png")
            self.idle_textures.append(texture)

        # Load textures for walking
        self.walk_textures = []
        for i in range(8):
            texture = load_texture_pair(f"{main_path}run/run ({i}).png")
            self.walk_textures.append(texture)

        # load texture for jumping
        self.jumping_textures = []
        for i in range(12):
            texture = load_texture_pair(f"{main_path}\jump\jump ({i}).png")
            self.jumping_textures.append(texture)

        # Load textures for climbing
        # self.climbing_textures = []
        # texture = arcade.load_texture(f"{main_path}_climb0.png")
        # self.climbing_textures.append(texture)
        # texture = arcade.load_texture(f"{main_path}_climb1.png")
        # self.climbing_textures.append(texture)

        # Set the initial texture
        self.texture = self.idle_texture_pair[0]

        # Hit box will be set based on the first image used. If you want to specify
        # a different hit box, you can do it like the code below.
        # set_hit_box = [[-22, -64], [22, -64], [22, 28], [-22, 28]]
        self.hit_box = self.texture.hit_box_points

    def update_animation(self, delta_time: float = 1 / 60):

        # Figure out if we need to flip face left or right
        if self.change_x < 0 and self.character_face_direction == RIGHT_FACING:
            self.character_face_direction = LEFT_FACING
            self.texture = self.idle_texture_pair[1]
            self.hit_box = self.texture.hit_box_points
        elif self.change_x > 0 and self.character_face_direction == LEFT_FACING:
            self.character_face_direction = RIGHT_FACING
            self.texture = self.idle_texture_pair[0]
            self.hit_box = self.texture.hit_box_points

        # Walking animation
        if self.change_x != 0 and self.change_y == 0:
            self.cur_texture += 1
            if self.cur_texture > 7 * 3:
                self.cur_texture = 0
            frame = self.cur_texture // 3
            self.texture = self.walk_textures[frame][
                self.character_face_direction
            ]
        # Jumping and fall animation
        if self.change_y > 1:
            self.cur_texture += 1
            if self.cur_texture > 11:
                self.cur_texture = 0
            frame = self.cur_texture // 1
            self.texture = self.jumping_textures[frame][
                self.character_face_direction
            ]



class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self):

        # Call the parent class and set up the window
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # Our TileMap Object
        self.tile_map = None

        # Our Scene Object
        self.scene = None

        # Separate variable that holds the player sprite
        self.player_sprite = None

        # Our physics engine
        self.physics_engine = None

        # A Camera that can be used for scrolling the screen
        self.camera = None

        # A Camera that can be used to draw GUI elements
        self.gui_camera = None

        # Keep track of the score
        self.score = 0


        # Do we need to reset the score?

        self.reset_score = True



        # Where is the right edge of the map?

        self.end_of_map = 0


        # Level
        self.level = 1


        # Load sounds

        self.collect_coin_sound = arcade.load_sound(":resources:sounds/coin1.wav")
        self.jump_sound = arcade.load_sound(":resources:sounds/jump1.wav")
        self.game_over = arcade.load_sound(":resources:sounds/gameover1.wav")

    def setup(self):
        """Set up the game here. Call this function to restart the game."""

        # Set up the Cameras

        self.camera = arcade.Camera(self.width, self.height)

        self.gui_camera = arcade.Camera(self.width, self.height)



        # Map name

        map_name = f"./maps/map_level_{self.level}.tmx"

        

        # Layer Specific Options for the Tilemap

        layer_options = {

            LAYER_NAME_PLATFORMS: {

                "use_spatial_hash": True,

            },

            LAYER_NAME_COINS: {

                "use_spatial_hash": True,

            },

            LAYER_NAME_DONT_TOUCH: {

                "use_spatial_hash": True,
            },

            LAYER_NAME_LADDERS: {
                "use_spatial_hash": True,
            }
        }

        # Load in TileMap
        self.tile_map = arcade.load_tilemap(map_name, TILE_SCALING, layer_options)

        # Initiate New Scene with our TileMap, this will automatically add all layers
        # from the map as SpriteLists in the scene in the proper order.
        self.scene = arcade.Scene.from_tilemap(self.tile_map)


        # Keep track of the score, make sure we keep the score if the player finishes a level

        if self.reset_score:

            self.score = 0

        self.reset_score = True



        # Set up the player, specifically placing it at these coordinates.
        self.player_sprite = Player_Character()
        self.player_sprite.center_x = PLAYER_START_X
        self.player_sprite.center_y = PLAYER_START_Y
        self.scene.add_sprite("Player", self.player_sprite)


        # --- Load in a map from the tiled editor ---

        # Calculate the right edge of the my_map in pixels
        self.end_of_map = self.tile_map.width * GRID_PIXEL_SIZE

        # --- Other stuff
        # Set the background color
        if self.tile_map.background_color:

            arcade.set_background_color(self.tile_map.background_color)


        # Create the 'physics engine'
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite,
            gravity_constant=GRAVITY,
            walls=self.scene[LAYER_NAME_PLATFORMS],
            ladders=self.scene[LAYER_NAME_LADDERS],
        )

    def on_draw(self):
        """Render the screen."""

        # Clear the screen to the background color
        self.clear()

        # Activate the game camera
        self.camera.use()

        # Draw our Scene
        self.scene.draw()

        # Activate the GUI camera before drawing GUI elements
        self.gui_camera.use()

        # Draw our score on the screen, scrolling it with the viewport
        score_text = f"Score: {self.score}"
        arcade.draw_text(
            score_text,
            10,
            10,
            arcade.csscolor.BLACK,
            18,
        )

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed."""

        if key == arcade.key.UP or key == arcade.key.W:
            if self.physics_engine.is_on_ladder():
                self.player_sprite.change_y = PLAYER_MOVEMENT_SPEED
            elif self.physics_engine.can_jump():
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
                arcade.play_sound(self.jump_sound)
        elif key == arcade.key.DOWN or key == arcade.key.S:
            if self.physics_engine.is_on_ladder():
                self.player_sprite.change_y = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key."""
        if key == arcade.key.UP or key == arcade.key.W:
            if self.physics_engine.is_on_ladder():
                self.player_sprite.change_y = 0
        elif key == arcade.key.DOWN or key == arcade.key.S:
            if self.physics_engine.is_on_ladder():
                self.player_sprite.change_y = 0
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x = 0
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = 0

    def center_camera_to_player(self):
        screen_center_x = self.player_sprite.center_x - (self.camera.viewport_width / 2)
        screen_center_y = self.player_sprite.center_y - (
            self.camera.viewport_height / 2
        )
        if screen_center_x < 0:
            screen_center_x = 0
        if screen_center_y < 0:
            screen_center_y = 0
        player_centered = screen_center_x, screen_center_y

        self.camera.move_to(player_centered)

    def update(self, delta_time):
        """Movement and game logic"""

        # Move the player with the physics engine
        self.physics_engine.update()

        # See if we hit any coins
        coin_hit_list = arcade.check_for_collision_with_list(
            self.player_sprite, self.scene[LAYER_NAME_COINS]
        )

        # Loop through each coin we hit (if any) and remove it
        for coin in coin_hit_list:
            # Remove the coin
            coin.remove_from_sprite_lists()

            # Play a sound

            arcade.play_sound(self.collect_coin_sound)

            # Add one to the score

            self.score += 1
    


        # Did the player fall off the map?

        if self.player_sprite.center_y < -100:

            self.player_sprite.center_x = PLAYER_START_X

            self.player_sprite.center_y = PLAYER_START_Y



            arcade.play_sound(self.game_over)



        # Did the player touch something they should not?

        if arcade.check_for_collision_with_list(

            self.player_sprite, self.scene[LAYER_NAME_DONT_TOUCH]

        ):

            self.player_sprite.change_x = 0

            self.player_sprite.change_y = 0

            self.player_sprite.center_x = PLAYER_START_X

            self.player_sprite.center_y = PLAYER_START_Y



            arcade.play_sound(self.game_over)

        # Update Animations
        self.scene.update_animation(
            delta_time, [LAYER_NAME_COINS, LAYER_NAME_BACKGROUND, LAYER_NAME_PLAYER]
        )


        # See if the user got to the end of the level

        if self.player_sprite.center_x >= self.end_of_map:

            # Advance to the next level
            self.level += 1

            # Make sure to keep the score from this level when setting up the next level
            self.reset_score = False

            # Load the next level
            self.setup()

        # Position the camera
        self.center_camera_to_player()


def main():
    """Main function"""
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()