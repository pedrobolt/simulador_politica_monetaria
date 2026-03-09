from argparse import Namespace
from pathlib import Path

import pytest

from run_simulador import CENARIOS, build_parser, exportar_grafico, montar_parametros
from simulator import SimulacaoParametros, SimuladorPoliticaMonetaria, resumir_resultados


def test_simulacao_gera_periodos_esperados():
    estados = SimuladorPoliticaMonetaria(SimulacaoParametros(periodos=12)).simular()
    assert len(estados) == 13
    assert estados[0].periodo == 0
    assert estados[-1].periodo == 12


def test_juros_reagem_mais_quando_inflacao_sobe():
    s = SimuladorPoliticaMonetaria(SimulacaoParametros(meta_inflacao=3.0))
    assert s.calcular_juros(inflacao=6.0, hiato_produto=0.0) > s.calcular_juros(inflacao=3.0, hiato_produto=0.0)


def test_limite_inferior_juros_e_respeitado():
    p = SimulacaoParametros(meta_inflacao=3.0, limite_inferior_juros=2.0, alfa_taylor=0.0, beta_taylor=0.0, juros_neutro=0.0)
    s = SimuladorPoliticaMonetaria(p)
    assert s.calcular_juros(inflacao=0.0, hiato_produto=-10.0) == 2.0


def test_parametros_invalidos_disparam_erro():
    with pytest.raises(ValueError):
        SimulacaoParametros(periodos=0).validar()


@pytest.mark.parametrize("cenario", sorted(CENARIOS.keys()))
def test_montar_parametros_com_cenario(cenario):
    args = Namespace(
        cenario=cenario,
        periodos=10,
        inflacao_inicial=4.0,
        meta_inflacao=3.0,
        hiato_inicial=-0.2,
        juros_neutro=4.0,
        alfa_taylor=None,
        beta_taylor=None,
        inercia_inflacao=0.6,
        sensibilidade_hiato_juros=0.2,
        sensibilidade_inflacao_hiato=0.3,
        persistencia_hiato=0.6,
        limite_inferior_juros=0.0,
        choque_inflacao=None,
        choque_hiato=None,
    )

    parametros = montar_parametros(args)
    assert parametros.periodos == 10


def test_resumo_conta_erro_final_meta():
    parametros = SimulacaoParametros(periodos=2)
    estados = SimuladorPoliticaMonetaria(parametros).simular()
    resumo = resumir_resultados(estados, meta_inflacao=parametros.meta_inflacao)
    assert "erro_final_meta" in resumo
    assert "inflacao_min" in resumo


def test_readme_menciona_cenarios():
    readme = Path("README.md").read_text(encoding="utf-8")
    assert "cenário" in readme.lower()


def test_parser_possui_opcoes_de_grafico():
    parser = build_parser()
    args = parser.parse_args([])
    assert hasattr(args, "gerar_grafico")
    assert str(args.saida_grafico).endswith("grafico_simulacao.svg")


def test_exportar_grafico_gera_svg_sem_dependencias(tmp_path):
    estados = SimuladorPoliticaMonetaria(SimulacaoParametros(periodos=3)).simular()
    arquivo = tmp_path / "grafico.svg"
    motor = exportar_grafico(arquivo, estados)
    assert motor == "svg"
    assert arquivo.exists()
    assert "<svg" in arquivo.read_text(encoding="utf-8")


def test_exportar_grafico_png_sem_matplotlib_falha_de_forma_clara(tmp_path, monkeypatch):
    import builtins

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name.startswith("matplotlib"):
            raise ImportError("sem matplotlib")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    estados = SimuladorPoliticaMonetaria(SimulacaoParametros(periodos=2)).simular()

    with pytest.raises(RuntimeError):
        exportar_grafico(tmp_path / "grafico.png", estados)
