import pygame
import sys
import time
from Ambiente import Ambiente
from Vento import ClimaMarkov
from Agente import Carcara


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

        # 1. PRIMEIRO o pássaro pensa e escolhe o alvo (usando o vento atual)
        self.carcara.escolher_melhor_alvo(self.estado_vento)
        
        # 2. SEGUNDO, com o alvo definido, geramos a tabela de métricas
        self.gerar_relatorio_desempenho()
        
        # 3. TERCEIRO, definimos a rota visual inicial do A* para a animação
        self.algoritmo_atual = "A*" 
        self.caminho_atual, _ = self.motores.a_estrela(
            self.carcara.posicao, self.carcara.alvo_atual, self.carcara.carregando_comida
        )
        
        # O temporizador da animação
        self.delay_passo = 300 
        self.tempo_ultimo_passo = pygame.time.get_ticks()

    def gerar_relatorio_desempenho(self):
        """Avalia o saldo de energia biológico e o custo computacional para cada algoritmo."""
        
        if self.carcara.alvo_atual is None:
            print("ERRO CRÍTICO: O Carcará não encontrou nenhuma comida no mapa!")
            sys.exit()
            
        # Pega as informações reais da comida alvo para a matemática
        comida_alvo = self.mapa.posicao_comida[self.carcara.alvo_atual]
        valor_nutricional = comida_alvo["valor"]
        nome_comida = comida_alvo["nome"]
            
        print("\n" + "="*105)
        print(f" RELATÓRIO COMPLETO (Alvo: {nome_comida} | {valor_nutricional * 10} kcal) ")
        print("="*105)
        

        print(f"{'Algoritmo':<10} | {'Passos (Gasto)':<15} | {'Risco (Dano)':<15} | {'Saldo Final':<15} | {'Tempo (ms)':<12} | {'Nós Exp.'}")
        print("-" * 105)

        algoritmos_para_testar = ["A*", "GREEDY", "BFS", "DFS"]
        
        for alg in algoritmos_para_testar:
  
            inicio_tempo = time.perf_counter()

            if alg == "A*":
                caminho, nos = self.motores.a_estrela(self.carcara.posicao, self.carcara.alvo_atual, False)
            elif alg == "GREEDY":
                caminho, nos = self.motores.busca_gulosa_greedy(self.carcara.posicao, self.carcara.alvo_atual, False)
            elif alg == "BFS":
                caminho, nos = self.motores.busca_em_largura_bfs(self.carcara.posicao, self.carcara.alvo_atual, False)
            elif alg == "DFS":
                caminho, nos = self.motores.busca_em_profundidade_dfs(self.carcara.posicao, self.carcara.alvo_atual, False)
                
            fim_tempo = time.perf_counter()
            tempo_ms = (fim_tempo - inicio_tempo) * 1000
            
            if not caminho:
                print(f"{alg:<10} | FALHOU EM ENCONTRAR ROTA")
                continue
                
            passos_dados = len(caminho)
            dano_predadores = 0
            
            for x, y in caminho:
                valor_chao = self.mapa.grid[y][x]
                if valor_chao == 5: 
                    dano_predadores += 15 
                    
            saldo_energia = (valor_nutricional*10) - passos_dados - dano_predadores
            
            str_passos = f"-{passos_dados}"
            str_dano = f"-{dano_predadores}" if dano_predadores > 0 else "Seguro"
            str_saldo = f"{saldo_energia} kcal"
            
            print(f"{alg:<10} | {str_passos:<15} | {str_dano:<15} | {str_saldo:<15} | {tempo_ms:<12.3f} | {nos}")
            
        print("="*105 + "\n")
        
        self.algoritmo_atual = "A*"
        self.caminho_atual, _ = self.motores.a_estrela(self.carcara.posicao, self.carcara.alvo_atual, self.carcara.carregando_comida)

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

                    coordenada = (x, y)

                    if coordenada in self.mapa.posicao_comida:
                        nome_comida = self.mapa.posicao_comida[coordenada]["nome"]
                        cor_bloco = CORES[nome_comida] 
                    else:

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

