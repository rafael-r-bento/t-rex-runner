"""
This module provides the class Obstacle.
"""

import math
import random
import pygame

from sprite import Sprite

from collision_box import CollisionBox

from constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS

MAX_GAP_COEFFICIENT = 1.5
MAX_OBSTACLE_LENGTH = 3

class Obstacle(object):
    """
    Obstacle class.
    """
    def __init__(
            self,
            screen,
            type_selected,
            sprite_img_pos,
            dimensions,
            gap_coefficient,
            speed,
            opt_x_offset
    ):
        """
        Initialise the obstacle.
        """
        self.screen = screen
        self.sprite_pos = sprite_img_pos
        self.type_config = type_selected
        self.gap_coefficient = gap_coefficient
        self.size = random.randint(1, MAX_OBSTACLE_LENGTH)
        self.dimensions = dimensions
        self.remove = False
        self.x_pos = dimensions["WIDTH"] + (opt_x_offset or 0)
        self.y_pos = 0
        self.width = 0
        self.collision_boxes = []
        self.gap = 0
        self.speed_offset = 0
        self.current_frame = 0
        self.timer = 0
        self.following_obstacle_created = None
        self.image_sprite = Sprite.image
        self.clone_collision_boxes()
        if self.size > 1 and self.type_config["multiple_speed"] > speed:
            self.size = 1
        self.width = self.type_config["width"] * self.size
        if isinstance(self.type_config["y_pos"], list):
            y_pos_config = self.type_config["y_pos"]
            self.y_pos = y_pos_config[random.randint(0, len(y_pos_config) - 1)]
        else:
            self.y_pos = self.type_config["y_pos"]
        self.draw()
        if self.size > 1:
            self.collision_boxes[1].width = (
                self.width -
                self.collision_boxes[0].width -
                self.collision_boxes[2].width
            )
            self.collision_boxes[2].x = self.width - self.collision_boxes[2].width
        if self.type_config["speed_offset"]:
            self.speed_offset = (
                self.type_config["speed_offset"]
                if random.random() > 0.5
                else -self.type_config["speed_offset"]
            )
        self.gap = self.get_gap(self.gap_coefficient, speed)

    def draw(self):
        """
        Draw and crop based on size.
        """
        source_width = self.type_config["width"]
        source_height = self.type_config["height"]
        source_x = (source_width * self.size) * (0.5 * (self.size - 1)) + self.sprite_pos["x"]
        if self.current_frame > 0:
            source_x += (source_width * self.current_frame)
        sprite_position = pygame.Rect(
            source_x,
            self.sprite_pos["y"],
            source_width * self.size,
            source_height
        )
        destination_rect = pygame.Rect(
            self.x_pos,
            self.y_pos,
            self.type_config["width"] * self.size,
            self.type_config["height"]
        )
        self.screen.blit(self.image_sprite, destination_rect, sprite_position)

    def update(self, delta_time, speed):
        """
        Obstacle frame update.
        """
        if not self.remove:
            if self.type_config["speed_offset"]:
                speed += self.speed_offset
            self.x_pos -= math.floor((speed * float(FPS) / 1000) * delta_time + 0.5)
            if self.type_config["num_frames"]:
                self.timer += delta_time
                if self.timer >= self.type_config["frame_rate"]:
                    self.current_frame = (
                        0
                        if self.current_frame == self.type_config["num_frames"] - 1
                        else self.current_frame + 1
                    )
                    self.timer = 0
            self.draw()
            if not self.is_visible():
                self.remove = True

    def get_gap(self, gap_coefficient, speed):
        """
        Calculate a random gap size. Minimum gap gets wider as speed increses.
        """
        min_gap = math.floor(
            self.width * speed + self.type_config["min_gap"] * gap_coefficient + 0.5
        )
        max_gap = math.floor(min_gap * MAX_GAP_COEFFICIENT + 0.5)
        return random.randint(min_gap, max_gap)

    def is_visible(self):
        """
        Check if obstacle is visible.
        """
        return self.x_pos + self.width > 0

    def clone_collision_boxes(self):
        """
        Make a copy of the collision boxes, since these will change based on obstacle type and size.
        """
        collision_boxes = self.type_config["collision_boxes"]
        for i in range(len(collision_boxes) - 1, -1, -1):
            box = collision_boxes[i]
            self.collision_boxes.insert(i, CollisionBox(box.x, box.y, box.width, box.height))
