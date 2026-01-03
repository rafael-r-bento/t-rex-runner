"""
This module provides the class DistanceMeter.
"""

import math
import pygame

from sprite import Sprite

class DistanceMeter(object):
    """
    Handles displaying the distance meter.
    """
    def __init__(self, screen, sprite_pos, screen_width):
        """
        Initialize the distance meter to '00000'.
        """
        self.screen = screen
        self.sprite_pos = sprite_pos
        self.x = 0
        self.y = 5
        self.current_distance = 0
        self.max_score = 0
        self.high_score = []
        self.container = None
        self.digits = []
        self.achievement = False
        self.default_string = ''
        self.flash_timer = 0
        self.flash_iterations = 0
        self.invert_trigger = False
        self.config = {
            "MAX_DISTANCE_UNITS": 5,
            "ACHIEVEMENT_DISTANCE": 100,
            "COEFFICIENT": 0.025,
            "FLASH_DURATION": 250,
            "FLASH_ITERATIONS": 3
        }
        self.max_score_units = self.config["MAX_DISTANCE_UNITS"]
        self.dimensions = {
            "WIDTH": 10,
            "HEIGHT": 13,
            "DEST_WIDTH": 11
        }
        self.y_pos = [0, 13, 27, 40, 53, 67, 80, 93, 107, 120]
        self.image_sprite = Sprite.image
        self.alpha = 255
        max_distance_str = ''
        self.calc_x_pos(screen_width)
        self.max_score = self.max_score_units
        for i in range(self.max_score_units):
            self.draw(i, 0)
            self.default_string += '0'
            max_distance_str += '9'
        self.max_score = int(max_distance_str)

    def calc_x_pos(self, screen_width):
        """
        Calculate the x position in the screen.
        """
        self.x = screen_width - (self.dimensions["DEST_WIDTH"] * (self.max_score_units + 1))

    def draw(self, digit_pos, value, opt_high_score=None):
        """
        Draw a digit to screen.
        """
        source_width = self.dimensions["WIDTH"]
        source_height = self.dimensions["HEIGHT"]
        source_x = self.dimensions["WIDTH"] * value
        source_y = 0
        target_x = digit_pos * self.dimensions["DEST_WIDTH"]
        target_y = self.y
        target_width = self.dimensions["WIDTH"]
        target_height = self.dimensions["HEIGHT"]
        source_x += self.sprite_pos["x"]
        source_y += self.sprite_pos["y"]
        offset_x = None
        offset_y = None
        if opt_high_score:
            high_score_x = self.x - (self.max_score_units * 2) * self.dimensions["WIDTH"]
            offset_x = high_score_x
            offset_y = self.y
        else:
            offset_x = self.x
            offset_y = self.y
        self.image_sprite.set_alpha(self.alpha)
        sprite_position = pygame.Rect(source_x, source_y, source_width, source_height)
        destination_rect = pygame.Rect(
            target_x + offset_x,
            target_y + offset_y,
            target_width,
            target_height
        )
        self.screen.blit(self.image_sprite, destination_rect, sprite_position)
        self.image_sprite.set_alpha(255)

    def get_actual_distance(self, distance):
        """
        Convert pixel distance to a 'real' distance.
        """
        return int(math.floor(distance * self.config['COEFFICIENT'] + 0.5)) if distance else 0

    def update(self, delta_time, distance):
        """
        Update the distance meter.
        """
        paint = True
        play_sound = False
        if not self.achievement:
            distance = self.get_actual_distance(distance)
            if (
                    distance > self.max_score and
                    self.max_score_units == self.config["MAX_DISTANCE_UNITS"]
            ):
                self.max_score_units += 1
                self.max_score = int(str(self.max_score) + '9')
            if distance > 0:
                if distance % self.config["ACHIEVEMENT_DISTANCE"] == 0:
                    self.achievement = True
                    self.flash_timer = 0
                    play_sound = True
                distance_str = (self.default_string + str(distance))[-self.max_score_units:]
                self.digits = list(distance_str)
            else:
                self.digits = list(self.default_string)
        else:
            if self.flash_iterations <= self.config["FLASH_ITERATIONS"]:
                self.flash_timer += delta_time
                if self.flash_timer < self.config["FLASH_DURATION"]:
                    paint = False
                elif self.flash_timer > self.config["FLASH_DURATION"] * 2:
                    self.flash_timer = 0
                    self.flash_iterations += 1
            else:
                self.achievement = False
                self.flash_iterations = 0
                self.flash_timer = 0
        if paint:
            for i in range(len(self.digits) - 1, -1, -1):
                self.draw(i, int(self.digits[i]))
        self.draw_high_score()
        return play_sound

    def draw_high_score(self):
        """
        Draw the high score.
        """
        previous_alpha = self.alpha if hasattr(self, 'alpha') else 255
        self.alpha = int(0.8 * 255)
        for i in range(len(self.high_score) - 1, -1, -1):
            self.draw(i, int(self.high_score[i]), True)
        self.alpha = previous_alpha

    def set_high_score(self, distance):
        """
        Set the high score as an array string.
        """
        distance = self.get_actual_distance(distance)
        high_score_str = (self.default_string + str(distance))[-self.max_score_units:]
        self.high_score = ['10', '11', '12'] + list(high_score_str)

    def reset(self):
        """
        Reset the distance meter back to '00000'.
        """
        self.update(0, 0)
        self.achievement = False
