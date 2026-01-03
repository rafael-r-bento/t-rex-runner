"""
This module provides the class NightMode.
"""

import random
import pygame

from sprite import Sprite
from constants import SCREEN_WIDTH, SCREEN_HEIGHT

class NightMode(object):
    """
    Night mode shows a moon and stars on the horizon.
    """
    def __init__(self, screen, sprite_pos_moon, sprite_pos_star, container_width):
        """
        Initializes the night mode.
        """
        self.sprite_pos_moon = sprite_pos_moon
        self.sprite_pos_star = sprite_pos_star
        self.screen = screen
        self.x_pos = container_width - 50
        self.y_pos = (SCREEN_HEIGHT / 3) + 30
        self.current_phase = 0
        self.opacity = 0
        self.container_width = container_width
        self.draw_stars = False
        self.config = {
            "FADE_SPEED": 0.035,
            "HEIGHT": 40,
            "MOON_SPEED": 0.25,
            "NUM_STARS": 2,
            "STAR_SIZE": 9,
            "STAR_SPEED": 0.3,
            "STAR_MAX_Y": 70,
            "WIDTH": 20
        }
        self.stars = [None] * self.config["NUM_STARS"]
        self.phases = [140, 120, 100, 60, 40, 20, 0]
        self.image_sprite = Sprite.image
        self.place_stars()

    def update(self, delta_time, activated):
        """
        Update moving moon, changing phases.
        """
        if activated and self.opacity == 0:
            self.current_phase += 1
            if self.current_phase >= len(self.phases):
                self.current_phase = 0
        if (activated and (self.opacity < 1 or self.opacity == 0)):
            self.opacity += self.config["FADE_SPEED"]
        elif self.opacity > 0:
            self.opacity -= self.config["FADE_SPEED"]
        if self.opacity > 0:
            if delta_time:
                self.x_pos = self.update_x_pos(self.x_pos, self.config["MOON_SPEED"])
                if self.draw_stars:
                    for i in range(self.config["NUM_STARS"]):
                        self.stars[i]["x"] = self.update_x_pos(
                            self.stars[i]["x"],
                            self.config["STAR_SPEED"]
                        )
            self.draw()
        else:
            self.opacity = 0
            self.place_stars()
        self.draw_stars = True

    def update_x_pos(self, current_pos, speed):
        """
        Return updated x position of a moon or star.
        """
        if current_pos < -self.config["WIDTH"]:
            current_pos = self.container_width
        else:
            current_pos -= speed
        return current_pos

    def draw(self):
        """
        Draw the moon and stars on the screen.
        """
        moon_source_width = (self.config["WIDTH"] * 2 if self.current_phase == 3
                             else self.config["WIDTH"])
        moon_source_height = self.config["HEIGHT"]
        moon_source_x = self.sprite_pos_moon["x"] + self.phases[self.current_phase]
        moon_output_width = moon_source_width
        star_size = self.config["STAR_SIZE"]
        star_source_x = self.sprite_pos_star["x"]
        self.image_sprite.set_alpha(round(self.opacity * 255))
        if self.draw_stars:
            for i in range(self.config["NUM_STARS"]):
                sprite_position = pygame.Rect(
                    star_source_x,
                    self.stars[i]["source_y"],
                    star_size,
                    star_size
                )
                destination_rect = pygame.Rect(
                    round(self.stars[i]["x"]),
                    self.stars[i]["y"],
                    self.config["STAR_SIZE"],
                    self.config["STAR_SIZE"]
                )
                self.screen.blit(self.image_sprite, destination_rect, sprite_position)
        sprite_position = pygame.Rect(
            moon_source_x,
            self.sprite_pos_moon["y"],
            moon_source_width,
            moon_source_height
        )
        destination_rect = pygame.Rect(
            round(self.x_pos),
            self.y_pos,
            moon_output_width,
            self.config["HEIGHT"]
        )
        self.screen.blit(self.image_sprite, destination_rect, sprite_position)
        self.image_sprite.set_alpha(255)

    def place_stars(self):
        """
        Do star placement.
        """
        segment_size = round(self.container_width / self.config["NUM_STARS"])
        for i in range(self.config["NUM_STARS"]):
            self.stars[i] = {"x": None, "y": None, "source_y": None}
            self.stars[i]["x"] = random.randint(segment_size * i, segment_size * (i + 1))
            self.stars[i]["y"] = (SCREEN_HEIGHT / 3) + random.randint(0, self.config["STAR_MAX_Y"])
            self.stars[i]["source_y"] = self.sprite_pos_star["y"] + self.config["STAR_SIZE"] * i

    def reset(self):
        """
        Reset the night mode.
        """
        self.current_phase = 0
        self.opacity = 0
        self.update(0, False)
