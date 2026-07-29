"""Conversão de HTML das seções da carta para texto plano legível em planilha."""
from __future__ import annotations

import re
from html import unescape
from html.parser import HTMLParser

# Limite de célula do Excel é 32.767 — margem de segurança.
MAX_CELULA = 32_000

_QUEBRA = {"p", "br", "div", "li", "tr", "h1", "h2", "h3", "h4", "h5", "h6"}
_ESPACOS = re.compile(r"[ \t]+")
_LINHAS = re.compile(r"\n{3,}")


class _Extrator(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)  # já resolve &eacute; etc.
        self.partes: list[str] = []

    def handle_data(self, data: str) -> None:
        self.partes.append(data)

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag in _QUEBRA:
            self.partes.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in _QUEBRA:
            self.partes.append("\n")


def to_text(html: str | None) -> str:
    """HTML da seção -> texto plano, sem tags nem entidades, espaços colapsados."""
    if not html:
        return ""
    p = _Extrator()
    p.feed(html)
    p.close()
    # 2ª passada: parte do conteúdo está duplo-codificada no banco (`&amp;amp;`),
    # o parser resolve só um nível e sobraria `&amp;` visível na planilha.
    texto = _ESPACOS.sub(" ", unescape("".join(p.partes)))
    # strip por linha antes de colapsar: linhas só com espaço viram vazias e
    # aí sim contam como quebra excedente.
    texto = "\n".join(linha.strip() for linha in texto.split("\n"))
    return _LINHAS.sub("\n\n", texto).strip()[:MAX_CELULA]


def demo() -> None:
    assert to_text("") == ""
    assert to_text(None) == ""
    assert to_text("<p>A Ouvidoria &eacute; o canal</p>") == "A Ouvidoria é o canal"
    assert to_text("<p>um</p><p>dois</p>") == "um\n\ndois"
    assert to_text("<ul><li>a</li><li>b</li></ul>") == "a\n\nb"
    assert to_text("texto   com     espaços") == "texto com espaços"
    assert to_text('<a href="http://x">link</a> aqui') == "link aqui"
    # linhas só com espaço não podem virar quebras extras
    assert to_text("<p>a</p><p> </p><p> </p><p>b</p>") == "a\n\nb"
    # duplo-codificado no banco
    assert to_text("<p>Lei &amp;amp; Ordem</p>") == "Lei & Ordem"
    assert to_text("<p>diz &amp;quot;oi&amp;quot;</p>") == 'diz "oi"'
    # e-mail entre sinais de menor/maior não é tag — precisa sobreviver
    assert to_text("<p>envie para &lt;a@b.gov.br&gt;</p>") == "envie para <a@b.gov.br>"
    assert len(to_text("<p>" + "x" * 40_000 + "</p>")) == MAX_CELULA
    print("[ok] html_text")


if __name__ == "__main__":
    demo()
