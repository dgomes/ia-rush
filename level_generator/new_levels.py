from Map_gen import Map_gen
from Search import BFS

def main():
    size = 8
    car_prob = 80
    x_prob = 5
    min_depth = 10
    max_nodes = 0 # acaba quando encontra a solução
    # max_nodes = 30000000
    num_maps = 10

    map = Map_gen()
    map.update(size, car_prob, x_prob)

    maps = []
    while len(maps) < num_maps:
        print("Generating map...")
        map.generate()
        # print_map(map.map)
        # print()
        map.scramble()
        map_str = str(map)
        print_map(map.map)
        BFS.size = map.size
        bfs = BFS(map_str)
        res = bfs.search(min_depth, max_nodes)
        if res is not None:
            maps.append((res[0], map_str, res[1]))
        

    print("\n\nMaps:")
    for i in range(len(maps)):
        depth, map_str, num_nodes = maps[i]
        # print(f"Map {i+1}:")
        # print(f"Board : {map_str}")
        # print(f"Total number of nodes: {num_nodes}")
        # print(f"Moves: {depth}\n")
        print(f"{i+1} {map_str} {num_nodes} {depth}")



def print_map(map):
    for i in range(len(map)):
        for j in range(len(map)):
            print(map[i][j], end=' ')
        print()

if __name__ == '__main__':
    main()