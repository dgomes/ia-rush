import math
from dataclasses import dataclass

SPACE = " "


@dataclass
class Coordinates:
    x: int
    y: int


Dimensions = Coordinates


class MapException(Exception):
    """Exception Moving Pieces."""


class Map:
    def __init__(self, txt):
        pieces, grid, movements = txt.split(" ")
        self.pieces = int(pieces)
        self.movements = int(movements)
        self.grid_size = int(math.sqrt(len(grid)))
        self.grid = []

        line = []
        for i, pos in enumerate(grid):
            line.append(pos)
            if (i + 1) % self.grid_size == 0:
                self.grid.append(line)
                line = []

    def __repr__(self):
        raw = ""
        for line in self.grid:
            for column in line:
                raw += column
        return f"{self.pieces} {raw} {self.movements}"

    @property
    def coordinates(self):
        _coordinates = []

        for y, line in enumerate(self.grid):
            for x, column in enumerate(line):
                if column != "o":
                    _coordinates.append((x, y, column))

        return _coordinates

    def get(self, cursor: Coordinates):
        if 0 <= cursor.x < self.grid_size and 0 <= cursor.y < self.grid_size:
            return self.grid[int(cursor.y)][int(cursor.x)]
        raise MapException("Out of the grid")

    def piece_coordinates(self, piece):
        return [Coordinates(x, y) for (x, y, p) in self.coordinates if p == piece]

    def move(self, piece, direction: Coordinates):
        piece_coord = self.piece_coordinates(piece)

        # Don't move vertical pieces sideways
        if direction.x != 0 and any([line.count(piece) == 1 for line in self.grid]):
            raise MapException("Can't move sideways")
        # Don't move horizontal pieces up-down
        if direction.y != 0 and any([line.count(piece) > 1 for line in self.grid]):
            raise MapException("Can't move up-down")

        def sum(a, b):
            return Coordinates(a.x + b.x, a.y + b.y)

        for pos in piece_coord:
            if not self.get(sum(pos, direction)) in [piece, "o"]:
                print(self.get(sum(pos, direction)))
                raise MapException("Blocked piece")

        for pos in piece_coord:
            self.grid[pos.y][pos.x] = "o"

        for pos in piece_coord:
            new_pos = sum(pos, direction)
            self.grid[new_pos.y][new_pos.x] = piece

    def test_win(self):
        return any([c.x == self.grid_size - 1 for c in self.piece_coordinates("A")])


""" TODO move to tests
m = Map("02 ooooBoooooBoAAooBooooooooooooooooooo 14")
print(m)
print(m.get(Dimensions(4,0)))
assert m.move("A", Coordinates(1, 0))
assert m.move("A", Coordinates(-1, 0))
assert not m.move("A", Coordinates(0, 1))
assert not m.move("A", Coordinates(0, -1))
assert m.move("B", Coordinates(0, 1))
assert m.move("B", Coordinates(0, -1))
assert not m.move("B", Coordinates(1,0))
assert not m.move("B", Coordinates(-1,0))
print(m)
"""
