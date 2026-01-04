"""
This module provides the class Game.
"""

import math
import sys
import pygame

from constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS

pygame.init()
INFO = pygame.display.Info()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

from collision_box import CollisionBox
from distance_meter import DistanceMeter
from game_over_panel import GameOverPanel
from horizon import Horizon
from t_rex import TRex

class Game(object):
    """
    T-Rex runner game.
    """
    def __init__(self):
        """
        Game initializer.
        """
        self.screen = screen
        pygame.display.set_caption("T-Rex Runner")
        self.clock = pygame.time.Clock()
        self.config = {
            "ACCELERATION": 0.001,
            "BG_CLOUD_SPEED": 0.2,
            "BOTTOM_PAD": 10,
            "CLEAR_TIME": 3000,
            "CLOUD_FREQUENCY": 0.5,
            "GAMEOVER_CLEAR_TIME": 750,
            "GAP_COEFFICIENT": 0.6,
            "GRAVITY": 0.6,
            "INITIAL_JUMP_VELOCITY": 12,
            "INVERT_FADE_DURATION": 12000,
            "INVERT_DISTANCE": 700,
            "MAX_BLINK_COUNT": 3,
            "MAX_CLOUDS": 6,
            "MAX_OBSTACLE_LENGTH": 3,
            "MAX_OBSTACLE_DUPLICATION": 2,
            "MAX_SPEED": 13,
            "MIN_JUMP_HEIGHT": 35,
            "SPEED": 6,
            "SPEED_DROP_COEFFICIENT": 3,
        }
        self.dimensions = {
            "WIDTH": SCREEN_WIDTH,
            "HEIGHT": SCREEN_HEIGHT
        }
        self.t_rex = None
        self.distance_meter = None
        self.distance_ran = 0
        self.highest_score = 0
        self.time = 0
        self.running_time = 0
        self.ms_per_frame = 1000 / FPS
        self.current_speed = self.config["SPEED"]
        self.obstacles = []
        self.playing = False
        self.crashed = False
        self.paused = False
        self.inverted = False
        self.invert_timer = 0
        self.play_count = 0
        pygame.mixer.pre_init(44100, -16, 2, 8192)
        pygame.mixer.init()
        self.button_press_sound = pygame.mixer.Sound("assets/button-press.ogg")
        self.hit_sound = pygame.mixer.Sound("assets/hit.ogg")
        self.score_reached_sound = pygame.mixer.Sound("assets/score-reached.ogg")
        self.sprite_def = {
            "CACTUS_LARGE": {'x': 332, 'y': 2},
            "CACTUS_SMALL": {'x': 228, 'y': 2},
            "CLOUD": {'x': 86, 'y': 2},
            "HORIZON": {'x': 2, 'y': 54},
            "MOON": {'x': 484, 'y': 2},
            "PTERODACTYL": {'x': 134, 'y': 2},
            "RESTART": {'x': 2, 'y': 2},
            "TEXT_SPRITE": {'x': 655, 'y': 2},
            "TREX": {'x': 848, 'y': 2},
            "STAR": {'x': 645, 'y': 2}
        }
        self.playing_intro = True
        self.game_over_panel = None
        self.horizon = Horizon(
            self.screen,
            self.sprite_def,
            self.dimensions,
            self.config["GAP_COEFFICIENT"]
        )
        self.distance_meter = DistanceMeter(
            self.screen,
            self.sprite_def["TEXT_SPRITE"],
            self.dimensions["WIDTH"]
        )
        self.t_rex = TRex(self.screen, self.sprite_def["TREX"])
        while True:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit(0)
                elif event.type == pygame.KEYDOWN:
                    self.on_key_down(event)
                elif event.type == pygame.KEYUP:
                    self.on_key_up(event)
            self.set_speed()
            if not self.inverted:
                self.screen.fill((247, 247, 247))
            else:
                self.screen.fill((0, 0, 0))
            self.update()
            pygame.display.flip()

    def set_speed(self, opt_speed=None):
        """
        Sets the game speed.
        """
        if opt_speed:
            self.current_speed = opt_speed

    def start_game(self):
        """
        Update the game status to started.
        """
        self.running_time = 0
        self.playing = True
        self.playing_intro = False
        self.play_count += 1

    def update(self):
        """
        Update the game frame.
        """
        self.update_pending = False
        now = pygame.time.get_ticks()
        delta_time = now - (self.time if self.time is not None else now)
        self.time = now
        if self.playing:
            if self.t_rex.jumping:
                self.t_rex.update_jump(delta_time)
            self.running_time += delta_time
            has_obstacles = self.running_time > self.config["CLEAR_TIME"]
            if self.t_rex.jump_count == 1 and self.playing_intro:
                self.start_game()
            if self.playing_intro:
                self.horizon.update(
                    0,
                    self.current_speed,
                    has_obstacles,
                    self.inverted
                )
            else:
                self.horizon.update(
                    delta_time,
                    self.current_speed,
                    has_obstacles,
                    self.inverted
                )
            collision = has_obstacles and self.check_for_collision(self.horizon.obstacles[0])
            if not collision:
                self.distance_ran += (self.current_speed * delta_time / self.ms_per_frame)
                if self.current_speed < self.config["MAX_SPEED"]:
                    self.current_speed += self.config["ACCELERATION"]
            else:
                self.game_over()
            play_achievement_sound = self.distance_meter.update(
                delta_time,
                math.ceil(self.distance_ran)
            )
            if play_achievement_sound:
                self.score_reached_sound.play()
            if self.invert_timer > self.config["INVERT_FADE_DURATION"]:
                self.invert_timer = 0
                self.invert_trigger = False
                self.invert()
            elif self.invert_timer:
                self.invert_timer += delta_time
            else:
                actual_distance = self.distance_meter.get_actual_distance(self.distance_ran)
                if actual_distance > 0:
                    self.invert_trigger = not actual_distance % self.config["INVERT_DISTANCE"]
                    if self.invert_trigger and self.invert_timer == 0:
                        self.invert_timer += delta_time
                        self.invert()
        if (self.playing or (self.t_rex.blink_count < self.config["MAX_BLINK_COUNT"])):
            self.t_rex.update(delta_time)
        if not self.playing:
            if (self.crashed and self.game_over_panel):
                self.game_over_panel.draw()
                self.horizon.update(
                    0,
                    self.current_speed,
                    True,
                    self.inverted
                )
                self.distance_meter.update(
                    delta_time,
                    math.ceil(self.distance_ran)
                )
            if not self.crashed:
                font = pygame.font.Font(None, 24)
                text_surface = font.render("Press START to begin", True, (0, 0, 0))
                self.screen.blit(text_surface, (5, 5))

    def on_key_down(self, event):
        """
        Process keydown.
        """
        if event.key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit()
        if self.playing_intro and event.key == pygame.K_RETURN:
            self.start_game()
            self.update()
            self.t_rex.start_jump(self.current_speed)
        if (
                not self.crashed and self.playing and
                (event.key == pygame.K_UP)
        ):
            if not self.t_rex.jumping and not self.t_rex.ducking:
                self.button_press_sound.play()
                self.t_rex.start_jump(self.current_speed)
        if self.crashed and event.key == pygame.K_RETURN:
            self.restart()
        if (
                self.playing and
                not self.crashed and
                (event.key == pygame.K_DOWN)
        ):
            if self.t_rex.jumping:
                self.t_rex.set_speed_drop()
            elif not self.t_rex.jumping and not self.t_rex.ducking:
                self.t_rex.set_duck(True)

    def on_key_up(self, event):
        """
        Process key up.
        """
        is_jump_key = (event.key == pygame.K_UP)
        if is_jump_key:
            self.t_rex.end_jump()
        elif event.key == pygame.K_DOWN:
            self.t_rex.speed_drop = False
            self.t_rex.set_duck(False)
        elif self.crashed:
            delta_time = pygame.time.get_ticks() - self.time
            if (
                    event.key == pygame.K_RETURN or
                    (delta_time >= self.config["GAMEOVER_CLEAR_TIME"] and
                     (event.key == pygame.K_UP))
            ):
                self.restart()
        elif self.paused and is_jump_key:
            self.t_rex.reset()
            self.play()

    def game_over(self):
        """
        Game over state.
        """
        self.hit_sound.play()
        self.stop()
        self.crashed = True
        self.distance_meter.achievement = False
        self.t_rex.update(100, self.t_rex.status["CRASHED"])
        if not self.game_over_panel:
            self.game_over_panel = GameOverPanel(
                self.screen,
                self.sprite_def["TEXT_SPRITE"],
                self.sprite_def["RESTART"],
                self.dimensions
            )
        else:
            self.game_over_panel.draw()
        if self.distance_ran > self.highest_score:
            self.highest_score = math.ceil(self.distance_ran)
            self.distance_meter.set_high_score(self.highest_score)
        self.time = pygame.time.get_ticks()

    def stop(self):
        """
        Stop game.
        """
        self.playing = False
        self.paused = True

    def play(self):
        """
        Play game.
        """
        if not self.crashed:
            self.playing = True
            self.paused = False
            self.t_rex.update(0, self.t_rex.status["RUNNING"])
            self.time = pygame.time.get_ticks()
            self.update()

    def restart(self):
        """
        Restart game.
        """
        self.play_count += 1
        self.running_time = 0
        self.playing = True
        self.crashed = False
        self.distance_ran = 0
        self.set_speed(self.config["SPEED"])
        self.time = pygame.time.get_ticks()
        self.distance_meter.reset()
        self.horizon.reset()
        self.t_rex.reset()
        self.button_press_sound.play()
        self.invert(True)
        self.update()

    def invert(self, reset=None):
        """
        Inverts the screen colors.
        """
        if reset:
            self.invert_timer = 0
            self.inverted = False
        else:
            self.inverted = self.invert_trigger

    def check_for_collision(self, obstacle):
        """
        Check for a collision.
        """
        obstacle_box = SCREEN_WIDTH + obstacle.x_pos
        t_rex_box = CollisionBox(
            self.t_rex.x_pos + 1,
            self.t_rex.y_pos + 1,
            self.t_rex.config["WIDTH"] - 2,
            self.t_rex.config["HEIGHT"] - 2
        )
        obstacle_box = CollisionBox(
            obstacle.x_pos + 1,
            obstacle.y_pos + 1,
            obstacle.type_config["width"] * obstacle.size - 2,
            obstacle.type_config["height"] - 2
        )
        if box_compare(t_rex_box, obstacle_box):
            collision_boxes = obstacle.collision_boxes
            t_rex_collision_boxes = (self.t_rex.collision_boxes["DUCKING"]
                                     if self.t_rex.ducking
                                     else self.t_rex.collision_boxes["RUNNING"])
            for _, t_rex_collision_box in enumerate(t_rex_collision_boxes):
                for _, collision_box in enumerate(collision_boxes):
                    adj_t_rex_box = create_adjusted_collision_box(
                        t_rex_collision_box,
                        t_rex_box
                    )
                    adj_obstacle_box = create_adjusted_collision_box(
                        collision_box,
                        obstacle_box
                    )
                    crashed = box_compare(adj_t_rex_box, adj_obstacle_box)
                    if crashed:
                        return [adj_t_rex_box, adj_obstacle_box]
        return False

def create_adjusted_collision_box(box, adjustment):
    """
    Adjust the collision box.
    """
    return CollisionBox(
        box.x + adjustment.x,
        box.y + adjustment.y,
        box.width,
        box.height
    )

def box_compare(t_rex_box, obstacle_box):
    """
    Compare two collision boxes for a collision.
    """
    crashed = False
    if (
            t_rex_box.x < obstacle_box.x + obstacle_box.width and
            t_rex_box.x + t_rex_box.width > obstacle_box.x and
            t_rex_box.y < obstacle_box.y + obstacle_box.height and
            t_rex_box.y + t_rex_box.height > obstacle_box.y
    ):
        crashed = True
    return crashed

Game()
