"""
This module provides the class GameOverPanel.
"""

import pygame

from sprite import Sprite
from constants import SCREEN_WIDTH, SCREEN_HEIGHT

class GameOverPanel(object):
    """
    Game over panel.
    """
    def __init__(self, screen, text_img_pos, restart_img_pos, screen_dimensions):
        """
        Initialize the game over panel.
        """
        self.screen = screen
        self.screen_dimensions = screen_dimensions
        self.text_img_pos = text_img_pos
        self.restart_img_pos = restart_img_pos
        self.dimensions = {
            "TEXT_X": 0,
            "TEXT_Y": 13,
            "TEXT_WIDTH": 191,
            "TEXT_HEIGHT": 11,
            "RESTART_WIDTH": 36,
            "RESTART_HEIGHT": 32
        }
        self.image_sprite = Sprite.image
        self.image_sprite.set_colorkey((152, 152, 152))
        self.draw()

    def update_dimensions(self, width, opt_height):
        """
        Update the panel dimensions.
        """
        self.screen_dimensions["WIDTH"] = width
        if opt_height:
            self.screen_dimensions["HEIGHT"] = opt_height

    def draw(self):
        """
        Draw the panel.
        """
        center_x = self.screen_dimensions["WIDTH"] / 2
        text_source_x = self.dimensions["TEXT_X"]
        text_source_y = self.dimensions["TEXT_Y"]
        text_source_width = self.dimensions["TEXT_WIDTH"]
        text_source_height = self.dimensions["TEXT_HEIGHT"]
        text_target_x = round(center_x - (self.dimensions["TEXT_WIDTH"] / 2))
        text_target_y = round((self.screen_dimensions["HEIGHT"] - 25) / 3)
        text_target_width = self.dimensions["TEXT_WIDTH"]
        text_target_height = self.dimensions["TEXT_HEIGHT"]
        text_source_x += self.text_img_pos["x"]
        text_source_y += self.text_img_pos["y"]
        sprite_position = pygame.Rect(
            text_source_x,
            text_source_y,
            text_source_width,
            text_source_height
        )
        destination_rect = pygame.Rect(
            text_target_x,
            text_target_y,
            text_target_width,
            text_target_height
        )
        self.screen.blit(self.image_sprite, destination_rect, sprite_position)
        font = pygame.font.Font(None, 24)
        text_surface = font.render("Press START to play again", True, (0, 0, 0))
        self.screen.blit(text_surface, (5, 5))
