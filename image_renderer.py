#!/usr/bin/env python3
"""
image_renderer.py
Abre o render_post.html com Playwright (set_content),
injeta window.POST_DATA com o conteúdo gerado pelo Gemini,
captura screenshot 1080x1080 e retorna os bytes PNG.
"""

import json
import logging
from pathlib import Path
from playwright.sync_api import sync_playwright

log = logging.getLogger(__name__)

_DIR      = Path(__file__).parent
HTML_FILE = _DIR / "render_post.html"


def renderizar_post(conteudo: dict) -> bytes | None:
    """
    Renderiza o post como imagem 1080x1080 usando o template HTML local.
    Retorna bytes PNG ou None em caso de erro.
    """
    if not HTML_FILE.exists():
        log.error(f"❌ Template HTML não encontrado: {HTML_FILE}")
        return None

    tipo = conteudo.get("type", "tecnico")

    # Lê o HTML e embute os dados antes de fazer set_content
    # Isso garante que window.POST_DATA existe quando o script do HTML rodar
    html_content = HTML_FILE.read_text(encoding="utf-8")
    dados_js     = json.dumps(conteudo, ensure_ascii=False)
    inject       = f"<script>window.POST_DATA = {dados_js};</script>"
    html_content = html_content.replace("</head>", f"{inject}\n</head>")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-gpu"],
            )
            page = browser.new_page(viewport={"width": 1080, "height": 1080})

            log.info(f"🎨 Renderizando template ({tipo})...")
            page.set_content(html_content, wait_until="networkidle", timeout=30000)

            # Aguardar fontes (Google Fonts via CSS @import) carregarem
            page.evaluate("document.fonts.ready")
            page.wait_for_timeout(2000)

            # Screenshot do #post-canvas 1080x1080
            el = page.locator("#post-canvas")
            el.wait_for(state="visible", timeout=10000)
            img_bytes = el.screenshot(type="png")

            log.info(f"✅ Screenshot {len(img_bytes) // 1024}KB ({tipo})")
            browser.close()
            return img_bytes

    except Exception as e:
        log.error(f"❌ Erro ao renderizar post: {e}")
        return None
