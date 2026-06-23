import os
import random
import logging
import subprocess
from pathlib import Path

log = logging.getLogger(__name__)

_DIR = Path(__file__).parent
AUDIOS_DIR = _DIR / "audios"

def processar_video_final(webm_path: str, output_path: str) -> str | None:
    """
    Converte um .webm gerado pelo Playwright para .mp4 (codec h264 padrão web).
    Se houver arquivos .mp3 na pasta 'audios', seleciona um aleatoriamente
    e embute no vídeo.
    Retorna o caminho do vídeo .mp4 gerado.
    """
    try:
        # 1. Encontrar áudios disponíveis
        arquivos_audio = []
        if AUDIOS_DIR.exists():
            arquivos_audio = [f for f in os.listdir(AUDIOS_DIR) if f.lower().endswith(".mp3")]
            
        audio_path = None
        if arquivos_audio:
            audio_escolhido = random.choice(arquivos_audio)
            audio_path = str(AUDIOS_DIR / audio_escolhido)
            log.info(f"🎵 Áudio selecionado: {audio_escolhido}")
        else:
            log.warning("⚠️ Nenhum arquivo .mp3 encontrado na pasta 'audios/'. Gerando vídeo sem áudio.")

        # 2. Montar o comando FFmpeg
        cmd = [
            "ffmpeg", "-y",         # -y sobrescreve se existir
            "-i", webm_path         # Input 1: O vídeo
        ]
        
        if audio_path:
            cmd.extend(["-i", audio_path])  # Input 2: O áudio
            
        # Parâmetros de codificação para garantir compatibilidade com Instagram/Reels
        cmd.extend([
            "-c:v", "libx264",      # Codec de vídeo h264
            "-preset", "fast",      # Velocidade de encode
            "-crf", "23",           # Qualidade visual
            "-pix_fmt", "yuv420p"   # Pixel format compatível com web
        ])
        
        if audio_path:
            cmd.extend([
                "-c:a", "aac",      # Codec de áudio AAC
                "-b:a", "192k",     # Bitrate do áudio
                "-map", "0:v:0",    # Pega o fluxo de vídeo do input 0
                "-map", "1:a:0",    # Pega o fluxo de áudio do input 1
                "-shortest"         # Corta no final do fluxo mais curto (o vídeo)
            ])
        
        cmd.append(output_path)

        # 3. Executar o FFmpeg
        log.info("🎞️ Processando mixagem do Reel via FFmpeg...")
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        log.info(f"✅ Vídeo MP4 final gerado: {output_path}")
        
        # Opcional: Apagar o webm temporário para limpar espaço
        try:
            os.remove(webm_path)
        except Exception:
            pass

        return output_path

    except subprocess.CalledProcessError as e:
        log.error(f"❌ Erro do FFmpeg (verifique se está instalado): {e}")
        return None
    except Exception as e:
        log.error(f"❌ Erro no processamento de vídeo: {e}")
        return None
