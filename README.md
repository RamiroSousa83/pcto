# Mapa da Aprovação PC-TO · Oficial Investigador

Página de vendas estática (HTML + CSS + JS puro, sem build), no mesmo molde da PPPE e da PC-BA.
Ângulo: **pré-edital** (comece antes do edital sair).

## Endereço (sugerido)

https://pcto.aprovadobizurado.com.br (subdomínio próprio, projeto separado na Vercel, caminhos na raiz).

## Rodar localmente

```
python -m http.server 8851
```

Abra http://localhost:8851/

## Dados usados na página (notícias de 16 e 17/11/2026)

- Contrato com o Cebraspe publicado no DOE-TO nº 7.183, de 16/11/2026 (contrato 2555/2026).
- Governador anunciou o edital para "até 18 dias", o que dá 04/12/2026. A Secom falou em 30 dias.
- 452 vagas: 323 Oficial Investigador, 69 Delegado, 60 Perito.
- Oficial Investigador: R$ 7.917,97, nível superior em qualquer área, CNH citada (categoria a confirmar).
  Carreira criada pela Lei Estadual 4.653/2025 (junta investigador e escrivão).
- Etapas previstas para Investigador: objetiva de 80 questões + redação, médico, psicológico, TAF,
  investigação social e curso de formação.
- Último concurso: 2014.

A contagem regressiva (`data-dias-edital`) vai até 04/12/2026 e está no fim de `assets/js/main.js`.
Quando o edital sair, troque o ângulo pré-edital pelo de data de prova (como na PPPE).

## Pendências antes de publicar

- Checkout: o botão `#checkout-btn` está com `href="#"`. Colar o link da Greenn do produto PC-TO.
- Rastreamento: colar as tags Raads Hub e Trackzeira do projeto PC-TO no `<head>` (marcado com comentário).
- Imagens: TODAS em `assets/img` são da PPPE (provisórias). Trocar capa, mockup, mapas da galeria,
  carrossel, comparador, bônus e og-image pelas do material PC-TO.
- Preço (R$ 47 / de R$ 150) e bônus copiados da PPPE: confirmar.
