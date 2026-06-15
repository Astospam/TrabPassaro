import math

class Carcara:
    def __init__(self, mapa_ambiente):
        self.mapa = mapa_ambiente
        self.posicao = self.mapa.posicao_ninho
        
        # Estados do Agente
        self.carregando_comida = False
        self.alvo_atual = None
        self.caminho_planejado = []
        
    def _estimar_custo_com_vento(self, destino, clima_atual):
        """Calcula a distância e soma uma penalidade se o alvo estiver contra o vento."""
        x1, y1 = self.posicao
        x2, y2 = destino
        distancia_base = abs(x1 - x2) + abs(y1 - y2)
        
        # Se não há clima ou o vento está parado, retorna só a distância
        if not clima_atual or clima_atual["vetor"] == (0, 0):
            return distancia_base
            
        vetor_vento = clima_atual["vetor"]
        forca_vento = clima_atual["forca"]
        
        dir_x = 1 if x2 > x1 else (-1 if x2 < x1 else 0)
        dir_y = 1 if y2 > y1 else (-1 if y2 < y1 else 0)
        
        penalidade = 0
        if dir_x == -vetor_vento[0] and dir_x != 0:
            penalidade += forca_vento * abs(x1 - x2)
        if dir_y == -vetor_vento[1] and dir_y != 0:
            penalidade += forca_vento * abs(y1 - y2)
            
        custo_final = distancia_base + penalidade
        return custo_final if custo_final > 0 else 1

    # O SEGREDO ESTÁ AQUI: Agora a função aceita o clima_atual como parâmetro!
    def escolher_melhor_alvo(self, clima_atual=None):
        """Avalia todas as comidas considerando o valor nutricional e o esforço do vento."""
        melhor_utilidade = -1
        melhor_alvo = None
        
        print("\n--- O Carcará está avaliando as opções ---")
        
        # Usando o mesmo nome de dicionário que você usou na sua interface
        for coordenada, comida in self.mapa.posicao_comida.items():
            # Agora a estimativa considera o clima para prever o cansaço
            custo_esforco = self._estimar_custo_com_vento(coordenada, clima_atual)
            
            # Fórmula de Utilidade: Recompensa / Esforço
            utilidade = comida["valor"] / custo_esforco
            
            print(f"Alvo em {coordenada} | {comida['nome']} (Valor: {comida['valor']}) | Utilidade: {utilidade:.2f}")
            
            if utilidade > melhor_utilidade:
                melhor_utilidade = utilidade
                melhor_alvo = coordenada
                
        self.alvo_atual = melhor_alvo
        if melhor_alvo:
            nome = self.mapa.posicao_comida[melhor_alvo]['nome']
            print(f">>> Decisão da IA: O alvo ideal no momento é {nome} em {melhor_alvo}")
            
        return melhor_alvo

    def pegar_comida(self):
        """Muda o estado do agente para a Fase de Volta."""
        if self.posicao in self.mapa.posicao_comida:
            comida_coletada = self.mapa.posicao_comida.pop(self.posicao)
            self.carregando_comida = True
            
            print(f"\n[!] Carcará abocanhou: {comida_coletada['nome']}! Ele agora está pesado.")
            
            self.alvo_atual = self.mapa.posicao_ninho
            print(f">>> Novo alvo: Voltar para o ninho em {self.alvo_atual}")