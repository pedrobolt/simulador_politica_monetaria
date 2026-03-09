from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from simulator import (
    SimulacaoParametros,
    SimuladorPoliticaMonetaria,
    estado_para_dict,
    resumir_resultados,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Simulador básico de política monetária com regra de Taylor"
    )
    parser.add_argument("--periodos", type=int, default=24)
    parser.add_argument("--inflacao-inicial", type=float, default=4.5)
    parser.add_argument("--meta-inflacao", type=float, default=3.0)
    parser.add_argument("--hiato-inicial", type=float, default=-0.5)
    parser.add_argument("--juros-neutro", type=float, default=4.0)
    parser.add_argument("--alfa-taylor", type=float, default=1.5)
    parser.add_argument("--beta-taylor", type=float, default=0.5)
    parser.add_argument("--inercia-inflacao", type=float, default=0.7)
    parser.add_argument("--sensibilidade-hiato-juros", type=float, default=0.2)
    parser.add_argument("--choque-inflacao", type=float, default=0.0)
    parser.add_argument("--choque-hiato", type=float, default=0.0)
    parser.add_argument("--saida-json", type=Path, default=Path("resultado_simulacao.json"))
    parser.add_argument("--saida-csv", type=Path, default=Path("trajetoria_simulacao.csv"))
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    parametros = SimulacaoParametros(
        periodos=args.periodos,
        inflacao_inicial=args.inflacao_inicial,
        meta_inflacao=args.meta_inflacao,
        hiato_produto_inicial=args.hiato_inicial,
        juros_neutro=args.juros_neutro,
        alfa_taylor=args.alfa_taylor,
        beta_taylor=args.beta_taylor,
        inercia_inflacao=args.inercia_inflacao,
        sensibilidade_hiato_juros=args.sensibilidade_hiato_juros,
        choque_inflacao=args.choque_inflacao,
        choque_hiato=args.choque_hiato,
    )

    simulador = SimuladorPoliticaMonetaria(parametros)
    estados = simulador.simular()
    resumo = resumir_resultados(estados, meta_inflacao=parametros.meta_inflacao)

    with args.saida_json.open("w", encoding="utf-8") as f:
        json.dump(
            {
                "parametros": parametros.__dict__,
                "resumo": resumo,
                "trajetoria": [estado_para_dict(e) for e in estados],
            },
            f,
            ensure_ascii=False,
            indent=2,
        )

    with args.saida_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["periodo", "inflacao", "hiato_produto", "juros_nominal"])
        writer.writeheader()
        for estado in estados:
            writer.writerow(estado_para_dict(estado))

    print("Simulação concluída.")
    print(f"Arquivo JSON: {args.saida_json}")
    print(f"Arquivo CSV: {args.saida_csv}")
    print("Resumo:")
    for k, v in resumo.items():
        print(f"- {k}: {v:.4f}")


if __name__ == "__main__":
    main()
