from simulator import SimulacaoParametros, SimuladorPoliticaMonetaria, resumir_resultados


def test_simulacao_gera_periodos_esperados():
    parametros = SimulacaoParametros(periodos=12)
    simulador = SimuladorPoliticaMonetaria(parametros)

    estados = simulador.simular()

    assert len(estados) == 13
    assert estados[0].periodo == 0
    assert estados[-1].periodo == 12


def test_juros_reagem_mais_quando_inflacao_sobe():
    p = SimulacaoParametros(meta_inflacao=3.0)
    s = SimuladorPoliticaMonetaria(p)

    juros_baixa = s.calcular_juros(inflacao=3.0, hiato_produto=0.0)
    juros_alta = s.calcular_juros(inflacao=6.0, hiato_produto=0.0)

    assert juros_alta > juros_baixa


def test_resumo_conta_erro_final_meta():
    parametros = SimulacaoParametros(periodos=2)
    estados = SimuladorPoliticaMonetaria(parametros).simular()

    resumo = resumir_resultados(estados, meta_inflacao=parametros.meta_inflacao)

    assert "erro_final_meta" in resumo
