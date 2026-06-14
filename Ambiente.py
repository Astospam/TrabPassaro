import random
import math

class Ambiente:
    def __init__(self, largura, altura):
        self.largura = largura
        self.altura = altura
        # Cria uma matriz preenchida com custo 1 (chão normal/seguro)
        self.grid = [[1 for _ in range(largura)] for _ in range(altura)]
        
        self.posicao_ninho = None
        # Formato: {(x, y): valor_nutricional}
        self.posicao_comida = {}
        
    def calcular_distancia(self, pos1, pos2):
        """Calcula a distância euclidiana entre duas coordenadas (x, y)."""
        return math.hypot(pos2[0] - pos1[0], pos2[1] - pos1[1])

    def gerar_ninho(self):
        """Garante que o ninho fique em um dos cantos do mapa."""
        x = random.choice([1, self.largura - 2])
        y = random.choice([1, self.altura - 2])
        self.posicao_ninho = (x, y)
        self.grid[y][x] = "N" # N = Ninho

    def gerar_comida(self, quantidade, raio_exclusao_ninho):
        """Espalha comidas com diferentes valores nutricionais."""
        tipos_de_comida = [
            {"nome": "Inseto", "valor": 5},
            {"nome": "Lagarto", "valor": 10},
            {"nome": "Carcaça", "valor": 15}
        ]
        
        for _ in range(quantidade):
            while True:
                x = random.randint(0, self.largura - 1)
                y = random.randint(0, self.altura - 1)
                pos_candidata = (x, y)
                
                dist_ninho = self.calcular_distancia(pos_candidata, self.posicao_ninho)
                if dist_ninho >= raio_exclusao_ninho and self.grid[y][x] == 1:
                    self.grid[y][x] = "C" 
                    
                    # Sorteia um tipo de comida e guarda no dicionário
                    comida_sorteada = random.choice(tipos_de_comida)
                    self.posicao_comida[pos_candidata] = comida_sorteada
                    break

    def gerar_predadores(self, quantidade, raio_seguro_ninho):
        """Adiciona áreas de alto risco (peso alto), respeitando a zona segura do ninho."""
        predadores_colocados = 0
        while predadores_colocados < quantidade:
            x = random.randint(0, self.largura - 1)
            y = random.randint(0, self.altura - 1)
            pos_candidata = (x, y)
            
            dist_ninho = self.calcular_distancia(pos_candidata, self.posicao_ninho)
            
            # Regra: Predador não pode nascer dentro do raio seguro do ninho
            # Regra: Predador não pode nascer em cima de comida ou do próprio ninho
            if dist_ninho > raio_seguro_ninho and self.grid[y][x] == 1:
                self.grid[y][x] = 5  # Custo 5 = Área de Risco/Predador
                predadores_colocados += 1

    def imprimir_terminal(self):
        """Visualização temporária para debug no terminal."""
        print("-" * (self.largura * 3))
        for linha in self.grid:
            linha_formatada = []
            for celula in linha:
                if celula == "N":
                    linha_formatada.append(" N ")
                elif celula == "C":
                    linha_formatada.append(" C ")
                elif celula == 5:
                    linha_formatada.append("[X]") # Risco
                else:
                    linha_formatada.append(" . ") # Chão normal
            print("".join(linha_formatada))
        print("-" * (self.largura * 3))

# --- Área de Teste ---
if __name__ == "__main__":

    meu_mapa = Ambiente(15, 15)
    
    meu_mapa.gerar_ninho()
    
    meu_mapa.gerar_comida(quantidade=3, raio_exclusao_ninho=8)
    
    meu_mapa.gerar_predadores(quantidade=20, raio_seguro_ninho=3)

    meu_mapa.imprimir_terminal()