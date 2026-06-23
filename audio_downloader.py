#!/usr/bin/env python3
"""
audio_downloader.py
Busca aleatoriamente um áudio em alta (TikTok/Reels) usando yt-dlp.
"""

import os
import random
import logging
from pathlib import Path
import yt_dlp

log = logging.getLogger(__name__)

_DIR = Path(__file__).parent
AUDIOS_DIR = _DIR / "audios"

# Garante que a pasta audios/ existe
os.makedirs(AUDIOS_DIR, exist_ok=True)

# Consultas de busca para variar os resultados
SEARCH_QUERIES = [
    "ytsearch50:tiktok viral audio shorts",
    "ytsearch50:trending reels audio short",
    "ytsearch50:aesthetic vlog no copyright music short",
    "ytsearch50:tiktok song 2024 viral"
]

def limpar_pasta_audios():
    """Remove qualquer arquivo .mp3 antigo da pasta audios/."""
    for f in os.listdir(AUDIOS_DIR):
        if f.lower().endswith(".mp3"):
            try:
                os.remove(AUDIOS_DIR / f)
                log.info(f"🗑️ Áudio antigo apagado: {f}")
            except Exception as e:
                log.warning(f"⚠️ Falha ao apagar {f}: {e}")

def baixar_audio_em_alta() -> str | None:
    """
    Limpa a pasta de áudios, busca um vídeo curto no YouTube, 
    baixa apenas o áudio convertido em MP3 e salva na pasta audios/.
    Retorna o nome do arquivo baixado ou None se falhar.
    """
    limpar_pasta_audios()
    
    query = random.choice(SEARCH_QUERIES)
    log.info(f"🔍 Buscando músicas em alta via yt-dlp... ({query})")

    # Primeiro, extraímos as informações dos 50 resultados sem baixar
    ydl_opts_extract = {
        'quiet': True,
        'extract_flat': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts_extract) as ydl:
            result = ydl.extract_info(query, download=False)
            
            if 'entries' not in result or not result['entries']:
                log.error("❌ Nenhum vídeo encontrado na busca.")
                return None
                
            # Filtra os vídeos para garantir que são curtos (menos de 3 minutos)
            videos = []
            for entry in result['entries']:
                duracao = entry.get('duration')
                # Algumas extrações flat não trazem duration, aceitamos as que trazem e são curtas
                # ou assumimos risco nas sem duration se a lista ficar vazia
                if duracao and duracao < 180:
                    videos.append(entry)
            
            if not videos:
                log.warning("⚠️ Nenhum vídeo com menos de 3 minutos encontrado com duração explícita, pegando os primeiros.")
                videos = list(result['entries'])[:10]
                
            random.shuffle(videos)
            
            # Tentar baixar até conseguir
            for video_escolhido in videos:
                video_url = video_escolhido.get('url') or video_escolhido.get('webpage_url')
                
                if not video_url.startswith("http"):
                    video_url = f"https://www.youtube.com/watch?v={video_url}"
                    
                log.info(f"🎯 Tentando baixar: {video_url} ({video_escolhido.get('title', 'Sem título')})")
                
                output_template = str(AUDIOS_DIR / "musica_%(id)s.%(ext)s")
                
                ydl_opts_download = {
                    'format': 'bestaudio/best',
                    'outtmpl': output_template,
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'quiet': True,
                    'no_warnings': True,
                    # Segurança adicional
                    'match_filter': yt_dlp.utils.match_filter_func("duration < 180"),
                }
                
                try:
                    with yt_dlp.YoutubeDL(ydl_opts_download) as ydl_dl:
                        ydl_dl.download([video_url])
                    
                    # Verifica se o arquivo foi criado
                    arquivos = [f for f in os.listdir(AUDIOS_DIR) if f.lower().endswith(".mp3")]
                    if arquivos:
                        log.info(f"✅ Áudio baixado com sucesso: {arquivos[0]}")
                        return arquivos[0]
                except Exception as e:
                    log.warning(f"⚠️ Falha no download deste vídeo: {e}. Tentando o próximo...")
                    continue
            
            log.error("❌ Todas as tentativas de download falharam.")
            return None

    except Exception as e:
        log.error(f"❌ Erro durante a busca ou download do áudio: {e}")
        return None

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    baixar_audio_em_alta()
