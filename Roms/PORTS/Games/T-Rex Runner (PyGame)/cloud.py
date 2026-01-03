"""
This module provides the class Cloud.
"""

import math
import random
import pygame

from sprite import Sprite
from constants import SCREEN_WIDTH, SCREEN_HEIGHT

class Cloud(object):
    """
    Cloud background item.
    """
    def __init__(self, screen, sprite_pos, container_width):
        """
        Initializes the cloud. Sets the cloud height.
        """
        self.screen = screen
        self.sprite_pos = sprite_pos
        self.container_width = container_width
        self.x_pos = container_width
        self.y_pos = 0
        self.remove = False
        self.config = {
            "HEIGHT": 14,
            "MAX_CLOUD_GAP": 400,
            "MAX_SKY_LEVEL": (SCREEN_HEIGHT / 3) + 30,
            "MIN_CLOUD_GAP": 100,
            "MIN_SKY_LEVEL": (SCREEN_HEIGHT / 3) + 71,
            "WIDTH": 46
        }
        self.cloud_gap = random.randint(self.config["MIN_CLOUD_GAP"], self.config["MAX_CLOUD_GAP"])
        self.image_sprite = Sprite.image
        self.y_pos = random.randint(self.config["MAX_SKY_LEVEL"], self.config["MIN_SKY_LEVEL"])
        self.draw()

    def draw(self):
        """
        Draw the cloud.
        """
        source_width = self.config["WIDTH"]
        source_height = self.config["HEIGHT"]
        sprite_position = pygame.Rect(
            self.sprite_pos["x"],
            self.sprite_pos["y"],
            source_width,
            source_height
        )
        destination_rect = pygame.Rect(self.x_pos, self.y_pos, source_width, source_height)
        self.screen.blit(self.image_sprite, destination_rect, sprite_position)

    def update(self, speed):
        """
        Update the cloud position.
        """
        if not self.remove:
            self.x_pos -= math.ceil(speed)
            self.draw()
            if not self.is_visible():
                self.remove = True

    def is_visible(self):
        """
        Check if the cloud is visible on the stage.
        """
        return self.x_pos + self.config["WIDTH"] > 0
