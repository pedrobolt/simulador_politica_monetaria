# Simulador de Política Monetária

Simulador **básico, mas completo**, para testar decisões de política monetária ao longo do tempo.

## O que este projeto entrega

1. Configuração de parâmetros econômicos (meta, inflação inicial, hiato, choques e juros inicial opcional).
2. Simulação temporal com regra de Taylor e dinâmica simplificada de inflação/atividade.
3. Cenários pré-definidos (`base`, `hawkish`, `dovish`, `choque_oferta`).
4. Exportação de resultados em JSON e CSV.
5. Geração automática de gráfico das séries simuladas (SVG por padrão).
6. Resumo estatístico da trajetória (médias, mínimos, máximos e erro final da meta).
7. Controles de estabilidade numérica com limites configuráveis de inflação e hiato.

## Estrutura do modelo

- **Taxa de juros:** regra de Taylor com **limite inferior de juros**.
- **Inflação:** inércia + convergência à meta + efeito do hiato + choque.
- **Hiato do produto:** persistência + reação ao juro real simplificado + choque.

> Objetivo: permitir análise de cenário e sensibilidade de forma transparente.

## Como executar

```bash
python run_simulador.py
```

## Exemplos

### 1) Cenário base

```bash
python run_simulador.py --cenario base
```

### 2) Cenário contracionista (hawkish)

```bash
python run_simulador.py --cenario hawkish --periodos 36
```

### 3) Cenário customizado (sobrescrevendo parâmetros)

```bash
python run_simulador.py \
  --cenario choque_oferta \
  --periodos 30 \
  --meta-inflacao 3.0 \
  --inflacao-inicial 6.2 \
  --alfa-taylor 2.2 \
  --limite-inferior-juros 1.5
```


Também é possível definir a projeção inicial da Selic/juros do período 0:

```bash
python run_simulador.py --inflacao-inicial 5.8 --juros-inicial 12.25
```

### 4) Gráfico (automático por padrão)

```bash
python run_simulador.py
```

Escolher nome/arquivo do gráfico:

```bash
python run_simulador.py --saida-grafico meu_grafico.svg
```



Para cenários extremos, você pode ajustar os limites de estabilização e inspecionar cada período:

```bash
python run_simulador.py --inflacao-max 15 --hiato-min -3 --hiato-max 3 --debug
```

Desativar geração de gráfico:

```bash
python run_simulador.py --sem-grafico
```

## Saídas

> Dica: o formato SVG funciona sem instalar bibliotecas extras.

- `resultado_simulacao.json`: cenário, parâmetros, resumo e trajetória.
- `trajetoria_simulacao.csv`: série por período.
- `grafico_simulacao.svg`: gráfico com inflação, juros e hiato (gerado por padrão).

## Qualidade e validações

- Validação de parâmetros (ex.: períodos > 0, coeficientes em faixa válida).
- Testes automatizados cobrindo regras de negócio e cenários.

## Testes

```bash
pytest -q
```
