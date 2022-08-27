import asyncio
import logging
import random
from asyncio.queues import Queue
from collections import Counter
from copy import deepcopy

from common import Coordinates, Dimensions, Map, MapException
from shape import SHAPES

logger = logging.getLogger("Game")
logger.setLevel(logging.DEBUG)

GAME_SPEED = 10
SPEED_STEP = 10  # points


class Game:
    def __init__(self, x=6, y=6) -> None:
        logger.info("Game")
        self.dimensions = Dimensions(x, y)
        self.current_piece = None

        self.grid = Map("02 ooooBoooooBoAAooBooooooooooooooooooo 14")
        self.game_speed = GAME_SPEED
        self._running = True
        self.cursor = Dimensions(x / 3, y / 3)

        self._step = 0
        self._timeout = 1000

        self._selected = None

        self._lastkeypress = "-"

    @property
    def running(self):
        """Status on game."""
        return self._running

    @property
    def score(self):
        return self._timeout - self._step + self.grid.movements

    def stop(self):
        """Stop the game."""
        if self._step:
            logger.info("GAME OVER at %s", self._step)
        self._running = False

    def info(self):
        return {
            "dimensions": (self.dimensions.x, self.dimensions.y),
            "grid": str(self.grid),
            "score": self.score,
            "game_speed": self.game_speed,
            "cursor": (self.cursor.x, self.cursor.y),
            "selected": self._selected if self._selected else "",
        }

    def keypress(self, key):
        """Update locally last key pressed."""
        self._lastkeypress = key

    async def loop(self):
        logger.info("Loop %s - score: %s", self._step, self.score)

        await asyncio.sleep(1.0 / GAME_SPEED)

        self._step += 1
        if self._step >= self._timeout:
            self.stop()

        if self._lastkeypress == " ":  # Toggle
            if self._selected is None:
                logger.debug("Select %s", self.grid.get(self.cursor))
                self._selected = self.grid.get(self.cursor)
            else:
                logger.debug("UnSelect")
                self._selected = None

        elif self._lastkeypress in "wasd":
            if self._selected:
                logger.debug("move piece")
                try:
                    if self._lastkeypress == "w" and self.cursor.y > 0:
                        self.grid.move(self._selected, Coordinates(0, -1))
                        self.cursor.y -= 1
                    elif self._lastkeypress == "a" and self.cursor.x > 0:
                        self.grid.move(self._selected, Coordinates(-1, 0))
                        self.cursor.x -= 1
                    elif (
                        self._lastkeypress == "s"
                        and self.cursor.y + 1 < self.dimensions.y
                    ):
                        self.grid.move(self._selected, Coordinates(0, 1))
                        self.cursor.y += 1
                    elif (
                        self._lastkeypress == "d"
                        and self.cursor.x + 1 < self.dimensions.x
                    ):
                        self.grid.move(self._selected, Coordinates(1, 0))
                        self.cursor.x += 1
                        # Test victory:
                        if self._selected == "A" and self.grid.test_win():
                            logger.info("You win!")
                            self.stop()
                except MapException as exc:
                    logger.error("Can't move %s: %s", self._selected, exc)
            else:
                logger.debug("move cursor")
                if self._lastkeypress == "w" and self.cursor.y > 0:
                    self.cursor.y -= 1
                elif self._lastkeypress == "a" and self.cursor.x > 0:
                    self.cursor.x -= 1
                elif (
                    self._lastkeypress == "s" and self.cursor.y + 1 < self.dimensions.y
                ):
                    self.cursor.y += 1
                elif (
                    self._lastkeypress == "d" and self.cursor.x + 1 < self.dimensions.x
                ):
                    self.cursor.x += 1

        self._lastkeypress = "-"

        return self.info()
