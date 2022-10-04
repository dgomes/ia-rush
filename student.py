"""Example client."""
import asyncio
import getpass
import json
import os

# Next 4 lines are not needed for AI agents, please remove them from your code!
import pygame
import websockets

BOARD = []
LEVEL = 0

def play(state, board):
    global BOARD, LEVEL

    dimensions = state["dimensions"]

    # if board not defined
    if  BOARD == [] or dimensions != [len(BOARD), len(BOARD[0])] or LEVEL != state["level"] or board != state["grid"]:
        LEVEL = state["level"]
        BOARD = []

        grid = state["grid"].split(" ")[1]

        for i in range(dimensions[0]):
            BOARD.append([x for x in grid[i*dimensions[0] : i*dimensions[0] + dimensions[1]]])

    print(BOARD)

    if state["selected"] == "":
        # See if there is any block in front of AA
        if BOARD[2].count("o") + BOARD[2].count("A") != dimensions[1]:
            print("something blocking")

            
        else:
            cursor = state["cursor"]

            A = BOARD[2].index("A")
            # [1, 0] cima ; [0, 1] direita
            walk = [cursor[0] - 4, A + 1 - cursor[1]]
            print(walk)

            return (["w"]*abs(walk[0]) if walk[0] < 0 else ["s"] * walk[0]) + (["a"]*abs(walk[1]) if walk[0] < 0 else ["d"] * walk[1]) + [" "] + ["d"]*(dimensions[1] - cursor[1] + 1)
        
    else:
        # execute best path
        return [" ", "a", " ", "d"] #["a", "d"]

    return [" "]




async def agent_loop(server_address="localhost:8000", agent_name="student"):
    """Example client loop."""
    async with websockets.connect(f"ws://{server_address}/player") as websocket:

        # Receive information about static game properties
        await websocket.send(json.dumps({"cmd": "join", "name": agent_name}))

        keys = []
        count = 1
        prev_board = ""

        while True:
            try:
                state = json.loads(
                    await websocket.recv()
                )  # receive game update, this must be called timely or your game will get out of sync with the server

                # skip first message
                if count == 1:
                    count += 1
                    continue

                print(state.get("cursor"))

                # Next lines are only for the Human Agent, the key values are nonetheless the correct ones!
                print(state)

                if len(keys) == 0:
                    keys = play(state, prev_board)

                else:
                    print(keys)
                    await websocket.send(
                        json.dumps({"cmd": "key", "key": keys.pop(0)})
                    )  # send key command to server - you must implement this send in the AI agent

                prev_board = state["grid"]

            except websockets.exceptions.ConnectionClosedOK:
                print("Server has cleanly disconnected us")
                return


# DO NOT CHANGE THE LINES BELLOW
# You can change the default values using the command line, example:
# $ NAME='arrumador' python3 client.py
loop = asyncio.get_event_loop()
SERVER = os.environ.get("SERVER", "localhost")
PORT = os.environ.get("PORT", "8000")
NAME = os.environ.get("NAME", getpass.getuser())
loop.run_until_complete(agent_loop(f"{SERVER}:{PORT}", NAME))
