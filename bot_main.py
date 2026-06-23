#!/usr/bin/env python3
"""
bot_main.py — Bot Dentista Curioso v4 (Multiformato: 4:5 Feed + 9:16 Reel Animado)
Fluxo: índice → Gemini Flash → Renderizar 4:5 (PNG) → Gravar 9:16 (WEBM) → FFmpeg (MP4 + Áudio) → Facebook API
"""

import os
import sys
import json
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(override=True)

from gemini_generator import gerar_conteudo
from image_renderer import renderizar_imagem_45, gravar_video_916
from video_processor import processar_video_final
from meta_publisher import publicar_foto, publicar_video

# ─── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

# ─── Caminhos ─────────────────────────────────────────────────────────────────
_DIR         = os.path.dirname(os.path.abspath(__file__))
INDEX_FILE   = os.path.join(_DIR, "post_index.json")
PREVIEW_IMG  = os.path.join(_DIR, "output_preview.png")
PREVIEW_VID  = os.path.join(_DIR, "output_reel.mp4")
TOTAL_POSTS  = 18

# ─── Os 18 prompts ────────────────────────────────────────────────────────────
PROMPTS = [
    "Técnico\nElabore um guia rápido sobre a correta seleção de curetas de Gracey na periodontia. Detalhe qual numeração para dentes anteriores, pré-molares e faces mesiais e distais de molares.",
    "Meme\nCrie um meme sobre o momento em que o paciente insiste em falar frases complexas com abridor de boca, sugador e isolamento. O dentista finge que entendeu tudo.",
    "Quiz técnico → Resposta na Legenda\nFármaco: protocolo padrão AHA para profilaxia antibiótica de endocardite bacteriana em adultos não alérgicos à penicilina. 4 opções de dosagem.",
    "Mito ou Fato técnico\nDentes decíduos (de leite) não possuem raiz. Explique a rizólise fisiológica. Veredicto: MITO ou FATO.",
    "Carreira\nImportância do contrato de prestação de serviços e do TCLE na clínica odontológica. Como protegem o profissional juridicamente.",
    "Técnico\nPasso a passo do localizador apical eletrônico na endodontia. Erros comuns que causam falsos positivos ou negativos (umidade, contato com restaurações metálicas).",
    "Meme\nTweet fake: infarto do dentista quando a matriz metálica deforma ou o anel do sistema seccionado voa longe na hora de fechar o ponto de contato da resina.",
    "Quiz técnico → Resposta na Legenda\nAnatomia interna: porcentagem de incidência de segundo canal (canal lingual) em incisivos inferiores. 4 alternativas.",
    "Mito ou Fato técnico\nEnxaguante bucal com álcool no uso diário: traz mais benefícios ou malefícios? Ressecamento de mucosa, microbiota oral. Veredicto MITO ou FATO.",
    "Carreira\nComo lidar com pacientes que pedem 'só uma olhadinha de graça'. Roteiro ético de como valorizar a consulta de avaliação inicial.",
    "Técnico\nNúcleo metálico fundido versus pino de fibra de vidro: quando indicar cada um. Estrutura coronária remanescente e efeito ferrule.",
    "Meme\nA dor invisível do estudante de odonto ao receber a lista de materiais do semestre (kit, articulador, instrumentais = um carro usado).",
    "Quiz técnico → Resposta na Legenda\nCirurgia: qual fórceps indicado para exodontia de pré-molares superiores? 4 opções de numeração (150, 151, 17, 18).",
    "Mito ou Fato técnico\nClareamento a laser de consultório é significativamente mais eficaz e duradouro que o clareamento caseiro supervisionado. Veredicto MITO ou FATO.",
    "Carreira\nImpacto do follow-up pós-cirúrgico. Como uma mensagem de WhatsApp da secretária no dia seguinte à cirurgia de siso é uma ferramenta poderosa de fidelização.",
    "Técnico\nComo identificar cárie interproximal incipiente na radiografia bite-wing. Macete visual: perda de definição da junção amelodentinária.",
    "Meme\nO momento em que o sugador de saliva prende na mucosa da bochecha ou no assoalho bucal e o dentista tem que soltar sem o paciente entrar em pânico.",
    "Quiz técnico → Resposta na Legenda\nOdontopediatria: em qual idade média ocorre a erupção do primeiro molar permanente, confundido pelos pais com dente decíduo. 4 alternativas.",
]


# ─── Controle de índice ────────────────────────────────────────────────────────
def carregar_indice() -> int:
    if os.path.exists(INDEX_FILE):
        try:
            return int(json.load(open(INDEX_FILE))["index"])
        except Exception:
            pass
    return 0


def salvar_indice(idx: int):
    json.dump({"index": idx}, open(INDEX_FILE, "w"), indent=2)


