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
    "Inseto": (150, 250, 150),   
    "Lagarto": (255, 165, 0),    
    "Carcaça": (128, 0, 128)     
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
        self.clock = pygame.time.Clock()
        
        # --- ESTADOS DA SIMULAÇÃO ---
        # A interface agora começa pausada, esperando o usuário escolher
        self.fase_atual = "AGUARDANDO_INICIO"
        self.estado_vento = self.clima.passar_turno()
        self.motores.clima = self.estado_vento
        
        self.algoritmo_atual = "Nenhum" 
        self.caminho_atual = [] # Começa sem linha azul
        
        # O pássaro analisa o ambiente, mas não dá nenhum passo ainda
        self.carcara.escolher_melhor_alvo(self.estado_vento)
        
        self.delay_passo = 300 
        self.tempo_ultimo_passo = pygame.time.get_ticks()

        print("\n" + "="*60)
        print(" SIMULAÇÃO PRONTA! AGUARDANDO COMANDO DO USUÁRIO ")
        print("="*60)
        print("Pressione na janela do jogo:")
        print(" [1] - Executar A* (Inteligência Otimizada)")
        print(" [2] - Executar GREEDY (Busca Gulosa Rápida)")
        print(" [3] - Executar BFS (Busca em Largura)")
        print(" [4] - Executar DFS (Busca em Profundidade)")
        print(" [5] - Executar Q-LEARNING (Aprendizado de Máquina)")
        print("="*60 + "\n")

    def _gerar_rota_dinamica(self):
        """Função auxiliar que aciona o motor correto baseado na escolha do usuário."""
        inicio_tempo = time.perf_counter()
        
        if self.algoritmo_atual == "A*":
            caminho, nos = self.motores.a_estrela(self.carcara.posicao, self.carcara.alvo_atual, self.carcara.carregando_comida)
        elif self.algoritmo_atual == "GREEDY":
            caminho, nos = self.motores.busca_gulosa_greedy(self.carcara.posicao, self.carcara.alvo_atual, self.carcara.carregando_comida)
        elif self.algoritmo_atual == "BFS":
            caminho, nos = self.motores.busca_em_largura_bfs(self.carcara.posicao, self.carcara.alvo_atual, self.carcara.carregando_comida)
        elif self.algoritmo_atual == "DFS":
            caminho, nos = self.motores.busca_em_profundidade_dfs(self.carcara.posicao, self.carcara.alvo_atual, self.carcara.carregando_comida)
        elif self.algoritmo_atual == "Q-LEARNING":
            caminho, nos = self.motores.aprendizado_por_reforco_qlearning(self.carcara.posicao, self.carcara.alvo_atual, self.carcara.carregando_comida)
            
        fim_tempo = time.perf_counter()
            
        fim_tempo = time.perf_counter()
        tempo_ms = (fim_tempo - inicio_tempo) * 1000
        
        return caminho, nos, tempo_ms

    def iniciar_simulacao(self, nome_algoritmo):
        """Disparado quando o usuário aperta um número (1 a 4)."""
        self.algoritmo_atual = nome_algoritmo
        self.fase_atual = "IDA"
        
        print(f"\n>>> INICIANDO MOTOR: {self.algoritmo_atual} <<<")
        
        self.caminho_atual, nos, tempo = self._gerar_rota_dinamica()
        
        # Mostra as métricas iniciais no terminal
        if self.caminho_atual:
            print(f" -> Rota Inicial Encontrada: {len(self.caminho_atual)} passos.")
            print(f" -> Nós Expandidos: {nos} | Tempo de Cálculo: {tempo:.3f} ms")
        else:
            print(" -> ALERTA: O algoritmo não encontrou nenhuma rota segura!")

    def desenhar_grid(self):
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
                    pygame.draw.rect(self.tela, cor_bloco, (x * TAMANHO_BLOCO, y * TAMANHO_BLOCO, TAMANHO_BLOCO, TAMANHO_BLOCO))
                
                pygame.draw.rect(self.tela, CORES["linhas"], (x * TAMANHO_BLOCO, y * TAMANHO_BLOCO, TAMANHO_BLOCO, TAMANHO_BLOCO), 1)

    def desenhar_agente_e_caminho(self):
        if self.caminho_atual:
            for pos_x, pos_y in self.caminho_atual:
                centro_x = pos_x * TAMANHO_BLOCO + (TAMANHO_BLOCO // 2)
                centro_y = pos_y * TAMANHO_BLOCO + (TAMANHO_BLOCO // 2)
                pygame.draw.circle(self.tela, CORES["caminho"], (centro_x, centro_y), 4)

        cx = self.carcara.posicao[0] * TAMANHO_BLOCO + (TAMANHO_BLOCO // 2)
        cy = self.carcara.posicao[1] * TAMANHO_BLOCO + (TAMANHO_BLOCO // 2)
        
        raio = 12 if self.carcara.carregando_comida else 10
        pygame.draw.circle(self.tela, CORES["carcara"], (cx, cy), raio)
        if self.carcara.carregando_comida:
            pygame.draw.circle(self.tela, CORES["comida"], (cx, cy), raio, 3)

    def atualizar_ia(self):
        # Impede a movimentação se o jogo estiver pausado ou concluído
        if self.fase_atual in ["CONCLUIDO", "AGUARDANDO_INICIO"]:
            return 

        tempo_atual = pygame.time.get_ticks()
        
        if tempo_atual - self.tempo_ultimo_passo > self.delay_passo:
            self.tempo_ultimo_passo = tempo_atual
            
            if self.carcara.posicao == self.carcara.alvo_atual:
                if self.fase_atual == "IDA":
                    print("\n[!] Carcará pegou a comida! Recalculando rota de volta para o ninho...")
                    self.carcara.pegar_comida()
                    self.fase_atual = "VOLTA"
                    
                    # Usa o motor universal para recalcular com peso
                    self.caminho_atual, _, _ = self._gerar_rota_dinamica()
                else:
                    print("\n[SUCESSO] Simulação Concluída! O Carcará voltou em segurança.")
                    self.fase_atual = "CONCLUIDO"
                return

            if self.caminho_atual:
                self.carcara.posicao = self.caminho_atual.pop(0)
                
                vento_anterior = self.estado_vento
                self.estado_vento = self.clima.passar_turno()
                self.motores.clima = self.estado_vento
                
                if self.estado_vento["nome"] != vento_anterior["nome"]:
                    print(f" -> O Vento mudou para {self.estado_vento['nome']}! Motor {self.algoritmo_atual} recalculando...")
                    
                    if self.fase_atual == "IDA":
                        self.carcara.escolher_melhor_alvo(self.estado_vento)
                        
                    # Usa o motor universal para recalcular fugindo do vento
                    self.caminho_atual, nos_extras, tempo_extra = self._gerar_rota_dinamica()

    def rodar(self):
        rodando = True
        while rodando:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    rodando = False
                
                # --- CONTROLES DO TECLADO ---
                elif event.type == pygame.KEYDOWN:
                    # Só aceita comando se a tela estiver esperando (Aguardando Início)
                    if self.fase_atual == "AGUARDANDO_INICIO":
                        if event.key == pygame.K_1:
                            self.iniciar_simulacao("A*")
                        elif event.key == pygame.K_2:
                            self.iniciar_simulacao("GREEDY")
                        elif event.key == pygame.K_3:
                            self.iniciar_simulacao("BFS")
                        elif event.key == pygame.K_4:
                            self.iniciar_simulacao("DFS")
                        elif event.key == pygame.K_5:
                            self.iniciar_simulacao("Q-LEARNING")
                    
            self.atualizar_ia()
            self.desenhar_grid()
            self.desenhar_agente_e_caminho()
            
            # Atualiza o título da janela para mostrar o status com clareza
            if self.fase_atual == "AGUARDANDO_INICIO":
                pygame.display.set_caption("Simulador | PAUSADO | Aperte 1 (A*), 2 (Greedy), 3 (BFS) ou 4 (DFS)")
            else:
                pygame.display.set_caption(f"IA Carcará | Motor: {self.algoritmo_atual} | Vento: {self.estado_vento['nome']} | Fase: {self.fase_atual}")
            
            pygame.display.flip()
            self.clock.tick(FPS)
            
        pygame.quit()
        sys.exit()