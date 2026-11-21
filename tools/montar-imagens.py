"""Monta todas as imagens da página PC-TO a partir da pasta "IMAGENS SITE" (mesmo molde da PCBA/PPPE).

Uso:
    python tools/montar-imagens.py

Origem (IMAGENS SITE):
  - previa/001.png ... 036.png      páginas do PDF "pcto-mostruario-35-mapas.pdf" (001 = capa)
                                    002-006 Português, 007-011 Informática, 012-016 Raciocínio Lógico,
                                    017-021 Direito Penal, 022-026 Processo Penal,
                                    027-031 Legislação Penal Especial, 032-036 Constitucional
  - capas-ia/bonus-01..04.png        capas 3D dos bônus (tools/gerar-capas-bonus.py); têm prioridade
  - bonus-01..04.* (opcional)       capas reais dos bônus; sem elas o script gera provisórias
  - texto-corrido-fato-tipico.webp  texto corrido do comparador (o mesmo da PCBA, tema Fato Típico)

Gera em assets/img (tudo WebP, cada arquivo abaixo de 600 KB):
  - capa.webp, mapa-002..017.webp (galeria; 002 e 005 ficam ao lado da capa no topo)
  - comparador-mapa.webp (Fato Típico), texto-corrido.webp
  - materia-01..16.webp (carrossel de matérias), bonus-01..04.webp
  - mockup-produto.webp (grade de mapas + capa no tablet + fileira de bônus, igual à PCBA)
  - og-image.jpg (compartilhamento 1200x630)

Para trocar uma imagem, mude o número da página nos dicionários abaixo e rode de novo.
"""
import io
import pathlib
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

RAIZ = pathlib.Path(__file__).resolve().parent.parent
ORIGEM = RAIZ / "IMAGENS SITE"
PREVIA = ORIGEM / "previa"
DESTINO = RAIZ / "assets" / "img"
FONTES = pathlib.Path(__file__).resolve().parent / "fonts"
LIMITE = 600 * 1024
DESTINO.mkdir(parents=True, exist_ok=True)

CAPA_PAGINA = 1

# Galeria (carrossel de prévias), mesma numeração da PCBA: mapa-002 e mapa-005 ficam ao lado da capa no topo.
GALERIA = {
    "mapa-002": 17,  # Direito Penal: legalidade e princípios
    "mapa-003": 23,  # Processo Penal: inquérito policial
    "mapa-004": 2,   # Português: interpretação e inferência
    "mapa-005": 31,  # Organização criminosa
    "mapa-006": 21,  # Fato típico e estrutura do crime
    "mapa-007": 12,  # Raciocínio Lógico: proposições e conectivos
    "mapa-008": 7,   # Informática: hardware e memória
    "mapa-009": 32,  # Constitucional: princípios fundamentais
    "mapa-010": 27,  # Abuso de autoridade: elemento subjetivo
    "mapa-011": 24,  # Notícia do crime e instauração
    "mapa-012": 13,  # Tabelas-verdade
    "mapa-013": 9,   # Windows: arquivos e pastas
    "mapa-014": 34,  # Direitos fundamentais
    "mapa-015": 19,  # Tempo e lugar do crime
    "mapa-016": 28,  # Abuso de autoridade: prisão e investigação
    "mapa-017": 5,   # Coesão e referenciação
}
COMPARADOR = 21  # Fato típico (casa com o texto corrido da PCBA)

# Carrossel de matérias: (página, legenda), na mesma ordem de SUBJECTS em assets/js/main.js.
MATERIAS = [
    (3, "Português"), (6, "Português"), (8, "Informática"), (10, "Informática"),
    (14, "Raciocínio Lógico"), (16, "Raciocínio Lógico"), (18, "Direito Penal"), (20, "Direito Penal"),
    (22, "Processo Penal"), (26, "Processo Penal"), (29, "Abuso de Autoridade"), (30, "Lei de Tortura"),
    (25, "Processo Penal"), (33, "Direito Constitucional"), (35, "Direito Constitucional"), (36, "Direito Constitucional"),
]

# Mockup: 14 mapas da grade (3 fileiras x 6 colunas, menos as 4 escondidas atrás da capa)
MOCKUP_GRADE = [6, 11, 16, 2, 22, 27, 32, 7, 12, 23, 30, 34, 24, 19]

