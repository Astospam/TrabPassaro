import random

class ClimaMarkov:
    def __init__(self):

        self.estados = {
            0: {"nome": "Calmaria", "vetor": (0, 0), "forca": 0},
            1: {"nome": "Vento Leste", "vetor": (1, 0), "forca": 3},  # Sopra para a Direita
            2: {"nome": "Vento Oeste", "vetor": (-1, 0), "forca": 3}  # Sopra para a Esquerda
        }
        
        self.estado_atual = 0 
        
        # Linhas = Estado Atual | Colunas = Probabilidade do Próximo Estado (0, 1, 2)
        self.matriz_transicao = [
            # 0(Calmaria)  1(Leste)   2(Oeste)
            [0.60,         0.20,      0.20],  # Se está Calmaria: 60% de continuar, 20% ir pra cada lado
            [0.40,         0.50,      0.10],  # Se está Leste: 50% continua, 40% acalma, 10% vira bruscamente
            [0.40,         0.10,      0.50]   # Se está Oeste: 50% continua, 40% acalma, 10% vira bruscamente
        ]

    def passar_turno(self):
        """Roda a roleta de Markov para definir o clima do próximo turno."""
        probabilidades = self.matriz_transicao[self.estado_atual]
        
        novo_estado = random.choices([0, 1, 2], weights=probabilidades, k=1)[0]
        
        self.estado_atual = novo_estado
        return self.estados[self.estado_atual]

# --- Área de Teste Rápido ---
if __name__ == "__main__":
    meu_clima = ClimaMarkov()
    
    print("Iniciando simulação climática (10 turnos):")
    for turno in range(1, 11):
        clima_do_turno = meu_clima.passar_turno()
        print(f"Turno {turno}: {clima_do_turno['nome']}")