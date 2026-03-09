from __future__ import annotations

from dataclasses import asdict, dataclass
from statistics import mean
from typing import Dict, List


@dataclass
class SimulacaoParametros:
    """Parâmetros para simulação macro simplificada com regra de Taylor."""

    periodos: int = 24
    inflacao_inicial: float = 4.5
    meta_inflacao: float = 3.0
    hiato_produto_inicial: float = -0.5
    juros_neutro: float = 4.0
    juros_inicial: float | None = None
    alfa_taylor: float = 1.5
    beta_taylor: float = 0.5
    inercia_inflacao: float = 0.7
    sensibilidade_hiato_juros: float = 0.2
    sensibilidade_inflacao_hiato: float = 0.3
    persistencia_hiato: float = 0.6
    limite_inferior_juros: float = 0.0
    choque_inflacao: float = 0.0
    choque_hiato: float = 0.0
    inflacao_min: float = 0.0
    inflacao_max: float = 20.0
    hiato_min: float = -5.0
    hiato_max: float = 5.0
    debug: bool = False

    def validar(self) -> None:
        if self.periodos <= 0:
            raise ValueError("periodos deve ser maior que zero")
        if not 0 <= self.inercia_inflacao <= 1:
            raise ValueError("inercia_inflacao deve estar entre 0 e 1")
        if not 0 <= self.persistencia_hiato <= 1:
            raise ValueError("persistencia_hiato deve estar entre 0 e 1")
        if self.sensibilidade_hiato_juros < 0:
            raise ValueError("sensibilidade_hiato_juros não pode ser negativa")
        if self.limite_inferior_juros < 0:
            raise ValueError("limite_inferior_juros não pode ser negativo")
        if self.juros_inicial is not None and self.juros_inicial < self.limite_inferior_juros:
            raise ValueError("juros_inicial não pode ser menor que limite_inferior_juros")
        if self.inflacao_min > self.inflacao_max:
            raise ValueError("inflacao_min não pode ser maior que inflacao_max")
        if self.hiato_min > self.hiato_max:
            raise ValueError("hiato_min não pode ser maior que hiato_max")


@dataclass
class EstadoPeriodo:
    periodo: int
    inflacao: float
    hiato_produto: float
    juros_nominal: float


class SimuladorPoliticaMonetaria:
    def __init__(self, parametros: SimulacaoParametros):
        parametros.validar()
        self.parametros = parametros

    def calcular_juros(self, inflacao: float, hiato_produto: float) -> float:
        p = self.parametros
        desvio_meta = inflacao - p.meta_inflacao
        juros = p.juros_neutro + p.alfa_taylor * desvio_meta + p.beta_taylor * hiato_produto
        return max(juros, p.limite_inferior_juros)

    def proximo_estado(self, inflacao_atual: float, hiato_atual: float, juros_atual: float) -> Dict[str, float]:
        p = self.parametros

        inflacao_proxima = (
            p.inercia_inflacao * inflacao_atual
            + (1 - p.inercia_inflacao) * p.meta_inflacao
            + p.sensibilidade_inflacao_hiato * hiato_atual
            + p.choque_inflacao
        )

        hiato_proximo = (
            p.persistencia_hiato * hiato_atual
            - p.sensibilidade_hiato_juros * (juros_atual - p.juros_neutro)
            + p.choque_hiato
        )

        inflacao_proxima = min(max(inflacao_proxima, p.inflacao_min), p.inflacao_max)
        hiato_proximo = min(max(hiato_proximo, p.hiato_min), p.hiato_max)

        juros_proximo = self.calcular_juros(inflacao_proxima, hiato_proximo)

        return {"inflacao": inflacao_proxima, "hiato_produto": hiato_proximo, "juros_nominal": juros_proximo}

    def simular(self) -> List[EstadoPeriodo]:
        p = self.parametros
        juros_inicial = (
            p.juros_inicial
            if p.juros_inicial is not None
            else self.calcular_juros(p.inflacao_inicial, p.hiato_produto_inicial)
        )

        estados: List[EstadoPeriodo] = [
            EstadoPeriodo(0, p.inflacao_inicial, p.hiato_produto_inicial, juros_inicial)
        ]

        inflacao, hiato, juros = p.inflacao_inicial, p.hiato_produto_inicial, juros_inicial
        for t in range(1, p.periodos + 1):
            novo = self.proximo_estado(inflacao, hiato, juros)
            inflacao, hiato, juros = novo["inflacao"], novo["hiato_produto"], novo["juros_nominal"]
            if p.debug:
                print(f"t={t}, inflacao={inflacao:.2f}, hiato={hiato:.2f}, juros={juros:.2f}")
            estados.append(EstadoPeriodo(t, inflacao, hiato, juros))

        return estados


def resumir_resultados(estados: List[EstadoPeriodo], meta_inflacao: float) -> Dict[str, float]:
    if not estados:
        raise ValueError("A lista de estados não pode ser vazia")

    inflacoes = [e.inflacao for e in estados]
    juros = [e.juros_nominal for e in estados]
    hiatos = [e.hiato_produto for e in estados]
    ultimo = estados[-1]

    return {
        "inflacao_media": mean(inflacoes),
        "juros_medio": mean(juros),
        "hiato_medio": mean(hiatos),
        "inflacao_min": min(inflacoes),
        "inflacao_max": max(inflacoes),
        "juros_min": min(juros),
        "juros_max": max(juros),
        "inflacao_final": ultimo.inflacao,
        "juros_final": ultimo.juros_nominal,
        "hiato_final": ultimo.hiato_produto,
        "erro_final_meta": ultimo.inflacao - meta_inflacao,
    }


def estado_para_dict(estado: EstadoPeriodo) -> Dict[str, float]:
    return asdict(estado)
