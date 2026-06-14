import pygame
import sys
from Ambiente import Ambiente
from Vento import ClimaMarkov
from Agente import Carcara
# IMPORTANTE: ajuste o nome do arquivo abaixo para bater com o seu (ex: Algoritimos ou algoritmos)
from Algoritimos import AlgoritmosDeBusca 

# --- CONFIGURAÇÕES VISUAIS ---
TAMANHO_BLOCO = 30
FPS = 60

CORES = {
    "chao": (240, 230, 190),     
    "predador": (200, 50, 50),   
    "ninho": (50, 150, 200),     
    "linhas": (200, 190, 150),
    "carcara": (30, 30, 30),     
    "caminho": (100, 100, 255),
    
    "comida": (50, 200, 50),
    # Novas cores para cada tipo de recompensa
    "Inseto": (150, 250, 150),   # Verde claro (menor valor)
    "Lagarto": (255, 165, 0),    # Laranja (médio valor)
    "Carcaça": (128, 0, 128)     # Roxo escuro (alto valor)
}

class InterfaceGrafica:
    def __init__(self, mapa_ambiente, carcara, clima, motores):
        self.mapa = mapa_ambiente
        self.carcara = carcara
        self.clima = clima
        self.motores = motores
        
        self.largura_tela = self.mapa.largura * TAMANHO_BLOCO
        self.altura_tela = self.mapa.altura * TAMANHO_BLOCO
        
        pygame.init()
        self.tela = pygame.display.set_mode((self.largura_tela, self.altura_tela))
        pygame.display.set_caption("Simulador de IA: O Voo do Carcará")
        self.clock = pygame.time.Clock()
        
        # --- ESTADOS DA SIMULAÇÃO ---
        self.fase_atual = "IDA"
        self.estado_vento = self.clima.passar_turno()
        self.motores.clima = self.estado_vento
        
        self.carcara.escolher_melhor_alvo()
        self.caminho_atual, _ = self.motores.a_estrela(
            self.carcara.posicao, self.carcara.alvo_atual, self.carcara.carregando_comida
        )
        
        # Temporizador para a animação (Move a cada 300 milissegundos)
        self.delay_passo = 300 
        self.tempo_ultimo_passo = pygame.time.get_ticks()

    def desenhar_grid(self):
        """Desenha o chão, os perigos, o ninho e identifica as comidas."""
        self.tela.fill(CORES["chao"])
        
        for y in range(self.mapa.altura):
            for x in range(self.mapa.largura):
                valor_celula = self.mapa.grid[y][x]
                cor_bloco = None
                
                if valor_celula == 5:
                    cor_bloco = CORES["predador"]
                elif valor_celula == "N":
                    cor_bloco = CORES["ninho"]
                elif valor_celula == "C":
                    # --- A LÓGICA DAS COMIDAS ENTRA AQUI ---
                    coordenada = (x, y)
                    # Verifica se a comida ainda existe no dicionário (se não foi comida)
                    if coordenada in self.mapa.posicao_comida:
                        nome_comida = self.mapa.posicao_comida[coordenada]["nome"]
                        cor_bloco = CORES[nome_comida] # Puxa a cor exata da paleta
                    else:
                        # Se já foi comida, vira chão normal
                        self.mapa.grid[y][x] = 1 
                        cor_bloco = CORES["chao"]
                    
                if cor_bloco:
                    pygame.draw.rect(
                        self.tela, cor_bloco, 
                        (x * TAMANHO_BLOCO, y * TAMANHO_BLOCO, TAMANHO_BLOCO, TAMANHO_BLOCO)
                    )
                
                pygame.draw.rect(
                    self.tela, CORES["linhas"], 
                    (x * TAMANHO_BLOCO, y * TAMANHO_BLOCO, TAMANHO_BLOCO, TAMANHO_BLOCO), 1
                )

    def desenhar_agente_e_caminho(self):
        """Desenha a rota planejada e o próprio pássaro por cima de tudo."""
        # Desenha bolinhas azuis para mostrar qual caminho a IA quer fazer
        for pos_x, pos_y in self.caminho_atual:
            centro_x = pos_x * TAMANHO_BLOCO + (TAMANHO_BLOCO // 2)
            centro_y = pos_y * TAMANHO_BLOCO + (TAMANHO_BLOCO // 2)
            pygame.draw.circle(self.tela, CORES["caminho"], (centro_x, centro_y), 4)

        # Desenha o Carcará (Círculo preto)
        cx = self.carcara.posicao[0] * TAMANHO_BLOCO + (TAMANHO_BLOCO // 2)
        cy = self.carcara.posicao[1] * TAMANHO_BLOCO + (TAMANHO_BLOCO // 2)
        
        # Se estiver pesado na volta, desenha ele um pouco maior e com contorno verde
        raio = 12 if self.carcara.carregando_comida else 10
        pygame.draw.circle(self.tela, CORES["carcara"], (cx, cy), raio)
        if self.carcara.carregando_comida:
            pygame.draw.circle(self.tela, CORES["comida"], (cx, cy), raio, 3)

    def atualizar_ia(self):
        """A lógica que roda a cada frame para controlar o tempo e o vento."""
        if self.fase_atual == "CONCLUIDO":
            return # A simulação acabou, apenas mantém a tela aberta

        tempo_atual = pygame.time.get_ticks()
        
        # Só dá um passo se o tempo de espera (delay) já passou
        if tempo_atual - self.tempo_ultimo_passo > self.delay_passo:
            self.tempo_ultimo_passo = tempo_atual
            
            # Se chegou no alvo atual
            if self.carcara.posicao == self.carcara.alvo_atual:
                if self.fase_atual == "IDA":
                    print("Carcará pegou a comida! Recalculando rota de volta para o ninho...")
                    self.carcara.pegar_comida()
                    self.fase_atual = "VOLTA"
                    self.caminho_atual, _ = self.motores.a_estrela(
                        self.carcara.posicao, self.carcara.alvo_atual, self.carcara.carregando_comida
                    )
                else:
                    print("Simulação Concluída! O Carcará voltou em segurança.")
                    self.fase_atual = "CONCLUIDO"
                return

            # Dá um passo no mapa
            if self.caminho_atual:
                self.carcara.posicao = self.caminho_atual.pop(0)
                
                # Rola os dados do Clima (Cadeia de Markov)
                vento_anterior = self.estado_vento
                self.estado_vento = self.clima.passar_turno()
                self.motores.clima = self.estado_vento
                
                # Se o vento mudou, joga a rota velha fora e recalcula visualmente
                if self.estado_vento["nome"] != vento_anterior["nome"]:
                    print(f"O Vento mudou para {self.estado_vento['nome']}! Recalculando...")
                    self.caminho_atual, _ = self.motores.a_estrela(
                        self.carcara.posicao, self.carcara.alvo_atual, self.carcara.carregando_comida
                    )

    def rodar(self):
        rodando = True
        while rodando:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    rodando = False
                    
            self.atualizar_ia()
            
            self.desenhar_grid()
            self.desenhar_agente_e_caminho()
            
            # Escreve o estado do vento no topo da janela para acompanharmos
            pygame.display.set_caption(f"IA Carcará | Vento Atual: {self.estado_vento['nome']} | Fase: {self.fase_atual}")
            
            pygame.display.flip()
            self.clock.tick(FPS)
            
        pygame.quit()
        sys.exit()

