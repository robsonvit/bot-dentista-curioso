#!/usr/bin/env python3
"""
image_renderer.py
Lida com a renderização visual do HTML para Imagem (4:5) e gravação de Vídeo (9:16).
"""

import os
import json
import logging
from pathlib import Path
from playwright.sync_api import sync_playwright

log = logging.getLogger(__name__)

_DIR      = Path(__file__).parent
HTML_FILE = _DIR / "render_post.html"
VIDEOS_DIR = _DIR / "temp_videos"

os.makedirs(VIDEOS_DIR, exist_ok=True)

def _preparar_html(conteudo: dict) -> str:
    if not HTML_FILE.exists():
        raise FileNotFoundError(f"Template HTML não encontrado: {HTML_FILE}")

    html_content = HTML_FILE.read_text(encoding="utf-8")
    dados_js     = json.dumps(conteudo, ensure_ascii=False)
    inject       = f"<script>window.POST_DATA = {dados_js};</script>"
    return html_content.replace("</head>", f"{inject}\n</head>")

def renderizar_imagem_45(conteudo: dict) -> bytes | None:
    """
    Renderiza o post como imagem 1080x1350 (4:5) para o feed do Instagram/FB.
    """
    tipo = conteudo.get("type", "tecnico")
    
    try:
        html_content = _preparar_html(conteudo)
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-gpu"])
            page = browser.new_page(viewport={"width": 1080, "height": 1350})

            log.info(f"🎨 Renderizando Imagem 4:5 ({tipo})...")
            page.set_content(html_content, wait_until="networkidle", timeout=30000)

            # Aguardar fontes e finalização das animações CSS (demoram ~1.2s)
            page.evaluate("document.fonts.ready")
            page.wait_for_timeout(2500)

            el = page.locator("#post-canvas")
            el.wait_for(state="visible", timeout=10000)
            img_bytes = el.screenshot(type="png")

            log.info(f"✅ Imagem 4:5 capturada: {len(img_bytes) // 1024}KB")
            browser.close()
            return img_bytes

    except Exception as e:
        log.error(f"❌ Erro ao renderizar imagem 4:5: {e}")
        return None

def gravar_video_916(conteudo: dict) -> str | None:
    """
    Renderiza o post em 1080x1920 (9:16) gravando um vídeo (.webm) da animação.
    Retorna o caminho absoluto do arquivo webm gerado.
    """
    tipo = conteudo.get("type", "tecnico")
    
    try:
        html_content = _preparar_html(conteudo)
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-gpu"])
            
            # Contexto configurado para gravar vídeo
            context = browser.new_context(
                viewport={"width": 1080, "height": 1920},
                record_video_dir=str(VIDEOS_DIR),
                record_video_size={"width": 1080, "height": 1920}
            )
            
            page = context.new_page()

            log.info(f"🎥 Gravando Vídeo Animado 9:16 ({tipo})...")
            
            # O vídeo começa a gravar. Setamos o conteúdo e a animação dispara.
            page.set_content(html_content, wait_until="networkidle", timeout=30000)
            page.evaluate("document.fonts.ready")
            
            # Tempo de duração do Reel (15 segundos para dar tempo à música)
            page.wait_for_timeout(15000)

            # Para fechar e salvar o arquivo de vídeo corretamente, fechamos context
            video_path = page.video.path()
            context.close()
            browser.close()
            
            log.info(f"✅ Vídeo .webm gravado em: {video_path}")
            return video_path

    except Exception as e:
        log.error(f"❌ Erro ao gravar vídeo 9:16: {e}")
        return None
