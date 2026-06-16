import heapq
import random
from collections import deque

class AlgoritmosDeBusca:
    def __init__(self, mapa_ambiente, clima_atual):
        self.mapa = mapa_ambiente
        self.clima = clima_atual

    def _pegar_vizinhos_validos(self, posicao):
        """Retorna os vizinhos (cima, baixo, esquerda, direita) dentro dos limites da malha."""
        x, y = posicao
        
        movimentos = [
            (0, -1),  # Cima
            (0, 1),   # Baixo
            (-1, 0),  # Esquerda
            (1, 0)    # Direita
        ]
        
        vizinhos = []
        for dx, dy in movimentos:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.mapa.largura and 0 <= ny < self.mapa.altura:
                vizinhos.append(((nx, ny), (dx, dy)))
        return vizinhos

    def _calcular_custo(self, custo_chao, vetor_movimento, carregando_peso):
        """Calcula o custo do terreno + penalidade do vento de Markov."""
        if isinstance(custo_chao, str):
            custo_chao = 1
            
        custo_final = custo_chao
        vetor_vento = self.clima["vetor"]
        forca_vento = self.clima["forca"]

        
        custo_final = custo_chao
        
 
        if (vetor_vento[0] != 0 and vetor_movimento[0] == -vetor_vento[0]) or \
           (vetor_vento[1] != 0 and vetor_movimento[1] == -vetor_vento[1]):
            
            penalidade = forca_vento * 2 if carregando_peso else forca_vento
            custo_final += penalidade
            
        return custo_final

    def _distancia_manhattan(self, pos_atual, alvo):
        """Heurística h(n) para o A* e para o Greedy."""
        return abs(pos_atual[0] - alvo[0]) + abs(pos_atual[1] - alvo[1])

    def _reconstruir_caminho(self, veio_de, inicio, alvo):
        """Função auxiliar para traçar a rota de volta do alvo até o início."""
        caminho = []
        passo_atual = alvo
        while passo_atual != inicio:
            caminho.append(passo_atual)
            passo_atual = veio_de.get(passo_atual)
            if passo_atual is None: return [] # Caminho sem saída
            
        caminho.reverse()
        return caminho

    # ==========================================
    # 1. BFS (Busca em Largura)
    # ==========================================
    def busca_em_largura_bfs(self, inicio, alvo, carregando_peso=False):
        fila = deque()
        fila.append(inicio)
        veio_de = {inicio: None}
        nos_expandidos = 0
        
        while fila:
            atual = fila.popleft() # FIFO: Tira o primeiro que entrou
            nos_expandidos += 1
            
            if atual == alvo:
                break
                
            for vizinho, _ in self._pegar_vizinhos_validos(atual):
                if vizinho not in veio_de:
                    fila.append(vizinho)
                    veio_de[vizinho] = atual
                    
        return self._reconstruir_caminho(veio_de, inicio, alvo), nos_expandidos

    # ==========================================
    # 2. DFS (Busca em Profundidade)
    # ==========================================
    def busca_em_profundidade_dfs(self, inicio, alvo, carregando_peso=False):
        pilha = []
        pilha.append(inicio)
        veio_de = {inicio: None}
        nos_expandidos = 0
        
        while pilha:
            atual = pilha.pop() # LIFO: Tira o último que entrou
            nos_expandidos += 1
            
            if atual == alvo:
                break
                
            for vizinho, _ in self._pegar_vizinhos_validos(atual):
                if vizinho not in veio_de:
                    pilha.append(vizinho)
                    veio_de[vizinho] = atual
                    
        return self._reconstruir_caminho(veio_de, inicio, alvo), nos_expandidos

    # ==========================================
    # 3. Greedy Best-First (Busca Gulosa)
    # ==========================================
    def busca_gulosa_greedy(self, inicio, alvo, carregando_peso=False):
        fila_prioridade = []
        heapq.heappush(fila_prioridade, (0, inicio))
        veio_de = {inicio: None}
        nos_expandidos = 0
        
        while fila_prioridade:
            # A prioridade é APENAS a heurística h(n)
            _, atual = heapq.heappop(fila_prioridade)
            nos_expandidos += 1
            
            if atual == alvo:
                break
                
            for vizinho, _ in self._pegar_vizinhos_validos(atual):
                if vizinho not in veio_de:
                    # O algoritmo olha apenas para a distância do vizinho até a comida
                    prioridade_h = self._distancia_manhattan(vizinho, alvo)
                    
                    heapq.heappush(fila_prioridade, (prioridade_h, vizinho))
                    veio_de[vizinho] = atual
                    
        return self._reconstruir_caminho(veio_de, inicio, alvo), nos_expandidos

    # ==========================================
    # 4. A* (A-Estrela)
    # ==========================================
    def a_estrela(self, inicio, alvo, carregando_peso=False):
        fila_prioridade = []
        heapq.heappush(fila_prioridade, (0, inicio))
        veio_de = {inicio: None}
        custo_g = {inicio: 0}
        nos_expandidos = 0
        
        while fila_prioridade:
            # A prioridade é f(n) = g(n) + h(n)
            _, atual = heapq.heappop(fila_prioridade)
            nos_expandidos += 1
            
            if atual == alvo:
                break
                
            for vizinho, vetor_mov in self._pegar_vizinhos_validos(atual):
                vx, vy = vizinho
                custo_chao = self.mapa.grid[vy][vx]
                
                custo_passo = self._calcular_custo(custo_chao, vetor_mov, carregando_peso)
                novo_custo_g = custo_g[atual] + custo_passo
                
                if vizinho not in custo_g or novo_custo_g < custo_g[vizinho]:
                    custo_g[vizinho] = novo_custo_g
                    
                    distancia_h = self._distancia_manhattan(vizinho, alvo)
                    custo_f = novo_custo_g + distancia_h 
                    
                    heapq.heappush(fila_prioridade, (custo_f, vizinho))
                    veio_de[vizinho] = atual
                    
        return self._reconstruir_caminho(veio_de, inicio, alvo), nos_expandidos
    
    def aprendizado_por_reforco_qlearning(self, pos_inicial, alvo, carregando_comida=False):
        """O Carcará treina milhares de vezes mentalmente antes de voar de verdade."""
        acoes = [(0, -1), (0, 1), (-1, 0), (1, 0)] 
        q_table = {}
        
        alpha = 0.1      
        gamma = 0.95     
        epsilon = 1.0    
        epsilon_decay = 0.99
        min_epsilon = 0.01
        episodios = 2000 #
        
        def get_q(estado, acao):
            return q_table.get((estado, acao), 0.0)
            
        nos_explorados = set()
        

        for ep in range(episodios):
            estado = pos_inicial
            passos = 0
            
            while estado != alvo and passos < 100:
                nos_explorados.add(estado)
                

                if random.uniform(0, 1) < epsilon:
                    acao = random.choice(acoes)
                else:
                    q_valores = [get_q(estado, a) for a in acoes]
                    max_q = max(q_valores)
                    acoes_vencedoras = [a for a, q in zip(acoes, q_valores) if q == max_q]
                    acao = random.choice(acoes_vencedoras)
                    
                prox_x = estado[0] + acao[0]
                prox_y = estado[1] + acao[1]
                prox_estado = (prox_x, prox_y)
                

                if 0 <= prox_x < self.mapa.largura and 0 <= prox_y < self.mapa.altura:
                    valor_bloco = self.mapa.grid[prox_y][prox_x]
                    
                    if prox_estado == alvo:
                        recompensa = 100  
                    elif valor_bloco == 5:
                        recompensa = -50  
                    else:
                        recompensa = -1   
                else:
                    prox_estado = estado  
                    recompensa = -10
                    
                max_prox_q = max([get_q(prox_estado, a) for a in acoes])
                q_atual = get_q(estado, acao)
                novo_q = q_atual + alpha * (recompensa + gamma * max_prox_q - q_atual)
                
                q_table[(estado, acao)] = novo_q
                estado = prox_estado
                passos += 1
                

            epsilon = max(min_epsilon, epsilon * epsilon_decay)
            
        caminho = []
        estado = pos_inicial
        passos = 0
        
        while estado != alvo and passos < 100:
            q_valores = [get_q(estado, a) for a in acoes]
            max_q = max(q_valores)
            
            if max_q == 0.0 and all(q == 0 for q in q_valores):
                break 
                
            acao = acoes[q_valores.index(max_q)]
            estado = (estado[0] + acao[0], estado[1] + acao[1])
            caminho.append(estado)
            passos += 1
            
        return caminho, len(nos_explorados)