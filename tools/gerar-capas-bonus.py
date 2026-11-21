"""Gera as capas 3D dos 4 bônus na KIE (gpt-image-2-image-to-image), no estilo caderno do material PC-TO.
Referências: ref/bonus-0N.webp (composição do mockup), previa/001.png (identidade da capa) e uma página de mapa.
A chave vem da linha KIE= de chaves-api/.env (nunca impressa).
uso: python -I tools/gerar-capas-bonus.py [01 02 03 04]  ->  IMAGENS SITE/capas-ia/bonus-0N.png
"""
import base64
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import json
import time

import requests

ENV = Path(r"C:\Users\Rafael\Documents\CLAUDECODE\chaves-api\.env")
BASE = Path(__file__).resolve().parent.parent / "IMAGENS SITE"
REF = BASE / "ref"
OUT = BASE / "capas-ia"
OUT.mkdir(exist_ok=True)


API = "https://api.kie.ai"
UPLOAD = "https://kieai.redpandaai.co/api/file-stream-upload"
MODELO = "gpt-image-2-image-to-image"


def chave():
    for l in ENV.read_text(encoding="utf-8").splitlines():
        if l.startswith("KIE="):
            return l.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit("sem KIE no .env")


def h():
    return {"Authorization": f"Bearer {chave()}"}


def ok(r):
    j = r.json()
    if j.get("code") != 200:
        raise RuntimeError(f"kie code={j.get('code')}: {j.get('msg')}")
    return j["data"]


def sobe(arq, nome):
    with open(arq, "rb") as f:
        d = ok(requests.post(UPLOAD, headers=h(), timeout=120, files={"file": (nome, f)},
                             data={"uploadPath": "pcto-bonus", "fileName": nome}))
    return d.get("downloadUrl") or d.get("fileUrl")


BONUS = {
    "01": dict(titulo="SIMULADO DA APROVAÇÃO", sub="PROVA COMPLETA NO PADRÃO CEBRASPE",
               faixa="TEMPO • GABARITO • REVISÃO", mapa="012",
               desenho="a stopwatch, an answer sheet with filled bubbles, a pencil and a green check mark"),
    "02": dict(titulo="REDAÇÃO NOTA MÁXIMA", sub="ESTRUTURA E TEMAS PARA TREINAR",
               faixa="ESTRUTURA • CRITÉRIOS • TEMAS", mapa="002",
               desenho="an open notebook with a handwritten essay, a fountain pen and a correction checklist clipboard"),
    "03": dict(titulo="PEGADINHAS DO CEBRASPE", sub="COMO A BANCA MONTA A QUESTÃO QUE DERRUBA",
               faixa="TERMO • AUTORIDADE • EXCEÇÃO", mapa="022",
               desenho="a big magnifying glass over a printed exam question, a yellow warning triangle and a mouse trap"),
    "04": dict(titulo="ROTA DA APROVAÇÃO PC-TO", sub="DO PRÉ-EDITAL ATÉ A PROVA",
               faixa="SEMANA • REVISÃO • QUESTÕES", mapa="032",
               desenho="a weekly study planner calendar, a winding road with a finish flag, a clock and a yellow highlighter"),
}

PROMPT = """Create a product mockup image with EXACTLY the same composition, camera angle, lighting and layout as the FIRST image:
a 3D hardcover book standing upright with its spine visible on the left, and loose printed study pages fanned behind it,
on a fully transparent background with a soft contact shadow. Do not copy any text or drawing from the first image.

The book cover design must follow the visual identity of the SECOND image (the PC-TO study material cover):
white ruled notebook paper with a black spiral binding on the left edge, thick black brush-stroke banners with bold white
hand lettering, bright yellow highlighter strokes, and illustrations drawn in blue ballpoint pen sketch style.
The loose pages behind the book must look like the THIRD image (visual study map pages, notebook style, yellow highlights).

Cover text, in Brazilian Portuguese, spelled exactly like this and nothing else:
- top line, small: "MAPA DA APROVAÇÃO · PC-TO"
- small yellow tag: "BÔNUS {n}"
- big title on black brush banners: "{titulo}"
- subtitle highlighted in yellow: "{sub}"
- bottom black strip: "{faixa}"
- round yellow seal at bottom right: "BÔNUS EXCLUSIVO"
Spine text, vertical, black on yellow: "{titulo}"

Cover illustration, in blue ballpoint pen sketch: {desenho}, in front of a Tocantins landscape with cerrado trees.
All letters must be crisp, correctly spelled with accents, and fully readable. High quality, sharp, professional."""


def gera(n):
    b = BONUS[n]
    prompt = PROMPT.format(n=n, **b)
    try:
        urls = [sobe(REF / f"bonus-{n}.png", f"ref-{n}.png"),
                sobe(BASE / "previa" / "001.png", f"capa-{n}.png"),
                sobe(BASE / "previa" / f"{b['mapa']}.png", f"mapa-{n}.png")]
        task = ok(requests.post(f"{API}/api/v1/jobs/createTask", headers=h(), timeout=60, json={
            "model": MODELO, "input": {"prompt": prompt, "input_urls": urls, "aspect_ratio": "1:1",
                                       "resolution": "1K", "background": "transparent"}}))["taskId"]
        t0 = time.time()
        while time.time() - t0 < 900:
            d = ok(requests.get(f"{API}/api/v1/jobs/recordInfo", params={"taskId": task}, headers=h(), timeout=30))
            if d.get("state") == "success":
                url = json.loads(d["resultJson"])["resultUrls"][0]
                (OUT / f"bonus-{n}.png").write_bytes(requests.get(url, timeout=300).content)
                return f"{n}: ok ({d.get('creditsConsumed')} créditos)"
            if d.get("state") == "fail":
                return f"{n}: falhou {d.get('failCode')} {d.get('failMsg')}"
            time.sleep(6)
        return f"{n}: tempo esgotado ({task})"
    except Exception as e:
        return f"{n}: erro {e}"


if __name__ == "__main__":
    alvo = sys.argv[1:] or list(BONUS)
    with ThreadPoolExecutor(4) as ex:
        for res in ex.map(gera, alvo):
            print(res, flush=True)
