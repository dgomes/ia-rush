"""Viewer application."""
import argparse
import asyncio
import json
import logging
import os
import random

import pygame
import requests
import websockets

from common import Dimensions, Map

logging.basicConfig(level=logging.DEBUG)
logger_websockets = logging.getLogger("websockets")
logger_websockets.setLevel(logging.WARN)

logger = logging.getLogger("Viewer")
logger.setLevel(logging.DEBUG)

BLOCK_SIDE = 30
BLOCK_SIZE = BLOCK_SIDE, BLOCK_SIDE

COLORS = {
    "white": (255, 255, 255),
    "red": (255, 0, 0),
    "pink": (255, 105, 180),
    "blue": (135, 206, 235),
    "orange": (255, 165, 0),
    "yellow": (255, 255, 0),
    "grey": (120, 120, 120),
    "green": (0, 240, 0),
}

COLOR_MAP = dict()


async def messages_handler(websocket_path, queue):
    """Handles server side messages, putting them into a queue."""
    async with websockets.connect(websocket_path) as websocket:
        await websocket.send(json.dumps({"cmd": "join"}))

        while True:
            update = await websocket.recv()
            queue.put_nowait(update)


def scale(pos):
    """Scale positions according to gfx."""
    x, y = pos
    return int(x * BLOCK_SIDE / SCALE), int(y * BLOCK_SIDE / SCALE)


def draw_info(surface, text, pos, color=(0, 0, 0), background=None):
    """Creates text based surfaces for information display."""
    myfont = pygame.font.Font(None, int(24 / SCALE))
    textsurface = myfont.render(text, True, color, background)

    x, y = pos
    if x > surface.get_width():
        pos = surface.get_width() - (textsurface.get_width() + 10), y
    if y > surface.get_height():
        pos = x, surface.get_height() - textsurface.get_height()

    if background:
        surface.blit(background, pos)
    else:
        erase = pygame.Surface(textsurface.get_size())
        erase.fill(COLORS["grey"])

    surface.blit(textsurface, pos)
    return textsurface.get_width(), textsurface.get_height()


async def main_loop(queue):
    """Processes events from server and display's."""
    win = pygame.display.set_mode((600 // SCALE, 1000 // SCALE))
    pygame.display.set_caption("Rush Hour")

    logging.info("Waiting for map information from server")
    state = await queue.get()  # first state message includes map information
    logging.debug("Initial game status: %s", state)
    newgame_json = json.loads(state)
    player_name = ""

    win.fill((0, 0, 0))

    def draw_blocks(grid, cursor, x_offset=0, y_offset=0):
        for x, y, piece in Map(grid).coordinates:

            if piece not in COLOR_MAP:
                COLOR_MAP[piece] = [
                    random.randint(25, 255),
                    random.randint(25, 255),
                    random.randint(25, 255),
                ]

            pygame.draw.rect(
                win,
                COLOR_MAP[piece],
                (
                    (x + x_offset) * BLOCK_SIDE / SCALE,
                    (y + y_offset) * BLOCK_SIDE / SCALE,
                    BLOCK_SIDE / SCALE,
                    BLOCK_SIDE / SCALE,
                ),
                0,
            )

        cur = Dimensions(*cursor)
        pygame.draw.rect(
            win,
            COLORS["white"],
            (
                (cur.x + x_offset) * BLOCK_SIDE / SCALE,
                (cur.y + y_offset) * BLOCK_SIDE / SCALE,
                BLOCK_SIDE / SCALE,
                BLOCK_SIDE / SCALE,
            ),
            4,
        )

    dimensions = Dimensions(*newgame_json["dimensions"])

    draw_blocks(newgame_json["grid"], newgame_json["cursor"])

    game_speed = newgame_json["game_speed"]

    while True:
        pygame.display.update()

        pygame.event.pump()
        if pygame.key.get_pressed()[pygame.K_ESCAPE]:
            asyncio.get_event_loop().stop()

        try:
            state = json.loads(queue.get_nowait())
            if "score" in state:
                score = state["score"]
            if "player" in state:
                player_name = state["player"]

            if "game_speed" in state:
                game_speed = state["game_speed"]

            win.fill((0, 0, 0))

            if "highscores" in state:
                logging.debug("Final game status: %s", state)

                if GLOBAL_HIGHSCORES:
                    print("FUCK")
                    highscores = [
                        [highscore["player"], highscore["score"]]
                        for highscore in requests.get(GLOBAL_HIGHSCORES).json()
                    ]
                    state["highscores"].extend(highscores)
                    state["highscores"].sort(key=lambda h: h[1], reverse=True)
                    state["highscores"] = state["highscores"][:9]
                    state["highscores"].append([player_name, score])
                    state["highscores"].sort(key=lambda h: h[1], reverse=True)

                draw_info(win, "HIGHSCORES", scale((5, 5)), COLORS["blue"])
                for idx, [name, sc] in enumerate(state["highscores"]):
                    draw_info(
                        win,
                        f"{sc:>05}    {name:<24}",
                        scale((5, 6 + idx)),
                        COLORS["orange"]
                        if [player_name, score] == [name, sc]
                        else COLORS["white"],
                    )
                continue

            logger.info(state)
            draw_blocks(state["grid"], state["cursor"])

            draw_info(
                win,
                f"{player_name}",
                scale((dimensions.x + 1, dimensions.y - 1)),
                COLORS["white"],
            )
            draw_info(
                win,
                f"SCORE: {score}",
                scale((dimensions.x + 1, dimensions.y)),
                COLORS["white"],
            )

        except asyncio.queues.QueueEmpty:
            await asyncio.sleep(1.0 / game_speed)
            continue


if __name__ == "__main__":
    SERVER = os.environ.get("SERVER", "localhost")
    PORT = os.environ.get("PORT", "8000")

    parser = argparse.ArgumentParser()
    parser.add_argument("--server", help="IP address of the server", default=SERVER)
    parser.add_argument(
        "--scale", help="reduce size of window by x times", type=int, default=1
    )
    parser.add_argument("--port", help="TCP port", type=int, default=PORT)
    parser.add_argument(
        "--global-highscores",
        help="Retrieve global highscores",
        default=False,
        action="store_true",
    )
    parser.add_argument(
        "--grading-server",
        help="url of grading server",
        default="http://atnog-tetriscores.av.it.pt/highscores",
    )
    arguments = parser.parse_args()
    SCALE = arguments.scale
    GLOBAL_HIGHSCORES = (
        arguments.grading_server if arguments.global_highscores else None
    )

    pygame.font.init()

    async def main():
        q = asyncio.Queue()
        # PROGRAM_ICON = pygame.image.load("data/tetris_block.png")
        # pygame.display.set_icon(PROGRAM_ICON)

        ws_path = f"ws://{arguments.server}:{arguments.port}/viewer"

        await asyncio.gather(messages_handler(ws_path, q), main_loop(q))

    try:
        asyncio.run(main())
    except RuntimeError as err:
        logger.error(err)
