# Simulador de Política Monetária

Projeto básico de **simulação de política monetária** com foco em todo o processo:

1. Definição de parâmetros macroeconômicos.
2. Simulação temporal com regra de Taylor.
3. Geração de trajetória por período.
4. Exportação de resultados em JSON e CSV.
5. Resumo com indicadores finais.

## Modelo usado (versão básica)

O simulador combina três blocos simplificados:

- **Regra de Taylor** para taxa de juros nominal.
- **Dinâmica de inflação** com inércia + hiato do produto.
- **Dinâmica do hiato do produto** reagindo ao nível de juros.

Isso permite testar cenários com diferentes metas, choques e sensibilidade da economia.

## Como executar

```bash
python run_simulador.py
```

### Exemplo com cenário customizado

```bash
python run_simulador.py \
  --periodos 36 \
  --inflacao-inicial 5.8 \
  --meta-inflacao 3.0 \
  --hiato-inicial -1.2 \
  --choque-inflacao 0.1 \
  --choque-hiato -0.05
```

## Saídas geradas

- `resultado_simulacao.json`: parâmetros, resumo e trajetória completa.
- `trajetoria_simulacao.csv`: série temporal por período.

## Testes

```bash
pytest -q
```
