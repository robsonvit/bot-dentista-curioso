# ✅ Deu Certo — Renderização Visual HTML com Playwright

**Data:** 22/06/2026
**Projeto:** Bot Dentista Curioso v3

## O que funcionou

Substituímos o processo falho e complexo de automatizar o Google Canvas Web (que exigia autenticação) e também abandonamos a geração rústica de imagens via Pillow. O que funcionou brilhantemente foi **recriar o frontend do canvas localmente via HTML/CSS e rodar o Playwright em modo headless para injetar os dados dinâmicos do Gemini (`window.POST_DATA`) e capturar um screenshot instantâneo e perfeito.**

Isso evitou depender da interface do Google, resolveu problemas de fontes (as fontes precisam carregar completamente para manter a beleza do design), garantiu que os 5 tipos visuais rodassem perfeitamente, e a publicação no Facebook (Meta API) ocorreu com imagem e texto em alta qualidade.

## Arquivos envolvidos

| Arquivo | Papel na solução |
|---------|-----------------|
| `render_post.html` | O template frontend com CSS que possui o mesmo visual lindo original do canvas, estruturado com funções JS para desenhar post Técnico, Meme, Quiz, etc. |
| `image_renderer.py` | Controla o Playwright rodando em background: injeta o JSON em `render_post.html`, espera a tela montar com as fontes, tira screenshot e devolve os bytes da imagem final. |
| `gemini_generator.py` | Pega a instrução do post (ex: "Fale sobre curetas") e pede para o LLM responder APENAS JSON formatado conforme a regra do nosso HTML. |
| `bot_main.py` | O orquestrador que une os 3 acima, avança o índice no `post_index.json` e repassa a imagem pro `meta_publisher.py` postar no Facebook. |

## Como replicar

Sempre que um usuário pedir um post de altíssima fidelidade gráfica com texto dinâmico do LLM sem depender da estabilidade de portais externos com login, crie um documento HTML de base responsivo/fiel ao design, use o `Playwright.page.set_content(html)` e injete no script os dados via JSON para depois capturar a tag contêiner usando o método `locator.screenshot()`.

## Observações

- **Google Fonts no Headless:** Foi preciso aguardar explicitamente a API `document.fonts.ready` no Playwright, do contrário o screenshot seria tirado "em branco" antes da fonte principal baixar, comprometendo o visual.
- **GitHub Actions Branch:** Lembre-se de certificar que o pull/push usa a mesma branch raiz criada pelo Git local (`master` ou `main`).
