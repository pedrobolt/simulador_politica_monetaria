from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, List


@dataclass
class SimulacaoParametros:
    """Parâmetros principais para a simulação macroeconômica simplificada."""

    periodos: int = 24
    inflacao_inicial: float = 4.5
    meta_inflacao: float = 3.0
    hiato_produto_inicial: float = -0.5
    juros_neutro: float = 4.0
    alfa_taylor: float = 1.5
    beta_taylor: float = 0.5
    inercia_inflacao: float = 0.7
    sensibilidade_hiato_juros: float = 0.2
    choque_inflacao: float = 0.0
    choque_hiato: float = 0.0


@dataclass
class EstadoPeriodo:
    periodo: int
    inflacao: float
    hiato_produto: float
    juros_nominal: float


class SimuladorPoliticaMonetaria:
    """
    Simulador básico de política monetária com:
    - Regra de Taylor para juros.
    - Curva de Phillips simplificada para inflação.
    - Dinâmica simples de hiato do produto.
    """

    def __init__(self, parametros: SimulacaoParametros):
        self.parametros = parametros

    def calcular_juros(self, inflacao: float, hiato_produto: float) -> float:
        p = self.parametros
        desvio_meta = inflacao - p.meta_inflacao
        return p.juros_neutro + p.alfa_taylor * desvio_meta + p.beta_taylor * hiato_produto

    def proximo_estado(self, inflacao_atual: float, hiato_atual: float, juros_atual: float) -> Dict[str, float]:
        p = self.parametros

        # Inflação com inércia e efeito do hiato do produto.
        inflacao_proxima = (
            p.inercia_inflacao * inflacao_atual
            + (1 - p.inercia_inflacao) * p.meta_inflacao
            + 0.3 * hiato_atual
            + p.choque_inflacao
        )

        # Hiato reduz quando juros estão acima da taxa neutra.
        hiato_proximo = (
            0.6 * hiato_atual
            - p.sensibilidade_hiato_juros * (juros_atual - p.juros_neutro)
            + p.choque_hiato
        )

        juros_proximo = self.calcular_juros(inflacao_proxima, hiato_proximo)

        return {
            "inflacao": inflacao_proxima,
            "hiato_produto": hiato_proximo,
            "juros_nominal": juros_proximo,
        }

    def simular(self) -> List[EstadoPeriodo]:
        p = self.parametros

        juros_inicial = self.calcular_juros(p.inflacao_inicial, p.hiato_produto_inicial)
        estados: List[EstadoPeriodo] = [
            EstadoPeriodo(
                periodo=0,
                inflacao=p.inflacao_inicial,
                hiato_produto=p.hiato_produto_inicial,
                juros_nominal=juros_inicial,
            )
        ]

        inflacao, hiato, juros = p.inflacao_inicial, p.hiato_produto_inicial, juros_inicial
        for t in range(1, p.periodos + 1):
            novo = self.proximo_estado(inflacao, hiato, juros)
            inflacao = novo["inflacao"]
            hiato = novo["hiato_produto"]
            juros = novo["juros_nominal"]
            estados.append(
                EstadoPeriodo(
                    periodo=t,
                    inflacao=inflacao,
                    hiato_produto=hiato,
                    juros_nominal=juros,
                )
            )

        return estados


def resumir_resultados(estados: List[EstadoPeriodo], meta_inflacao: float) -> Dict[str, float]:
    inflacoes = [e.inflacao for e in estados]
    juros = [e.juros_nominal for e in estados]
    hiatos = [e.hiato_produto for e in estados]

    ultimo = estados[-1]
    return {
        "inflacao_media": sum(inflacoes) / len(inflacoes),
        "juros_medio": sum(juros) / len(juros),
        "hiato_medio": sum(hiatos) / len(hiatos),
        "inflacao_final": ultimo.inflacao,
        "juros_final": ultimo.juros_nominal,
        "hiato_final": ultimo.hiato_produto,
        "erro_final_meta": ultimo.inflacao - meta_inflacao,
    }


def estado_para_dict(estado: EstadoPeriodo) -> Dict[str, float]:
    return asdict(estado)
