import random

class ClimaMarkov:
    def __init__(self):

        self.estados = {
            0: {"nome": "Calmaria", "vetor": (0, 0), "forca": 0},
            1: {"nome": "Vento Leste", "vetor": (1, 0), "forca": 3},  # Sopra para a Direita
            2: {"nome": "Vento Oeste", "vetor": (-1, 0), "forca": 3},  # Sopra para a Esquerda
            3: {"nome": "Vento Norte", "vetor": (0, 1), "forca": 3},   # Sopra para a Cima
            4: {"nome": "Vento Sul", "vetor": (0, -1), "forca": 3}    # Sopra para a Baixo
        }
        
        self.estado_atual = 0 
        
        # Linhas = Estado Atual | Colunas = Probabilidade do Próximo Estado (0, 1, 2, 3, 4)
        self.matriz_transicao = [
            # 0(Calmaria)  1(Leste)   2(Oeste)   3(Norte)   4(Sul)
            [0.60,         0.10,      0.10,      0.10,      0.10],  # Se está Calmaria
            [0.30,         0.45,      0.05,      0.10,      0.10],  # Se está Leste
            [0.30,         0.05,      0.45,      0.10,      0.10],   # Se está Oeste
            [0.30,         0.10,      0.10,      0.45,      0.05],   # Se está Norte
            [0.30,         0.10,      0.10,      0.05,      0.45]   # Se está Sul
        ]

    def passar_turno(self):
        """Roda a roleta de Markov para definir o clima do próximo turno."""
        probabilidades = self.matriz_transicao[self.estado_atual]
        
        novo_estado = random.choices([0, 1, 2, 3, 4], weights=probabilidades, k=1)[0]
        
        self.estado_atual = novo_estado
        return self.estados[self.estado_atual]

# --- Área de Teste Rápido ---
if __name__ == "__main__":
    meu_clima = ClimaMarkov()
    
    print("Iniciando simulação climática (10 turnos):")
    for turno in range(1, 11):
        clima_do_turno = meu_clima.passar_turno()
        print(f"Turno {turno}: {clima_do_turno['nome']}")