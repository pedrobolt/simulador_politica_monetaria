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


CENARIOS = {
    "base": {},
    "hawkish": {"alfa_taylor": 2.0, "beta_taylor": 0.8},
    "dovish": {"alfa_taylor": 1.0, "beta_taylor": 0.2},
    "choque_oferta": {"choque_inflacao": 0.3},
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Simulador de política monetária com regra de Taylor")
    parser.add_argument("--cenario", choices=sorted(CENARIOS.keys()), default="base")
    parser.add_argument("--periodos", type=int, default=24)
    parser.add_argument("--inflacao-inicial", type=float, default=4.5)
    parser.add_argument("--meta-inflacao", type=float, default=3.0)
    parser.add_argument("--hiato-inicial", type=float, default=-0.5)
    parser.add_argument("--juros-neutro", type=float, default=4.0)
    parser.add_argument("--juros-inicial", type=float, help="Define a taxa de juros no período 0")
    parser.add_argument("--alfa-taylor", type=float)
    parser.add_argument("--beta-taylor", type=float)
    parser.add_argument("--inercia-inflacao", type=float, default=0.7)
    parser.add_argument("--sensibilidade-hiato-juros", type=float, default=0.2)
    parser.add_argument("--sensibilidade-inflacao-hiato", type=float, default=0.3)
    parser.add_argument("--persistencia-hiato", type=float, default=0.6)
    parser.add_argument("--limite-inferior-juros", type=float, default=0.0)
    parser.add_argument("--choque-inflacao", type=float)
    parser.add_argument("--choque-hiato", type=float)
    parser.add_argument("--saida-json", type=Path, default=Path("resultado_simulacao.json"))
    parser.add_argument("--saida-csv", type=Path, default=Path("trajetoria_simulacao.csv"))
    parser.add_argument("--gerar-grafico", dest="gerar_grafico", action="store_true", help="Força geração de gráfico")
    parser.add_argument("--sem-grafico", dest="gerar_grafico", action="store_false", help="Não gera gráfico")
    parser.set_defaults(gerar_grafico=True)
    parser.add_argument("--saida-grafico", type=Path, default=Path("grafico_simulacao.svg"))
    return parser


def montar_parametros(args: argparse.Namespace) -> SimulacaoParametros:
    base = CENARIOS[args.cenario]

    def valor(nome: str, default: float) -> float:
        return getattr(args, nome) if getattr(args, nome) is not None else base.get(nome, default)

    return SimulacaoParametros(
        periodos=args.periodos,
        inflacao_inicial=args.inflacao_inicial,
        meta_inflacao=args.meta_inflacao,
        hiato_produto_inicial=args.hiato_inicial,
        juros_neutro=args.juros_neutro,
        juros_inicial=args.juros_inicial,
        alfa_taylor=valor("alfa_taylor", 1.5),
        beta_taylor=valor("beta_taylor", 0.5),
        inercia_inflacao=args.inercia_inflacao,
        sensibilidade_hiato_juros=args.sensibilidade_hiato_juros,
        sensibilidade_inflacao_hiato=args.sensibilidade_inflacao_hiato,
        persistencia_hiato=args.persistencia_hiato,
        limite_inferior_juros=args.limite_inferior_juros,
        choque_inflacao=valor("choque_inflacao", 0.0),
        choque_hiato=valor("choque_hiato", 0.0),
    )


def exportar_csv(destino: Path, estados: list) -> None:
    with destino.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["periodo", "inflacao", "hiato_produto", "juros_nominal"])
        writer.writeheader()
        for estado in estados:
            writer.writerow(estado_para_dict(estado))


def _polyline_points(valores: list[float], x0: float, y0: float, largura: float, altura: float) -> str:
    if not valores:
        return ""
    vmin = min(valores)
    vmax = max(valores)
    span = (vmax - vmin) if vmax != vmin else 1.0
    n = len(valores)
    pontos: list[str] = []
    for i, v in enumerate(valores):
        x = x0 + (i / (n - 1 if n > 1 else 1)) * largura
        y = y0 + altura - ((v - vmin) / span) * altura
        pontos.append(f"{x:.2f},{y:.2f}")
    return " ".join(pontos)