BONUS = [
    ("BÔNUS 01", "SIMULADO DA", "APROVAÇÃO", "Questões no padrão Cebraspe", 18),
    ("BÔNUS 02", "REDAÇÃO", "NOTA MÁXIMA", "Estrutura e temas para treinar", 23),
    ("BÔNUS 03", "PEGADINHAS DO", "CEBRASPE", "Como a banca monta a questão que derruba", 21),
    ("BÔNUS 04", "ROTA DA", "APROVAÇÃO", "Do pré-edital até a prova", 27),
]

NAVY = (16, 32, 64)
YELLOW = (247, 196, 0)
BLACK = (22, 22, 22)
CREAM = (253, 250, 240)
WHITE = (255, 255, 255)


def fonte(nome, tamanho):
    return ImageFont.truetype(str(FONTES / f"Poppins-{nome}.ttf"), tamanho)


def salvar_webp(im, nome, qualidade=82):
    """Salva como WebP baixando a qualidade até ficar abaixo do limite."""
    while True:
        buf = io.BytesIO()
        im.save(buf, "WEBP", quality=qualidade, method=6)
        if buf.tell() <= LIMITE or qualidade <= 40:
            break
        qualidade -= 4
    (DESTINO / nome).write_bytes(buf.getvalue())
    print(f"{nome:24s} {im.size[0]}x{im.size[1]}  {buf.tell() // 1024:4d} KB  (q{qualidade})")


def pagina(n):
    for ext in ("jpeg", "jpg", "png", "webp"):
        p = PREVIA / f"{n:03d}.{ext}"
        if p.exists():
            return Image.open(p).convert("RGB")
    raise FileNotFoundError(f"página {n} não encontrada em {PREVIA}")


def capa():
    return pagina(CAPA_PAGINA)


def largura(im, w):
    """Reduz para a largura w (mantendo a proporção). Não amplia."""
    if im.width <= w:
        return im
    return im.resize((w, round(w * im.height / im.width)), Image.LANCZOS)


def achar(stem):
    for ext in (".webp", ".png", ".jpg", ".jpeg"):
        p = ORIGEM / f"{stem}{ext}"
        if p.exists():
            return p
    return None


# ---------------------------------------------------------------- texto corrido

TEXTO_TITULO = "Assistência ao Preso na Execução Penal"
TEXTO = [
    ("A assistência ao preso e ao internado", " constitui dever do Estado, que deve orientá-la com o objetivo de prevenir o crime e orientar o retorno à convivência em sociedade, nos termos do art. 10 da Lei de Execução Penal (Lei nº 7.210/1984). O parágrafo único do mesmo dispositivo estende essa assistência ao egresso, de modo que o dever estatal não se encerra com a saída do estabelecimento, prolongando-se pelo período em que a lei considera o indivíduo em fase de reintegração. Trata-se de projeção do princípio da humanidade das penas e do objetivo de integração social harmônica previsto no art. 1º da mesma lei, razão pela qual a assistência não se confunde com benefício ou favor da Administração."),
    ("As modalidades de assistência", " estão enumeradas no art. 11 da LEP: material, à saúde, jurídica, educacional, social e religiosa. A enumeração é relevante para fins de prova, uma vez que alternativas que suprimam alguma dessas espécies ou acrescentem modalidades inexistentes costumam ser apresentadas como corretas. Cada modalidade possui disciplina própria nos artigos subsequentes da lei, com destinatários, conteúdo e formas de prestação específicos, devendo ser interpretada à luz das regras mínimas para o tratamento de reclusos e dos tratados de direitos humanos de que o Brasil é signatário."),
    ("A assistência material,", " nos termos do art. 12, consistirá no fornecimento de alimentação, vestuário e instalações higiênicas. O art. 13 complementa a disciplina ao estabelecer que o estabelecimento disporá de instalações e serviços que atendam aos presos nas suas necessidades pessoais, além de locais destinados à venda de produtos e objetos permitidos e não fornecidos pela Administração. Observa-se, portanto, que a lei não se limita a garantir a subsistência mínima, mas impõe ao Estado o dever de estruturar o ambiente prisional de modo compatível com a dignidade da pessoa humana, admitindo, de forma subsidiária, a aquisição de itens não fornecidos diretamente."),
    ("A assistência à saúde", " do preso e do internado, de caráter preventivo e curativo, compreenderá atendimento médico, farmacêutico e odontológico, conforme o art. 14. A amplitude do dispositivo afasta a interpretação restritiva segundo a qual a assistência se limitaria à consulta médica, sendo frequente a cobrança da exclusão indevida do atendimento odontológico ou farmacêutico. O § 2º estabelece que, quando o estabelecimento penal não estiver aparelhado para prover a assistência médica necessária, esta será prestada em outro local, mediante autorização da direção do estabelecimento. A identificação da autoridade competente para essa autorização é ponto sensível, porquanto a troca da direção do estabelecimento pelo juiz da execução ou por outra autoridade é recurso recorrente das bancas examinadoras."),
    ("A proteção à gestante e à puérpera", " está no § 3º do art. 14, que assegura acompanhamento médico à mulher, principalmente no pré-natal e no pós-parto, extensivo ao recém-nascido. O § 4º, por sua vez, determina que será assegurado tratamento humanitário à mulher grávida durante os atos médico-hospitalares preparatórios para a realização do parto e durante o trabalho de parto, bem como à mulher no período de puerpério, cabendo ao poder público promover a assistência integral à sua saúde e à do recém-nascido. Tais disposições harmonizam-se com as Regras de Bangkok e com a vedação ao uso de algemas durante o parto."),
    ("Em conclusão,", " a assistência ao preso, ao internado e ao egresso integra o núcleo de direitos preservados durante a execução penal e expressa o compromisso do Estado com a finalidade ressocializadora da pena. O domínio das seis modalidades, do conteúdo da assistência material e à saúde e das autoridades competentes para cada providência é indispensável para a resolução das questões que exploram a literalidade dos arts. 10 a 14 da Lei de Execução Penal."),
]