# ─── Hashtags por post ─────────────────────────────────────────────────────────
HASHTAGS = [
    "#periodontia #gracey #odontologia #dentista #dentistaacurioso",
    "#meme #humor #dentista #odontologia #dentistaacurioso",
    "#quiz #farmacologia #endocardite #odontologia #dentistaacurioso",
    "#mitoufato #dentes #decíduos #odontologia #dentistaacurioso",
    "#carreira #tcle #contrato #odontologia #dentistaacurioso",
    "#endodontia #localizadorapical #dentista #odontologia #dentistaacurioso",
    "#meme #humor #resina #dentista #dentistaacurioso",
    "#quiz #anatomia #endodontia #dentista #dentistaacurioso",
    "#mitoufato #enxaguante #bucal #odontologia #dentistaacurioso",
    "#carreira #consultório #dentista #odontologia #dentistaacurioso",
    "#tecnico #nucleo #pino #endodontia #dentistaacurioso",
    "#meme #humor #estudante #odonto #dentistaacurioso",
    "#quiz #cirurgia #exodontia #dentista #dentistaacurioso",
    "#mitoufato #clareamento #laser #odontologia #dentistaacurioso",
    "#carreira #followup #gestão #dentista #dentistaacurioso",
    "#radiologia #carie #bitewin #odontologia #dentistaacurioso",
    "#meme #humor #sugador #dentista #dentistaacurioso",
    "#quiz #odontopediatria #molar #dentista #dentistaacurioso",
]


# ─── Main ──────────────────────────────────────────────────────────────────────
def main():
    log.info("🦷 Bot Dentista Curioso v4 (Multiformato + Reel Animado)")
    log.info(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

    for var in ("FB_TOKEN", "FB_PAGE_ID"):
        if not os.environ.get(var):
            log.error(f"❌ '{var}' não configurada. Encerrando.")
            sys.exit(1)

    if not os.environ.get("GEMINI_API_KEY"):
        log.error("❌ GEMINI_API_KEY não configurada. Encerrando.")
        sys.exit(1)

    # 1. Índice atual
    idx = carregar_indice()
    if idx >= TOTAL_POSTS:
        idx = 0
        
    log.info(f"📌 Índice: {idx + 1}/{TOTAL_POSTS}")

    prompt = PROMPTS[idx]
    log.info(f"📝 Prompt: {prompt[:100]}...")

    # 2. Gerar conteúdo com Gemini Flash
    log.info("🤖 Gerando conteúdo com Gemini Flash...")
    conteudo = gerar_conteudo(prompt)
    if not conteudo:
        log.error("❌ Falha na geração de conteúdo.")
        sys.exit(1)

    legenda  = conteudo.get("caption", "")
    hashtags = conteudo.get("hashtags", HASHTAGS[idx])

    # 3. Gerar Imagem 4:5 (Feed)
    log.info("📸 Iniciando renderização da Imagem 4:5...")
    img_bytes = renderizar_imagem_45(conteudo)
    if not img_bytes:
        log.error("❌ Falha ao renderizar imagem 4:5.")
        sys.exit(1)

    with open(PREVIEW_IMG, "wb") as f:
        f.write(img_bytes)

    # 4. Gerar Vídeo 9:16 (Reel)
    log.info("🎥 Iniciando gravação do Vídeo animado 9:16...")
    webm_path = gravar_video_916(conteudo)
    if not webm_path:
        log.error("❌ Falha ao gravar vídeo 9:16.")
        sys.exit(1)
        
    # 5. Baixar Música em Alta (Dinâmico)
    from audio_downloader import baixar_audio_em_alta
    log.info("🎵 Preparando áudio dinâmico...")
    baixar_audio_em_alta()

    # 6. Processar Vídeo (Converter para MP4 e adicionar Áudio)
    log.info("🎞️ Mixando áudio e convertendo vídeo para MP4...")
    mp4_path = processar_video_final(webm_path, PREVIEW_VID)
    if not mp4_path:
        log.error("❌ Falha no processamento via FFmpeg.")
        sys.exit(1)

    # 7. Publicar Foto no Facebook
    log.info("📘 Publicando Foto 4:5 no Facebook...")
    foto_id = publicar_foto(img_bytes, legenda, hashtags)

    # 8. Publicar Vídeo no Facebook Reels
    log.info("📘 Publicando Reel 9:16 no Facebook...")
    reel_id = publicar_video(mp4_path, legenda, hashtags)

    if not foto_id and not reel_id:
        log.error("❌ Ambas as publicações falharam. O índice NÃO será avançado.")
        sys.exit(1)
        
    if not foto_id or not reel_id:
        log.warning("⚠️ Uma das mídias falhou ao publicar, mas a outra foi com sucesso. Avançando índice.")

    # 9. Avançar índice
    novo_idx = idx + 1
    salvar_indice(novo_idx)
    log.info(f"✅ Fluxo do Post {novo_idx}/18 completo!")
    log.info("🏁 Finalizado com sucesso.")


if __name__ == "__main__":
    main()
