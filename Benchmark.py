import csv
import time
from Ambiente import Ambiente
from Vento import ClimaMarkov
from Agente import Carcara
from Algoritimos import AlgoritmosDeBusca

def rodar_experimento_em_massa(num_ambientes=30):
    print("="*60)
    print(f" INICIANDO BENCHMARK: COLETANDO DADOS DE {num_ambientes} AMBIENTES ")
    print("="*60)
    print("Executando simulações nos bastidores...")

    arquivo_csv = "resultados_carcara.csv"
    
    # Cabeçalho limpo, apenas com as 5 variáveis exigidas
    colunas = ["Ambiente_ID", "Algoritmo", "Saldo_Energia", "Tempo_ms", "Nos_Expandidos"]

    # Dicionário acumulador simplificado para as médias
    acumulado = {
        alg: {"saldo": 0, "tempo": 0, "nos": 0, "sucessos": 0}
        for alg in ["A*", "GREEDY", "BFS", "DFS"]
    }

    with open(arquivo_csv, mode="w", newline="", encoding="utf-8") as f:
        escritor = csv.writer(f)
        escritor.writerow(colunas)

        for i in range(1, num_ambientes + 1):
            meu_mapa = Ambiente(20, 20)
            meu_mapa.gerar_ninho()
            meu_mapa.gerar_comida(quantidade=3, raio_exclusao_ninho=8)
            meu_mapa.gerar_predadores(quantidade=20, raio_seguro_ninho=4)
            
            clima = ClimaMarkov()
            estado_vento = clima.passar_turno()
            motores = AlgoritmosDeBusca(meu_mapa, estado_vento)
            carcara = Carcara(meu_mapa)
            
            carcara.escolher_melhor_alvo(estado_vento)
            if carcara.alvo_atual is None:
                continue 
                
            comida_alvo = meu_mapa.posicao_comida[carcara.alvo_atual]
            
            for alg in ["A*", "GREEDY", "BFS", "DFS"]:
                inicio_tempo = time.perf_counter()
                
                if alg == "A*":
                    caminho, nos = motores.a_estrela(carcara.posicao, carcara.alvo_atual, False)
                elif alg == "GREEDY":
                    caminho, nos = motores.busca_gulosa_greedy(carcara.posicao, carcara.alvo_atual, False)
                elif alg == "BFS":
                    caminho, nos = motores.busca_em_largura_bfs(carcara.posicao, carcara.alvo_atual, False)
                elif alg == "DFS":
                    caminho, nos = motores.busca_em_profundidade_dfs(carcara.posicao, carcara.alvo_atual, False)
                
                fim_tempo = time.perf_counter()
                tempo_ms = (fim_tempo - inicio_tempo) * 1000
                
                if caminho:
                    # Calcula as penalidades apenas para achar o saldo
                    passos = len(caminho)
                    dano = sum(15 for x, y in caminho if meu_mapa.grid[y][x] == 5)
                    saldo = (comida_alvo["valor"] * 10) - passos - dano
                    
                    # Salva no CSV apenas as variáveis limpas
                    escritor.writerow([i, alg, saldo, round(tempo_ms, 3), nos])
                    
                    # Acumula para as médias
                    acumulado[alg]["saldo"] += saldo
                    acumulado[alg]["tempo"] += tempo_ms
                    acumulado[alg]["nos"] += nos
                    acumulado[alg]["sucessos"] += 1
                else:
                    escritor.writerow([i, alg, "FALHA", round(tempo_ms, 3), nos])

            if i % 5 == 0 or i == num_ambientes:
                print(f" -> {i}/{num_ambientes} ambientes processados...")

    # Imprime o Resumo Limpo no Terminal
    print("\n" + "="*60)
    print(f" RESUMO DAS MÉDIAS APÓS {num_ambientes} EXPERIMENTOS ")
    print("="*60)
    print(f"{'Algoritmo':<10} | {'Média Saldo':<13} | {'Tempo Médio':<12} | {'Nós Médios'}")
    print("-" * 60)
    
    for alg, dados in acumulado.items():
        sucessos = dados["sucessos"] if dados["sucessos"] > 0 else 1
        m_saldo = dados["saldo"] / sucessos
        m_tempo = dados["tempo"] / sucessos
        m_nos = dados["nos"] / sucessos
        
        print(f"{alg:<10} | {m_saldo:<13.1f} | {m_tempo:<11.3f}ms | {m_nos:.1f}")
        
    print("="*60)
    print(f"\n[SUCESSO] Dados salvos no arquivo '{arquivo_csv}'.")

if __name__ == "__main__":
    # Teste de carga com 50 ambientes
    rodar_experimento_em_massa(num_ambientes=50)