def papel(w, h):
    rnd = random.Random(7)
    base = Image.new("L", (w // 4, h // 4))
    base.putdata([rnd.randint(0, 255) for _ in range((w // 4) * (h // 4))])
    ruido = base.resize((w, h), Image.BICUBIC).filter(ImageFilter.GaussianBlur(1.2))
    im = Image.new("RGB", (w, h), (236, 233, 226))
    escuro = Image.new("RGB", (w, h), (200, 196, 188))
    im = Image.composite(escuro, im, ruido.point(lambda v: int(v * 0.35)))
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rectangle([28, 28, w - 28, h - 28], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(40))
    borda = Image.new("RGB", (w, h), (186, 182, 174))
    return Image.composite(im, borda, mask)


def texto_corrido():
    w, h = 1054, 1492
    im = papel(w, h)
    d = ImageDraw.Draw(im)
    reg = ImageFont.truetype("times.ttf", 22)
    neg = ImageFont.truetype("timesbd.ttf", 22)
    tit = ImageFont.truetype("timesbd.ttf", 32)
    cor = (34, 32, 30)
    margem, larg, lh = 74, 1054 - 2 * 74, 28
    tw = d.textlength(TEXTO_TITULO, font=tit)
    d.text(((w - tw) / 2, 50), TEXTO_TITULO, font=tit, fill=cor)
    y = 112
    esp = d.textlength(" ", font=reg)
    for lead, corpo in TEXTO:
        palavras = [(p, neg) for p in lead.split()] + [(p, reg) for p in corpo.split()]
        linha, lw, linhas = [], 0, []
        for p, f in palavras:
            pw = d.textlength(p, font=f)
            if linha and lw + esp + pw > larg:
                linhas.append(linha)
                linha, lw = [], 0
            lw += (esp if linha else 0) + pw
            linha.append((p, f, pw))
        linhas.append(linha)
        for i, ln in enumerate(linhas):
            total = sum(pw for _, _, pw in ln)
            gap = (larg - total) / (len(ln) - 1) if i < len(linhas) - 1 and len(ln) > 1 else esp
            x = margem
            for p, f, pw in ln:
                d.text((x, y), p, font=f, fill=cor)
                x += pw + gap
            y += lh
        y += 14
    d.text((w / 2 - 5, h - 52), "1", font=reg, fill=cor)
    print(f"  texto corrido termina em y={y:.0f} de {h}")
    salvar_webp(largura(im, 960), "texto-corrido.webp", qualidade=80)


# ---------------------------------------------------------------- bônus provisórios


def centro(d, cx, y, texto, f, cor):
    d.text((cx - d.textlength(texto, font=f) / 2, y), texto, font=f, fill=cor)


def pilula(d, cx, y, partes, f, fundo=NAVY, padx=44, pady=18):
    total = sum(d.textlength(t, font=f) for t, _ in partes)
    asc, desc = f.getmetrics()
    alt = asc + desc + pady * 2
    x0 = cx - total / 2
    d.rounded_rectangle((x0 - padx, y, x0 + total + padx, y + alt), radius=alt // 2, fill=fundo)
    x = x0
    for t, c in partes:
        d.text((x, y + pady), t, font=f, fill=c)
        x += d.textlength(t, font=f)


def grifo(d, cx, y, texto, f):
    w = d.textlength(texto, font=f)
    l, t, r, b = d.textbbox((cx - w / 2, y), texto, font=f)
    d.rounded_rectangle((l - 22, t + (b - t) * 0.42, r + 22, b + 10), radius=12, fill=YELLOW)
    d.text((cx - w / 2, y), texto, font=f, fill=BLACK)


def bonus_provisorio(tag, l1, l2, sub, pag):
    W, H = 1055, 1491
    im = Image.new("RGBA", (W, H), CREAM + (255,))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W, H), outline=NAVY, width=14)
    pilula(d, W / 2, 60, [("MAPA DA APROVAÇÃO ", WHITE), ("PC-TO", YELLOW)], fonte("ExtraBold", 46))
    pilula(d, W / 2, 185, [(tag, NAVY)], fonte("ExtraBold", 40), fundo=YELLOW, padx=36, pady=10)
    centro(d, W / 2, 300, l1, fonte("ExtraBold", 92), BLACK)
    grifo(d, W / 2, 405, l2, fonte("ExtraBold", 108))
    colar_com_sombra(im, cartao(pagina(pag), 540, 765), W / 2, 520 + 400, angulo=-3, sombra=20)
    pilula(d, W / 2, H - 175, [(sub, YELLOW)], fonte("Bold", 44))
    return im.convert("RGB")


# ---------------------------------------------------------------- mockup (igual PCBA/PMPE)


def cartao(im, w, h, raio=6):
    """Redimensiona a página e arredonda os cantos."""
    c = im.resize((w, h), Image.LANCZOS).convert("RGBA")
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], raio, fill=255)
    c.putalpha(m)
    return c


def colar_com_sombra(tela, peca, cx, cy, angulo=0.0, sombra=26, opac=230):
    if angulo:
        peca = peca.rotate(angulo, resample=Image.BICUBIC, expand=True)
    pad = sombra * 3
    sh = Image.new("RGBA", (peca.width + 2 * pad, peca.height + 2 * pad), (0, 0, 0, 0))
    alfa = peca.getchannel("A").point(lambda v: v * opac // 255)
    sh.paste(Image.new("RGBA", peca.size, (2, 8, 20, 255)), (pad, pad + sombra // 3), alfa)
    sh = sh.filter(ImageFilter.GaussianBlur(sombra))
    x, y = round(cx - peca.width / 2), round(cy - peca.height / 2)
    camada = Image.new("RGBA", tela.size, (0, 0, 0, 0))
    camada.paste(sh, (x - pad, y - pad))
    camada.paste(peca, (x, y), peca)
    tela.alpha_composite(camada)


def livro(im, w, h, lombada=14, raio=8):
    """Página com lombada azul-marinho à esquerda, como as apostilas do mockup da PCBA."""
    t = Image.new("RGBA", (w + lombada, h), (0, 0, 0, 0))
    ImageDraw.Draw(t).rounded_rectangle([0, 0, w + lombada - 1, h - 1], raio, fill=(14, 51, 89, 255))
    t.alpha_composite(cartao(im, w, h, raio=4), (lombada, 0))
    return t


def tablet(img, w_int, borda=24, raio=34):
    h_int = round(w_int * img.height / img.width)
    W, H = w_int + 2 * borda, h_int + 2 * borda
    t = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(t).rounded_rectangle([0, 0, W - 1, H - 1], raio, fill=(14, 51, 89, 255))
    t.alpha_composite(cartao(img, w_int, h_int, raio=10), (borda, borda))
    return t


def mockup(bonus_imgs):
    W, H = 1946, 2003
    tela = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cw, ch = 279, 395
    xs = [49 + round(k * 314.2) for k in range(6)]
    ys = [117, 551, 985]
    fila = iter(MOCKUP_GRADE)
    for r, y in enumerate(ys):
        for c, x in enumerate(xs):
            if r < 2 and c in (2, 3):
                continue  # atrás da capa
            colar_com_sombra(tela, livro(pagina(next(fila)), cw - 12, ch), x + cw / 2, y + ch / 2, sombra=22)
    colar_com_sombra(tela, tablet(capa(), 620), 948, 560, angulo=-4.5, sombra=34, opac=255)
    bw, bh = 340, 480
    for k, ((cx, cy, ang), im) in enumerate(zip([(395, 1612, 2.5), (772, 1655, -2.0), (1150, 1640, 1.5), (1524, 1618, -3.0)], bonus_imgs)):
        if im.mode == "RGBA":  # capa 3D gerada por IA (tools/gerar-capas-bonus.py): já vem com volume e fundo transparente
            colar_com_sombra(tela, largura(im, 468), 250 + k * 482, 1660, sombra=14, opac=120)
        else:
            colar_com_sombra(tela, livro(im, bw, bh, lombada=16), cx, cy, angulo=ang, sombra=26)
    x0, y0, x1, y1 = tela.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
    tela = tela.crop((0, 0, W, min(H, y1 + 24)))
    W, H = tela.size
    tela = tela.resize((1120, round(1120 * H / W)), Image.LANCZOS)
    salvar_webp(tela, "mockup-produto.webp", qualidade=84)


# ---------------------------------------------------------------- og-image


def og_image():
    W, H = 1200, 630
    topo, base = (7, 29, 50), (14, 50, 87)
    im = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(im)
    for y in range(H):
        t = y / (H - 1)
        d.line([(0, y), (W, y)], fill=tuple(round(a + (b - a) * t) for a, b in zip(topo, base)))
    im = im.convert("RGBA")
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([60, 70, 372, 120], 25, fill=(255, 255, 255))
    d.ellipse([82, 88, 96, 102], fill=(34, 157, 94))
    d.text((106, 95), "Mapa da Aprovação", font=fonte("SemiBold", 21), fill=(7, 29, 49), anchor="lm")
    d.text((56, 222), "PC-TO 2026", font=fonte("ExtraBold", 84), fill=(255, 255, 255), anchor="ls")
    d.text((60, 300), "Oficial Investigador de Polícia", font=fonte("Bold", 36), fill=(230, 186, 77), anchor="ls")
    d.text((60, 380), "290 mapas visuais · comece antes do edital", font=fonte("Regular", 29), fill=(226, 232, 240), anchor="ls")
    d.text((60, 425), "323 vagas · R$ 7.917 · Cebraspe", font=fonte("Regular", 29), fill=(226, 232, 240), anchor="ls")
    d.rounded_rectangle([60, 480, 560, 556], 38, fill=(31, 167, 91))
    d.text((310, 518), "Edital no início de dezembro", font=fonte("Bold", 28), fill=(255, 255, 255), anchor="mm")
    colar_com_sombra(im, cartao(pagina(COMPARADOR), 330, 467), 945, 300, angulo=8, sombra=16)
    colar_com_sombra(im, tablet(capa(), 316, borda=12, raio=18), 978, 362, angulo=-2.5, sombra=18, opac=255)
    out = im.convert("RGB")
    out.save(DESTINO / "og-image.jpg", quality=88, optimize=True, progressive=True)
    print(f"og-image.jpg              1200x630  {(DESTINO / 'og-image.jpg').stat().st_size // 1024:4d} KB")


# Larguras de saída: o dobro (ou um pouco mais) do tamanho em que cada imagem aparece na tela.
# Capa: 140px na página. Mapas do carrossel e do topo: ~184px. Comparador: até 480px. Mockup: até 560px.
def main():
    salvar_webp(largura(capa(), 420), "capa.webp", qualidade=80)
    for nome, pag in GALERIA.items():
        salvar_webp(largura(pagina(pag), 400), f"{nome}.webp", qualidade=78)
    salvar_webp(largura(pagina(COMPARADOR), 960), "comparador-mapa.webp", qualidade=80)
    for i, (pag, _) in enumerate(MATERIAS, 1):
        salvar_webp(largura(pagina(pag), 440), f"materia-{i:02d}.webp", qualidade=78)
    bonus_imgs = []
    for i, (tag, l1, l2, sub, pag) in enumerate(BONUS, 1):
        ia = ORIGEM / "capas-ia" / f"bonus-{i:02d}.png"
        own = achar(f"bonus-{i:02d}")
        if ia.exists():  # mockup 3D do bônus (tools/gerar-capas-bonus.py), recortado nas bordas transparentes
            im = Image.open(ia).convert("RGBA")
            im = im.crop(im.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox())
        else:
            im = Image.open(own).convert("RGB") if own else bonus_provisorio(tag, l1, l2, sub, pag)
        bonus_imgs.append(im)
        salvar_webp(largura(im, 700), f"bonus-{i:02d}.webp", qualidade=78)
    salvar_webp(Image.open(ORIGEM / "texto-corrido-fato-tipico.webp").convert("RGB"), "texto-corrido.webp", qualidade=80)
    mockup(bonus_imgs)
    og_image()


if __name__ == "__main__":
    main()
