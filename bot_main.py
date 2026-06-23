#!/usr/bin/env python3
"""
bot_main.py — Bot Dentista Curioso v3 (HTML Template + Playwright Screenshot)
Fluxo: índice → Gemini Flash (conteúdo) → HTML template → Playwright screenshot → Facebook
Visual idêntico ao canvas DentPost Pro, sem depender de sessão Google.
"""

import os
import sys
import json
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(override=True)

from gemini_generator import gerar_conteudo
from image_renderer import renderizar_post
from meta_publisher import publicar_no_meta

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
PREVIEW_FILE = os.path.join(_DIR, "output_preview.png")
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
    log.info("🦷 Bot Dentista Curioso v3 (DentPost Style) — INICIANDO")
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
    
    # Se por acaso o índice estiver fora do limite, forçar reset (ciclo infinito)
    if idx >= TOTAL_POSTS:
        idx = 0
        
    log.info(f"📌 Índice: {idx + 1}/{TOTAL_POSTS}")

    prompt = PROMPTS[idx]
    log.info(f"📝 Prompt: {prompt[:100]}...")

    # 2. Gerar conteúdo estruturado com Gemini Flash
    log.info("🤖 Gerando conteúdo com Gemini Flash...")
    conteudo = gerar_conteudo(prompt)
    if not conteudo:
        log.error("❌ Falha na geração de conteúdo.")
        sys.exit(1)

    # 3. Renderizar template HTML e capturar screenshot via Playwright
    log.info(f"🎨 Renderizando template visual ({conteudo.get('type')})...")
    img_bytes = renderizar_post(conteudo)
    if not img_bytes:
        log.error("❌ Falha ao renderizar imagem.")
        sys.exit(1)

    # Salvar preview local
    with open(PREVIEW_FILE, "wb") as f:
        f.write(img_bytes)
    log.info(f"💾 Preview: {PREVIEW_FILE} ({len(img_bytes) // 1024}KB)")

    # 4. Publicar no Facebook
    log.info("📘 Publicando no Facebook...")
    legenda  = conteudo.get("caption", "")
    hashtags = conteudo.get("hashtags", HASHTAGS[idx])
    post_id  = publicar_no_meta(img_bytes, legenda, hashtags)

    if not post_id:
        log.error("❌ Falha na publicação. Índice NÃO avançado.")
        sys.exit(1)

    # 5. Avançar índice
    novo_idx = idx + 1
    salvar_indice(novo_idx)
    restantes = TOTAL_POSTS - novo_idx
    log.info(f"✅ Post {novo_idx}/18 publicado! {restantes} restantes.")
    log.info("🏁 Finalizado com sucesso.")


if __name__ == "__main__":
    main()
