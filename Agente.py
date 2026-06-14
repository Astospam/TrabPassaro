import math

class Carcara:
    def __init__(self, ambiente_ambiente):

        self.ambiente = ambiente_ambiente
        self.posicao = self.ambiente.posicao_ninho
        
        self.carregando_comida = False
        self.alvo_atual = None
        self.caminho_planejado = []
        
    def _estimar_custo_heuristico(self, destino):
        """
        Uma estimativa rápida de custo (distância de Manhattan) para a tomada de decisão.
        """
        x1, y1 = self.posicao
        x2, y2 = destino
        return abs(x1 - x2) + abs(y1 - y2)

    def escolher_melhor_alvo(self):

        melhor_utilidade = -1
        melhor_alvo = None
        
        print("--- O Carcará está pensando ---")
        
        for coordenada, comida in self.ambiente.posicao_comida.items():
            distancia = self._estimar_custo_heuristico(coordenada)
            
            if distancia == 0:
                distancia = 1 
                
            utilidade = comida["valor"] / distancia
            
            print(f"Alvo em {coordenada} | {comida['nome']} (Valor: {comida['valor']}) | Distância: {distancia} | Utilidade: {utilidade:.2f}")
            
            if utilidade > melhor_utilidade:
                melhor_utilidade = utilidade
                melhor_alvo = coordenada
                
        self.alvo_atual = melhor_alvo
        print(f">>> Carcará avistou sua Comida!: {self.ambiente.posicao_comida[melhor_alvo]['nome']} em {melhor_alvo}")
        return melhor_alvo

    def pegar_comida(self):

        if self.posicao in self.ambiente.posicao_comida:
            comida_coletada = self.ambiente.posicao_comida.pop(self.posicao)
            self.carregando_comida = True
            print(f"\nCarcará pegou {comida_coletada['nome']}! Ele agora está pesado.")
            
            self.alvo_atual = self.ambiente.posicao_ninho
            print(f"Novo alvo: Voltar para o ninho em {self.alvo_atual}")