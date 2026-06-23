#!/usr/bin/env python3
"""
audio_downloader.py
Busca dinamicamente as músicas do Top 50 Spotify Brasil no Kworb, 
escolhe uma aleatoriamente e faz o download exato do áudio via YouTube (yt-dlp).
"""

import os
import random
import logging
import requests
import re
from pathlib import Path
import yt_dlp

log = logging.getLogger(__name__)

_DIR = Path(__file__).parent
AUDIOS_DIR = _DIR / "audios"

os.makedirs(AUDIOS_DIR, exist_ok=True)

def limpar_pasta_audios():
    """Remove qualquer arquivo .mp3 antigo da pasta audios/."""
    for f in os.listdir(AUDIOS_DIR):
        if f.lower().endswith(".mp3"):
            try:
                os.remove(AUDIOS_DIR / f)
                log.info(f"🗑️ Áudio antigo apagado: {f}")
            except Exception as e:
                log.warning(f"⚠️ Falha ao apagar {f}: {e}")

def obter_musicas_em_alta_spotify() -> list:
    """Acessa o ranking diário do Spotify Brasil e retorna uma lista de 'Artista - Música'."""
    url = "https://kworb.net/spotify/country/br_daily.html"
    log.info(f"🌐 Lendo o Top 200 do Spotify Brasil em: {url}")
    try:
        r = requests.get(url, timeout=10)
        # Extrai os nomes usando regex na tabela do Kworb
        matches = re.findall(r'<td class="text[^>]*><div><a href="[^"]+">([^<]+)</a> - <a href="[^"]+">([^<]+)</a>', r.text)
        
        musicas = []
        # Pega as top 50
        for artist, title in matches[:50]:
            # Evita nomes com aspas duplas que quebram a busca no shell
            artista_limpo = artist.replace('"', '').strip()
            titulo_limpo = title.replace('"', '').strip()
            musicas.append(f"{artista_limpo} - {titulo_limpo}")
            
        log.info(f"✅ Sucesso: Encontradas {len(musicas)} músicas no Top 50 do Spotify!")
        return musicas
    except Exception as e:
        log.error(f"❌ Erro ao acessar o ranking do Spotify: {e}")
        return []

def baixar_audio_em_alta() -> str | None:
    """
    Limpa a pasta de áudios, escolhe uma música do Top Spotify Brasil, 
    busca ativamente no YouTube e baixa o MP3.
    """
    limpar_pasta_audios()
    
    musicas_top_50 = obter_musicas_em_alta_spotify()
    
    if not musicas_top_50:
        log.error("❌ Não foi possível buscar o ranking. Fallback desativado.")
        return None
        
    random.shuffle(musicas_top_50)
    
    for musica_escolhida in musicas_top_50:
        # Trocando ytsearch1 por scsearch1 (SoundCloud)
        # O YouTube está bloqueando IPs do GitHub Actions ativamente. O SoundCloud não possui essa restrição pesada,
        # além de ser extremamente mais rápido e focado em áudio, retornando faixas de alta qualidade que servem perfeitamente pro Reel.
        query = f"scsearch1:{musica_escolhida}"
        log.info(f"🎯 Tentando baixar a música selecionada via SoundCloud: '{musica_escolhida}'")
        
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
            # 'match_filter': yt_dlp.utils.match_filter_func("duration < 300"), # até 5 minutos (nem precisa no SC mas vamos manter por segurança se a api suportar)
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts_download) as ydl_dl:
                ydl_dl.download([query])
            
            arquivos = [f for f in os.listdir(AUDIOS_DIR) if f.lower().endswith(".mp3")]
            if arquivos:
                log.info(f"✅ Áudio baixado com sucesso: {arquivos[0]}")
                return arquivos[0]
        except Exception as e:
            log.warning(f"⚠️ Falha no download desta música: {e}. Tentando a próxima...")
            continue
            
    log.error("❌ Todas as tentativas de download falharam.")
    return None

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    baixar_audio_em_alta()
