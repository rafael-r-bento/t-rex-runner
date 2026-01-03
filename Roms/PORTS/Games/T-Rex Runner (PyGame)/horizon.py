"""
This module provides the class Horizon.
"""

import random

from cloud import Cloud
from collision_box import CollisionBox
from horizon_line import HorizonLine
from night_mode import NightMode
from obstacle import Obstacle

from constants import SCREEN_WIDTH, SCREEN_HEIGHT, BOTTOM_PAD

MAX_OBSTACLE_DUPLICATION = 2

class Horizon(object):
    """
    Horizon background class.
    """
    def __init__(self, screen, sprite_pos, dimensions, gap_coefficient):
        """
        Initialise the horizon. Just add the line and a cloud. No obstacles.
        """
        self.screen = screen
        self.config = {
            "BG_CLOUD_SPEED": 0.2,
            "CLOUD_FREQUENCY": 0.5,
            "HORIZON_HEIGHT": 16,
            "MAX_CLOUDS": 6
        }
        self.dimensions = dimensions
        self.gap_coefficient = gap_coefficient
        self.obstacles = []
        self.obstacle_history = []
        self.horizon_offsets = [0, 0]
        self.cloud_frequency = self.config["CLOUD_FREQUENCY"]
        self.sprite_pos = sprite_pos
        self.night_mode = None
        self.clouds = []
        self.cloud_speed = self.config["BG_CLOUD_SPEED"]
        self.horizon_line = None
        self.running_time = 0
        self.types = [
            {
                "type": "CACTUS_SMALL",
                "width": 17,
                "height": 35,
                "y_pos": SCREEN_HEIGHT - 35 - BOTTOM_PAD,
                "multiple_speed": 4,
                "min_gap": 120,
                "min_speed": 0,
                "collision_boxes": [
                    CollisionBox(0, 7, 5, 27),
                    CollisionBox(4, 0, 6, 34),
                    CollisionBox(10, 4, 7, 14)
                ],
                "num_frames": None,
                "speed_offset": None
            },
            {
                "type": "CACTUS_LARGE",
                "width": 25,
                "height": 50,
                "y_pos": SCREEN_HEIGHT - 50 - BOTTOM_PAD,
                "multiple_speed": 7,
                "min_gap": 120,
                "min_speed": 0,
                "collision_boxes": [
                    CollisionBox(0, 12, 7, 38),
                    CollisionBox(8, 0, 7, 49),
                    CollisionBox(13, 10, 10, 38)
                ],
                "num_frames": None,
                "speed_offset": None
            },
            {
                "type": "PTERODACTYL",
                "width": 46,
                "height": 40,
                "y_pos": [SCREEN_HEIGHT - 50, SCREEN_HEIGHT - 75, SCREEN_HEIGHT - 100],
                "multiple_speed": 999,
                "min_gap": 150,
                "min_speed": 8.5,
                "collision_boxes": [
                    CollisionBox(15, 15, 16, 5),
                    CollisionBox(18, 21, 24, 6),
                    CollisionBox(2, 14, 4, 3),
                    CollisionBox(6, 10, 4, 7),
                    CollisionBox(10, 8, 6, 9)
                ],
                "num_frames": 2,
                "frame_rate": 1000 / 6,
                "speed_offset": 0.8
            }
        ]
        self.add_cloud()
        self.horizon_line = HorizonLine(self.screen, self.sprite_pos["HORIZON"])
        self.night_mode = NightMode(
            self.screen,
            self.sprite_pos["MOON"],
            self.sprite_pos["STAR"],
            self.dimensions["WIDTH"]
        )

    def update(self, delta_time, current_speed, update_obstacles, show_night_mode):
        """
        Update horizon line, night mode (if activated) and the clouds.
        """
        self.running_time += delta_time
        self.horizon_line.update(delta_time, current_speed)
        self.night_mode.update(delta_time, show_night_mode)
        self.update_clouds(delta_time, current_speed)
        if update_obstacles:
            self.update_obstacles(delta_time, current_speed)

    def update_clouds(self, delta_time, speed):
        """
        Update the cloud positions.
        """
        cloud_speed = self.cloud_speed / 1000 * delta_time * speed
        num_clouds = len(self.clouds)

        if num_clouds:
            for cloud in self.clouds:
                cloud.update(cloud_speed)
            last_cloud = self.clouds[num_clouds - 1]
            if (
                    num_clouds < self.config["MAX_CLOUDS"] and
                    (self.dimensions["WIDTH"] - last_cloud.x_pos) > last_cloud.cloud_gap and
                    self.cloud_frequency > random.random()
            ):
                self.add_cloud()
            self.clouds = [obj for obj in self.clouds if not obj.remove]
        else:
            self.add_cloud()

    def update_obstacles(self, delta_time, current_speed):
        """
        Update the obstacle positions.
        """
        updated_obstacles = self.obstacles[:]
        for obstacle in self.obstacles:
            obstacle.update(delta_time, current_speed)
            if obstacle.remove:
                updated_obstacles.pop(0)
        self.obstacles = updated_obstacles
        if self.obstacles:
            last_obstacle = self.obstacles[-1]
            if (
                    last_obstacle
                    and not last_obstacle.following_obstacle_created
                    and last_obstacle.is_visible()
                    and (last_obstacle.x_pos + last_obstacle.width + last_obstacle.gap)
                    < self.dimensions["WIDTH"]
            ):
                self.add_new_obstacle(current_speed)
                last_obstacle.following_obstacle_created = True
        else:
            self.add_new_obstacle(current_speed)

    def remove_first_obstacle(self):
        """
        Remove first obstacle from obstacles.
        """
        self.obstacles.pop(0)

    def add_new_obstacle(self, current_speed):
        """
        Add a new obstacle.
        """
        obstacle_type_index = random.randint(0, len(self.types) - 1)
        obstacle_type = self.types[obstacle_type_index]
        if (
                self.duplicate_obstacle_check(obstacle_type["type"]) or
                current_speed < obstacle_type["min_speed"]
        ):
            self.add_new_obstacle(current_speed)
        else:
            obstacle_sprite_pos = self.sprite_pos[obstacle_type["type"]]
            self.obstacles.append(
                Obstacle(
                    self.screen,
                    obstacle_type,
                    obstacle_sprite_pos,
                    self.dimensions,
                    self.gap_coefficient,
                    current_speed,
                    obstacle_type["width"]
                )
            )
            self.obstacle_history.insert(0, obstacle_type["type"])
            if len(self.obstacle_history) > 1:
                del self.obstacle_history[MAX_OBSTACLE_DUPLICATION:]

    def duplicate_obstacle_check(self, next_obstacle_type):
        """
        Returns whether the previous two obstacles are the same as the next one.
        """
        duplicate_count = 0
        for obstacle_type in self.obstacle_history:
            duplicate_count = duplicate_count + 1 if obstacle_type == next_obstacle_type else 0
        return duplicate_count >= MAX_OBSTACLE_DUPLICATION

    def reset(self):
        """
        Reset the horizon layer.
        """
        self.obstacles = []
        self.horizon_line.reset()
        self.night_mode.reset()

    def add_cloud(self):
        """
        Add a new cloud to the horizon.
        """
        self.clouds.append(Cloud(self.screen, self.sprite_pos["CLOUD"], self.dimensions["WIDTH"]))
