"""
This module provides the class TRex.
"""

import math
import random
import pygame

from collision_box import CollisionBox

from sprite import Sprite
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BOTTOM_PAD

BLINK_TIMING = 7000

class TRex(object):
    """
    T-rex game character.
    """
    def __init__(self, screen, sprite_pos):
        """
        T-rex player initaliser.
        """
        self.screen = screen
        self.sprite_pos = sprite_pos
        self.x_pos = 0
        self.y_pos = 0
        self.ground_y_pos = 0
        self.current_frame = 0
        self.current_anim_frames = []
        self.blink_delay = 0
        self.blink_count = 0
        self.anim_start_time = 0
        self.timer = 0
        self.ms_per_frame = 1000 // FPS
        self.config = {
            "DROP_VELOCITY": -5,
            "GRAVITY": 0.6,
            "HEIGHT": 47,
            "HEIGHT_DUCK": 25,
            "INITIAL_JUMP_VELOCITY": -10,
            "INTRO_DURATION": 1500,
            "MAX_JUMP_HEIGHT": 30,
            "MIN_JUMP_HEIGHT": 30,
            "SPEED_DROP_COEFFICIENT": 3,
            "SPRITE_WIDTH": 262,
            "START_X_POS": 50,
            "WIDTH": 44,
            "WIDTH_DUCK": 59
        }
        self.status = {
            "CRASHED": "CRASHED",
            "DUCKING": "DUCKING",
            "JUMPING": "JUMPING",
            "RUNNING": "RUNNING",
            "WAITING": "WAITING"
        }
        self.current_status = self.status["WAITING"]
        self.jumping = False
        self.ducking = False
        self.jump_velocity = 0
        self.reached_min_height = False
        self.speed_drop = False
        self.jump_count = 0
        self.jumpspot_x = 0
        self.collision_boxes = {
            "DUCKING": [
                CollisionBox(1, 18, 55, 25)
            ],
            "RUNNING": [
                CollisionBox(22, 0, 17, 16),
                CollisionBox(1, 18, 30, 9),
                CollisionBox(10, 35, 14, 8),
                CollisionBox(1, 24, 29, 5),
                CollisionBox(5, 30, 21, 4),
                CollisionBox(9, 34, 15, 4)
            ]
        }
        self.anim_frames = {
            "WAITING": {
                "frames": [44, 0],
                "ms_per_frame": 1000/3
            },
            "RUNNING": {
                "frames": [88, 132],
                "ms_per_frame": 1000/12
            },
            "CRASHED": {
                "frames": [220],
                "ms_per_frame": 1000/60
            },
            "JUMPING": {
                "frames": [0],
                "ms_per_frame": 1000/60
            },
            "DUCKING": {
                "frames": [264, 323],
                "ms_per_frame": 1000/8
            },
        }
        self.image_sprite = Sprite.image
        self.ground_y_pos = SCREEN_HEIGHT - self.config["HEIGHT"] - BOTTOM_PAD
        self.y_pos = self.ground_y_pos
        self.min_jump_height = self.ground_y_pos - self.config["MIN_JUMP_HEIGHT"]
        self.draw(0, 0)
        self.update(0, self.status["JUMPING"])

    def update(self, delta_time, opt_status=None):
        """
        Set the animation status.
        """
        self.timer += delta_time
        if opt_status:
            self.current_status = opt_status
            self.current_frame = 0
            self.ms_per_frame = self.anim_frames[opt_status]["ms_per_frame"]
            self.current_anim_frames = self.anim_frames[opt_status]["frames"]
            if opt_status == self.status["WAITING"]:
                self.anim_start_time = pygame.time.get_ticks()
                self.draw(self.current_anim_frames[self.current_frame], 0)
        if self.current_status == self.status["WAITING"]:
            self.blink(pygame.time.get_ticks())
        else:
            self.draw(self.current_anim_frames[self.current_frame], 0)
        if self.timer >= self.ms_per_frame:
            self.current_frame = (
                0 if self.current_frame == len(self.current_anim_frames) - 1
                else self.current_frame + 1
            )
            self.timer = 0
        if self.speed_drop and self.y_pos == self.ground_y_pos:
            self.speed_drop = False
            self.set_duck(True)

    def draw(self, x, y):
        """
        Draw the t-rex to a particular position.
        """
        source_x = x
        source_y = y
        source_width = (
            self.config["WIDTH_DUCK"]
            if self.ducking and self.current_status != self.status["CRASHED"]
            else self.config["WIDTH"]
        )
        source_height = self.config["HEIGHT"]

        source_x += self.sprite_pos["x"]
        source_y += self.sprite_pos["y"]
        if self.ducking and self.current_status != self.status["CRASHED"]:
            sprite_position = pygame.Rect(source_x, source_y, source_width, source_height)
            destination_rect = pygame.Rect(
                self.x_pos,
                self.y_pos,
                self.config["WIDTH_DUCK"],
                self.config["HEIGHT"]
            )
            self.screen.blit(self.image_sprite, destination_rect, sprite_position)
        else:
            sprite_position = pygame.Rect(source_x, source_y, source_width, source_height)
            destination_rect = pygame.Rect(
                self.x_pos,
                self.y_pos,
                self.config["WIDTH"],
                self.config["HEIGHT"]
            )
            self.screen.blit(self.image_sprite, destination_rect, sprite_position)

    def set_blink_delay(self):
        """
        Sets a random time for the blink to happen.
        """
        self.blink_delay = math.ceil(random.random() * BLINK_TIMING)

    def blink(self, time):
        """
        Make t-rex blink at random intervals.
        """
        delta_time = time - self.anim_start_time
        if delta_time >= self.blink_delay:
            self.draw(self.current_anim_frames[self.current_frame], 0)
            if self.current_frame == 1:
                self.set_blink_delay()
                self.anim_start_time = time
                self.blink_count += 1

    def start_jump(self, speed):
        """
        Initialise a jump.
        """
        if not self.jumping:
            self.update(0, self.status["JUMPING"])
            self.jump_velocity = self.config["INITIAL_JUMP_VELOCITY"] - (float(speed) / 10)
            self.jumping = True
            self.reached_min_height = False
            self.speed_drop = False

    def end_jump(self):
        """
        Jump is complete, falling down.
        """
        if self.reached_min_height and self.jump_velocity < self.config["DROP_VELOCITY"]:
            self.jump_velocity = self.config["DROP_VELOCITY"]

    def update_jump(self, delta_time):
        """
        Update frame for a jump.
        """
        ms_per_frame = self.anim_frames[self.current_status]["ms_per_frame"]
        frames_elapsed = float(delta_time) / ms_per_frame
        if self.speed_drop:
            self.y_pos += math.floor(
                self.jump_velocity * self.config["SPEED_DROP_COEFFICIENT"] * frames_elapsed + 0.5
            )
        else:
            self.y_pos += math.floor(self.jump_velocity * frames_elapsed + 0.5)
        self.jump_velocity += (self.config["GRAVITY"] * frames_elapsed)
        if self.y_pos < self.min_jump_height or self.speed_drop:
            self.reached_min_height = True
        if self.y_pos < self.config["MAX_JUMP_HEIGHT"] or self.speed_drop:
            self.end_jump()
        if self.y_pos > self.ground_y_pos:
            self.reset()
            self.jump_count += 1
        self.update(delta_time)

    def set_speed_drop(self):
        """
        Set the speed drop. Immediately cancels the current jump.
        """
        self.speed_drop = True
        self.jump_velocity = 1

    def set_duck(self, is_ducking):
        """
        Set whether the t-rex is ducking.
        """
        if is_ducking and self.current_status != self.status["DUCKING"]:
            self.update(0, self.status["DUCKING"])
            self.ducking = True
        elif self.current_status == self.status["DUCKING"]:
            self.update(0, self.status["RUNNING"])
            self.ducking = False

    def reset(self):
        """
        Reset the t-rex to running at start of game.
        """
        self.y_pos = self.ground_y_pos
        self.jump_velocity = 0
        self.jumping = False
        self.ducking = False
        self.update(0, self.status["RUNNING"])
        self.speed_drop = False
        self.jump_count = 0
