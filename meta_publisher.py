#!/usr/bin/env python3
"""
meta_publisher.py
Publica a imagem e o Reel na Página do Facebook via Meta Graph API.
"""

import os
import logging
import requests

log = logging.getLogger(__name__)

FB_GRAPH   = "https://graph.facebook.com/v22.0"
FB_TOKEN   = os.environ.get("FB_TOKEN", "")
FB_PAGE_ID = os.environ.get("FB_PAGE_ID", "")


def publicar_foto(img_bytes: bytes, legenda: str, hashtags: str) -> str | None:
    """
    Publica a imagem 4:5 diretamente na Página do Facebook.
    Retorna o ID do post publicado ou None em caso de erro.
    """
    if not FB_TOKEN or not FB_PAGE_ID:
        log.error("❌ FB_TOKEN ou FB_PAGE_ID não configurados.")
        return None

    mensagem = f"{legenda}\n.\n{hashtags}"

    try:
        r = requests.post(
            f"{FB_GRAPH}/{FB_PAGE_ID}/photos",
            files={"source": ("post.png", img_bytes, "image/png")},
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
            log.info(f"✅ Foto publicada no Facebook! ID: {post_id}")
            return post_id
        else:
            log.error(f"❌ Erro na publicação da foto: {resp}")
            return None

    except Exception as e:
        log.error(f"❌ Exceção ao publicar foto no Facebook: {e}")
        return None


def publicar_video(video_path: str, legenda: str, hashtags: str) -> str | None:
    """
    Publica o vídeo (Reel 9:16) diretamente na Página do Facebook.
    Retorna o ID do post publicado ou None em caso de erro.
    """
    if not FB_TOKEN or not FB_PAGE_ID:
        log.error("❌ FB_TOKEN ou FB_PAGE_ID não configurados para o vídeo.")
        return None

    mensagem = f"{legenda}\n.\n{hashtags}"

    try:
        with open(video_path, 'rb') as vf:
            r = requests.post(
                f"{FB_GRAPH}/{FB_PAGE_ID}/videos",
                files={"source": ("reel.mp4", vf, "video/mp4")},
                data={
                    "description": mensagem,
                    "access_token": FB_TOKEN,
                },
                timeout=180, # Upload de vídeo demora mais
            )
        resp = r.json()

        if "id" in resp:
            post_id = resp["id"]
            log.info(f"✅ Reel publicado no Facebook! ID: {post_id}")
            return post_id
        else:
            log.error(f"❌ Erro na publicação do vídeo: {resp}")
            return None

    except Exception as e:
        log.error(f"❌ Exceção ao publicar vídeo no Facebook: {e}")
        return None
