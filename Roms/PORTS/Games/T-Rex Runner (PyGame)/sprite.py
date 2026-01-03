"""
This module provides the class Sprite.
"""

import pygame

class Sprite(object):
    """
    Shared sprite.
    """
    image = pygame.image.load("assets/100-offline-sprite.png").convert()
    image.set_colorkey((152, 152, 152))
