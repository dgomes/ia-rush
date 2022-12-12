from Search import DFS, BFS
import random

class Map_gen:

    def __init__(self):
        self.map = []
        self.size = 10
        self.p_car = 0
        self.p_x = 0
        self.p_o = 0

    
    def update(self, size, p_car, p_x):
        self.size = size
        self.p_car = p_car
        self.p_x = p_x
        self.p_o = 100 - p_car - p_x
        self.map = [['o']* size] * size
        self.map = [[*i] for i in self.map]
        self.map[(size-1)//2][size-1] = 'A'
        self.map[(size-1)//2][size-2] = 'A' 


    def generate(self):
        self.update(self.size, self.p_car, self.p_x)
        letters = ['A']
        probs = ['o']*int(self.p_o) + ['x']*int(self.p_x) + ['car']*int(self.p_car)

        for y in range(self.size):
            for x in range(self.size):
                if self.map[y][x] != 'o':
                    continue
                
                option = random.choice(probs)
                if option == 'o':
                    continue
                elif option == 'x' and y != (self.size-1)//2:
                    self.map[y][x] = 'x'
                elif option == 'car':

                    orientation = random.choice(['h', 'v'])
                    length = random.randint(2, 3)
                    last_letter = letters[-1]
                    if last_letter == 'Z':
                        continue
                    letter = chr(ord(last_letter) + 1)
                    letters.append(letter)

                    if orientation == 'h' and y != (self.size-1)//2:
                        if x + length > self.size:
                            continue
                        for i in range(length):
                            if self.map[y][x+i] != 'o':
                                break
                        else:
                            for i in range(length):
                                self.map[y][x+i] = letter
                    elif orientation == 'v':
                        if y + length > self.size:
                            continue
                        for i in range(length):
                            if self.map[y+i][x] != 'o':
                                break
                        else:
                            for i in range(length):
                                self.map[y+i][x] = letter


    def scramble(self):
        BFS.size = self.size
        dfs = DFS(str(self))
        str_ = dfs.search()
        self.map = [[*str_[i:i+self.size]] for i in range(0, len(str_), self.size)]


    def __str__(self):
        return ''.join([''.join(i) for i in self.map])