def _bloco_svg(titulo: str, valores: list[float], cor: str, x: float, y: float, largura: float, altura: float) -> str:
    points = _polyline_points(valores, x + 40, y + 20, largura - 60, altura - 45)
    return f"""
  <g>
    <rect x="{x}" y="{y}" width="{largura}" height="{altura}" fill="white" stroke="#ddd"/>
    <text x="{x + 8}" y="{y + 16}" font-size="13" fill="#333">{titulo}</text>
    <polyline points="{points}" fill="none" stroke="{cor}" stroke-width="2"/>
  </g>"""


def exportar_grafico_svg(destino: Path, estados: list) -> None:
    periodos = [e.periodo for e in estados]
    inflacao = [e.inflacao for e in estados]
    juros = [e.juros_nominal for e in estados]
    hiato = [e.hiato_produto for e in estados]

    largura_total = 980
    altura_bloco = 190
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{largura_total}" height="640" viewBox="0 0 {largura_total} 640">
  <rect width="100%" height="100%" fill="#f8fafc"/>
  <text x="20" y="26" font-size="18" font-family="Arial, sans-serif" fill="#111">Trajetória da simulação de política monetária</text>
  <text x="20" y="46" font-size="12" font-family="Arial, sans-serif" fill="#555">Períodos: {periodos[0]} a {periodos[-1]}</text>
  {_bloco_svg("Inflação (%)", inflacao, "#e11d48", 20, 60, 940, altura_bloco)}
  {_bloco_svg("Juros nominais (%)", juros, "#2563eb", 20, 260, 940, altura_bloco)}
  {_bloco_svg("Hiato do produto (p.p.)", hiato, "#059669", 20, 460, 940, 160)}
</svg>
"""
    destino.write_text(svg, encoding="utf-8")


def exportar_grafico(destino: Path, estados: list) -> str:
    # SVG funciona sem dependências externas.
    if destino.suffix.lower() == ".svg":
        exportar_grafico_svg(destino, estados)
        return "svg"

    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise RuntimeError(
            "Para PNG/PDF é necessário matplotlib. Use --saida-grafico grafico_simulacao.svg ou instale matplotlib."
        ) from exc

    periodos = [e.periodo for e in estados]
    inflacao = [e.inflacao for e in estados]
    juros = [e.juros_nominal for e in estados]
    hiato = [e.hiato_produto for e in estados]

    fig, axes = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
    axes[0].plot(periodos, inflacao, color="tab:red", label="Inflação")
    axes[0].set_ylabel("%")
    axes[0].legend(loc="best")
    axes[0].grid(True, alpha=0.3)

    axes[1].plot(periodos, juros, color="tab:blue", label="Juros nominais")
    axes[1].set_ylabel("%")
    axes[1].legend(loc="best")
    axes[1].grid(True, alpha=0.3)

    axes[2].plot(periodos, hiato, color="tab:green", label="Hiato do produto")
    axes[2].set_ylabel("p.p.")
    axes[2].set_xlabel("Período")
    axes[2].legend(loc="best")
    axes[2].grid(True, alpha=0.3)

    fig.suptitle("Trajetória da simulação de política monetária")
    fig.tight_layout()
    fig.savefig(destino, dpi=150)
    plt.close(fig)
    return "matplotlib"


def main() -> None:
    args = build_parser().parse_args()
    parametros = montar_parametros(args)
    simulador = SimuladorPoliticaMonetaria(parametros)

    estados = simulador.simular()
    resumo = resumir_resultados(estados, meta_inflacao=parametros.meta_inflacao)

    with args.saida_json.open("w", encoding="utf-8") as f:
        json.dump(
            {
                "cenario": args.cenario,
                "parametros": parametros.__dict__,
                "resumo": resumo,
                "trajetoria": [estado_para_dict(e) for e in estados],
            },
            f,
            ensure_ascii=False,
            indent=2,
        )

    exportar_csv(args.saida_csv, estados)

    print(f"Simulação concluída (cenário: {args.cenario}).")
    print(f"Arquivo JSON: {args.saida_json}")
    print(f"Arquivo CSV: {args.saida_csv}")

    if args.gerar_grafico:
        try:
            motor = exportar_grafico(args.saida_grafico, estados)
            print(f"Arquivo gráfico: {args.saida_grafico} (gerado via {motor})")
        except RuntimeError as erro:
            print(f"Aviso: {erro}")

    for k, v in resumo.items():
        print(f"- {k}: {v:.4f}")


if __name__ == "__main__":
    main()
