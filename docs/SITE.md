# Site Compramos Carros — compramoscarros.pt

Site estático (HTML, CSS e JavaScript, sem dependências), com a mesma estrutura, textos e
logotipo do site original.

| Página | Ficheiro |
|---|---|
| Início (formulário de avaliação) | `index.html` |
| Como funciona | `como-funciona.html` |
| Quem Somos | `quem-somos.html` |
| Centro de Entregas | `centro-de-entregas.html` |
| Contactos | `contactos.html` |
| Política de privacidade | `politica-de-privacidade.html` |
| Política de cookies | `politica-de-cookies.html` |

## Editar textos

As páginas são geradas por `ferramentas/gerar_site.py` (cabeçalho e rodapé num só sítio).
Altere esse ficheiro e corra:

```bash
python3 ferramentas/gerar_site.py
```

Para ver o site localmente: `python3 -m http.server --directory site 8000` e abrir
http://localhost:8000.

## Formulários

Configurados em `assets/js/config.js`:

- Com `formEndpoint` vazio (por omissão), o pedido abre o WhatsApp para o 912 263 717 com
  todos os dados do formulário já preenchidos.
- Para receber os pedidos por email, crie um formulário gratuito em https://formspree.io
  (com o email da empresa) e coloque o endereço em `formEndpoint`,
  por exemplo `"https://formspree.io/f/abcd1234"`.

## Publicar em compramoscarros.pt (GitHub Pages)

1. Juntar este ramo ao `main`.
2. No GitHub: **Settings → Pages → Source: GitHub Actions**. O workflow
   `.github/workflows/site.yml` publica a pasta `site/` a cada alteração.
3. Em **Settings → Pages → Custom domain** escrever `compramoscarros.pt` e ativar
   **Enforce HTTPS**.
4. No painel do registo do domínio, criar os registos DNS:
   - `A` em `@` para `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`
   - `CNAME` em `www` para `bernas77764-glitch.github.io`

A pasta também pode ser enviada tal como está para qualquer alojamento (Netlify, Vercel,
cPanel, …).
