"""
This module provides the class HorizonLine.
"""

import math
import random
import pygame

from sprite import Sprite
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BOTTOM_PAD

class HorizonLine(object):
    """
    Consists of two connecting lines. Randomly assigns a flat/bumpy horizon.
    """
    def __init__(self, screen, sprite_pos):
        """
        Initialize the horizon line.
        """
        self.screen = screen
        self.sprite_pos = sprite_pos
        self.source_dimensions = {}
        self.dimensions = {
            "WIDTH": 600,
            "HEIGHT": 12,
            "YPOS": SCREEN_HEIGHT - BOTTOM_PAD - 12
        }
        self.source_x_pos = [self.sprite_pos["x"], self.sprite_pos["x"] + self.dimensions["WIDTH"]]
        self.x_pos = []
        self.y_pos = 0
        self.bump_threshold = 0.5
        self.image_sprite = Sprite.image
        self.set_source_dimensions()
        self.draw()

    def set_source_dimensions(self):
        """
        Set the source dimensions of the horizon line.
        """
        for dimension in self.dimensions:
            self.source_dimensions[dimension] = self.dimensions[dimension]
        self.x_pos = [0, self.dimensions["WIDTH"]]
        self.y_pos = self.dimensions["YPOS"]

    def get_random_type(self):
        """
        Return the crop x position of a type.
        """
        return self.dimensions["WIDTH"] if random.random() > self.bump_threshold else 0

    def draw(self):
        """
        Draw the horizon line.
        """
        sprite_position = pygame.Rect(
            self.source_x_pos[0],
            self.sprite_pos["y"],
            self.source_dimensions["WIDTH"],
            self.source_dimensions["HEIGHT"]
        )
        destination_rect = pygame.Rect(
            self.x_pos[0],
            self.y_pos,
            self.dimensions["WIDTH"],
            self.dimensions["HEIGHT"]
        )
        self.screen.blit(self.image_sprite, destination_rect, sprite_position)
        sprite_position = pygame.Rect(
            self.source_x_pos[1],
            self.sprite_pos["y"],
            self.source_dimensions["WIDTH"],
            self.source_dimensions["HEIGHT"]
        )
        destination_rect = pygame.Rect(
            self.x_pos[1],
            self.y_pos,
            self.dimensions["WIDTH"],
            self.dimensions["HEIGHT"]
        )
        self.screen.blit(self.image_sprite, destination_rect, sprite_position)

    def update_x_pos(self, pos, increment):
        """
        Update the x position of an individual piece of the line.
        """
        line1 = pos
        line2 = 1 if pos == 0 else 0

        self.x_pos[line1] -= increment
        self.x_pos[line2] = self.x_pos[line1] + self.dimensions["WIDTH"]

        if self.x_pos[line1] <= -self.dimensions["WIDTH"]:
            self.x_pos[line1] += self.dimensions["WIDTH"] * 2
            self.x_pos[line2] = self.x_pos[line1] - self.dimensions["WIDTH"]
            self.source_x_pos[line1] = self.get_random_type() + self.sprite_pos["x"]

    def update(self, delta_time, speed):
        """
        Update the horizon line.
        """
        increment = math.floor(speed * (float(FPS) / 1000) * delta_time + 0.5)
        if self.x_pos[0] <= 0:
            self.update_x_pos(0, increment)
        else:
            self.update_x_pos(1, increment)
        self.draw()

    def reset(self):
        """
        Reset horizon to the starting position.
        """
        self.x_pos[0] = 0
        self.x_pos[1] = self.dimensions["WIDTH"]
