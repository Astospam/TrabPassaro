from Ambiente import Ambiente
from Vento import ClimaMarkov
from Agente import Carcara
from Algoritimos import AlgoritmosDeBusca
from Interface import InterfaceGrafica

def iniciar_projeto():

    meu_mapa = Ambiente(25, 25)
    meu_mapa.gerar_ninho()
    meu_mapa.gerar_comida(quantidade=3, raio_exclusao_ninho=15)
    meu_mapa.gerar_predadores(quantidade=200, raio_seguro_ninho=3)

    clima = ClimaMarkov()
    motores = AlgoritmosDeBusca(meu_mapa, {"nome": "Calmaria", "vetor": (0,0), "forca": 0})
    carcara = Carcara(meu_mapa)
    
    app = InterfaceGrafica(meu_mapa, carcara, clima, motores)
    app.rodar()

if __name__ == "__main__":
    iniciar_projeto()