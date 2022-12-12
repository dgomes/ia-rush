## Level generator

O ficheiro [new_levels.py](new_levels.py) contém na main as seguintes variáveis:
- size: tamanho do tabuleiro
- car_prob: probabilidade de *tentar* colocar um carro
- x_prob: probabilidade de colocar um 'x' no tabuleiro
- min_depth: numero minimo de moves da solução de um tabuleiro
- max_nodes: numero maximo de nós a explorar (depois de encontrar soluçao) (para nao ocupar demasiado tempo ou ficar sem memoria)
- num_maps: numero de tabuleiros a gerar

O ficheiro [Search.py](Search.py) contém 2 searches:
- BFS 
    - calcular o numero de moves da solução de um tabuleiro
    - calcular o numero de possibilidades de um tabuleiro
- DFS
    - baralhar o tabuleiro inicial
    - (contem algumas variaveis que podem ser ajustadas)