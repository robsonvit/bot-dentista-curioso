#!/usr/bin/env python3
"""
meta_publisher.py
Publica a imagem na Página do Facebook via Meta Graph API.
"""

import os
import logging
import requests

log = logging.getLogger(__name__)

FB_GRAPH   = "https://graph.facebook.com/v22.0"
FB_TOKEN   = os.environ.get("FB_TOKEN", "")
FB_PAGE_ID = os.environ.get("FB_PAGE_ID", "")


def publicar_no_meta(img_bytes: bytes, legenda: str, hashtags: str) -> str | None:
    """
    Publica a imagem diretamente na Página do Facebook.
    Retorna o ID do post publicado ou None em caso de erro.
    """
    if not FB_TOKEN or not FB_PAGE_ID:
        log.error("❌ FB_TOKEN ou FB_PAGE_ID não configurados.")
        return None

    mensagem = f"{legenda}\n.\n{hashtags}"

    try:
        r = requests.post(
            f"{FB_GRAPH}/{FB_PAGE_ID}/photos",
            files={"source": ("post.jpg", img_bytes, "image/jpeg")},
            data={
                "message": mensagem,
                "access_token": FB_TOKEN,
                "published": "true",
            },
            timeout=60,
        )
        resp = r.json()

        if "id" in resp:
            post_id = resp["id"]
            log.info(f"✅ Publicado no Facebook! ID: {post_id}")
            return post_id
        else:
            log.error(f"❌ Erro na publicação: {resp}")
            return None

    except Exception as e:
        log.error(f"❌ Exceção ao publicar no Facebook: {e}")
        return None
