# Simulador de Política Monetária

Simulador **básico, mas completo**, para testar decisões de política monetária ao longo do tempo.

## O que este projeto entrega

1. Configuração de parâmetros econômicos (meta, inflação inicial, hiato, choques).
2. Simulação temporal com regra de Taylor e dinâmica simplificada de inflação/atividade.
3. Cenários pré-definidos (`base`, `hawkish`, `dovish`, `choque_oferta`).
4. Exportação de resultados em JSON e CSV.
5. Geração opcional de gráfico PNG com as séries simuladas.
6. Resumo estatístico da trajetória (médias, mínimos, máximos e erro final da meta).

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


### 4) Gerar gráfico automaticamente

```bash
python run_simulador.py --gerar-grafico
```

Também é possível escolher o nome/arquivo:

```bash
python run_simulador.py --gerar-grafico --saida-grafico meu_grafico.svg
```

## Saídas

> Dica: o formato SVG funciona sem instalar bibliotecas extras.

- `resultado_simulacao.json`: cenário, parâmetros, resumo e trajetória.
- `trajetoria_simulacao.csv`: série por período.
- `grafico_simulacao.svg`: gráfico com inflação, juros e hiato (quando `--gerar-grafico` é usado).

## Qualidade e validações

- Validação de parâmetros (ex.: períodos > 0, coeficientes em faixa válida).
- Testes automatizados cobrindo regras de negócio e cenários.

## Testes

```bash
pytest -q
```
