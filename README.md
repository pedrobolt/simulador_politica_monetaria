# Simulador de Política Monetária

Aplicação em **Streamlit** para simular cenários de política monetária com foco em:

- trajetória da inflação;
- resposta dos juros via regra inspirada em Taylor;
- evolução do hiato do produto;
- geração de **gráficos interativos** ao final da simulação.

## Como executar

```bash
pip install -r requirements.txt
streamlit run app.py
```

## O que o app entrega

- métricas finais da simulação;
- tabela com todos os períodos;
- exportação dos resultados em CSV;
- gráficos interativos com Plotly:
  - linhas para evolução temporal;
  - barras comparativas entre inflação e juros;
  - dispersão entre hiato, inflação e juros.

## Personalização

Pelo menu lateral você pode ajustar:

- taxa neutra;
- meta de inflação;
- inflação inicial;
- juros iniciais;
- hiato inicial;
- choques de demanda e oferta;
- pesos da regra monetária;
- persistência inflacionária;
- sensibilidade do hiato aos juros;
- número de períodos.
