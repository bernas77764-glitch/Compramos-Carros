"""Interface web mínima (apenas biblioteca padrão) para demonstrar o avaliador.

    python3 -m avaliador servir --porta 8000   →  http://localhost:8000
"""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlparse

from .avaliacao import avaliar
from .config import carregar_config
from .fontes import FonteCSV
from .modelos import Viatura

PAGINA = """<!doctype html>
<html lang="pt">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Avaliador de Viaturas — protótipo</title>
<style>
  :root { --fundo:#f5f6f8; --cartao:#fff; --texto:#1b1f24; --mudo:#5b6470; --linha:#e1e5ea; --acento:#0b5fff; --ok:#1a7f37; --aviso:#b45309; --mau:#b42318; }
  * { box-sizing:border-box }
  body { margin:0; font:15px/1.45 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif; background:var(--fundo); color:var(--texto) }
  header { background:#fff; border-bottom:1px solid var(--linha); padding:14px 24px }
  header h1 { margin:0; font-size:18px } header p { margin:2px 0 0; color:var(--mudo); font-size:13px }
  main { max-width:1080px; margin:24px auto; padding:0 16px; display:grid; grid-template-columns:340px 1fr; gap:20px }
  @media (max-width:820px) { main { grid-template-columns:1fr } }
  .cartao { background:var(--cartao); border:1px solid var(--linha); border-radius:10px; padding:18px }
  label { display:block; font-size:13px; color:var(--mudo); margin:10px 0 4px }
  input, select, button { width:100%; padding:8px 10px; border:1px solid var(--linha); border-radius:6px; font:inherit; background:#fff }
  button { background:var(--acento); color:#fff; border:0; margin-top:16px; cursor:pointer; font-weight:600 }
  button:disabled { opacity:.6; cursor:wait }
  .grelha2 { display:grid; grid-template-columns:1fr 1fr; gap:10px }
  .valor { font-size:34px; font-weight:700; letter-spacing:-.5px } .valor small { font-size:14px; color:var(--mudo); font-weight:400 }
  .proposta { color:var(--ok) }
  .etiqueta { display:inline-block; padding:2px 8px; border-radius:999px; font-size:12px; font-weight:600 }
  .alta { background:#dcfce7; color:var(--ok) } .media { background:#fef3c7; color:var(--aviso) } .baixa, .insuficiente { background:#fee2e2; color:var(--mau) }
  table { width:100%; border-collapse:collapse; font-size:13px; margin-top:8px } th, td { padding:6px 8px; border-bottom:1px solid var(--linha); text-align:right; white-space:nowrap } th:first-child, td:first-child, th:nth-child(2), td:nth-child(2) { text-align:left }
  .tabela { overflow-x:auto }
  .avisos li { color:var(--aviso) } .mudo { color:var(--mudo); font-size:13px }
  dl { display:grid; grid-template-columns:auto auto; gap:4px 16px; margin:8px 0; font-size:13px } dt { color:var(--mudo) } dd { margin:0; text-align:right }
  .oculto { display:none }
</style>
</head>
<body>
<header><h1>Avaliador de Viaturas — protótipo</h1><p>Estimativa por comparáveis de mercado. Valores indicativos, a confirmar por um avaliador.</p></header>
<main>
  <form class="cartao" id="form">
    <label>Marca</label><select id="marca" required></select>
    <label>Modelo</label><select id="modelo" required></select>
    <div class="grelha2">
      <div><label>Ano</label><input id="ano" type="number" min="1990" max="2026" value="2019" required></div>
      <div><label>Quilómetros</label><input id="km" type="number" min="0" step="1000" value="85000" required></div>
    </div>
    <div class="grelha2">
      <div><label>Combustível</label><select id="combustivel"><option>Gasolina</option><option>Diesel</option><option>Híbrido</option><option>Elétrico</option></select></div>
      <div><label>Caixa</label><select id="caixa"><option value="">Indiferente</option><option>Manual</option><option>Automática</option></select></div>
    </div>
    <label>Estado geral</label>
    <select id="estado"><option value="1">1 — Mau (danos, mecânica duvidosa)</option><option value="2">2 — Fraco</option><option value="3" selected>3 — Normal para a idade</option><option value="4">4 — Bom</option><option value="5">5 — Impecável</option></select>
    <button id="btn" type="submit">Avaliar</button>
    <p class="mudo" id="erro"></p>
  </form>
  <section class="cartao" id="resultado">
    <p class="mudo">Preencha os dados e carregue em <b>Avaliar</b>.</p>
  </section>
</main>
<script>
const $ = id => document.getElementById(id);
const eur = v => v == null ? '—' : new Intl.NumberFormat('pt-PT',{style:'currency',currency:'EUR',maximumFractionDigits:0}).format(v);
const num = v => new Intl.NumberFormat('pt-PT').format(v);
let catalogo = {};
fetch('/api/catalogo').then(r=>r.json()).then(c => {
  catalogo = c;
  $('marca').innerHTML = Object.keys(c).map(m=>`<option>${m}</option>`).join('');
  $('marca').value = 'Renault' in c ? 'Renault' : Object.keys(c)[0];
  atualizarModelos();
});
function atualizarModelos(){ const ms = catalogo[$('marca').value]||[]; $('modelo').innerHTML = ms.map(m=>`<option>${m}</option>`).join(''); }
$('marca').addEventListener('change', atualizarModelos);
$('form').addEventListener('submit', async e => {
  e.preventDefault(); $('btn').disabled = true; $('erro').textContent = '';
  const corpo = { marca:$('marca').value, modelo:$('modelo').value, ano:+$('ano').value, quilometros:+$('km').value,
    combustivel:$('combustivel').value, caixa:$('caixa').value, estado:+$('estado').value };
  try {
    const r = await fetch('/api/avaliar',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(corpo)});
    const d = await r.json();
    if(!r.ok) throw new Error(d.erro||'Erro');
    mostrar(d);
  } catch(err){ $('erro').textContent = err.message; }
  $('btn').disabled = false;
});
function mostrar(d){
  const s = $('resultado'); const et = `<span class="etiqueta ${d.confianca}">confiança ${d.confianca}</span>`;
  if (d.valor_mercado == null) {
    s.innerHTML = `<h2 style="margin-top:0">Sem valor automático ${et}</h2><ul class="avisos">${d.avisos.map(a=>`<li>${a}</li>`).join('')}</ul>
      <p class="mudo">Comparáveis encontrados: ${d.n_comparaveis}. Avaliação manual recomendada.</p>`; return;
  }
  const dt = d.detalhe;
  s.innerHTML = `
    <div style="display:flex;gap:24px;flex-wrap:wrap;align-items:flex-end">
      <div><div class="mudo">Valor de mercado</div><div class="valor">${eur(d.valor_mercado)} <small>(${eur(d.intervalo[0])} – ${eur(d.intervalo[1])})</small></div></div>
      <div><div class="mudo">Proposta de compra</div><div class="valor proposta">${eur(d.proposta_compra)}</div></div>
      <div>${et}<div class="mudo">${d.n_comparaveis} comparáveis</div></div>
    </div>
    <dl>
      <dt>Mediana ponderada dos comparáveis ajustados</dt><dd>${eur(dt.mediana_ponderada)}</dd>
      <dt>Ajuste por estado (${d.viatura.estado}/5)</dt><dd>${dt.ajuste_estado_pct>=0?'+':''}${dt.ajuste_estado_pct} %</dd>
      <dt>Margem (${dt.margem_pct} %)</dt><dd>−${eur(dt.margem_eur)}</dd>
      <dt>Custos fixos</dt><dd>−${eur(dt.custos_fixos_eur)}</dd>
      <dt>Recondicionamento (estado ${d.viatura.estado})</dt><dd>−${eur(dt.recondicionamento_eur)}</dd>
      <dt>Dispersão (coef. variação)</dt><dd>${(dt.coef_variacao*100).toFixed(1)} %</dd>
    </dl>
    ${d.avisos.length?`<ul class="avisos">${d.avisos.map(a=>`<li>${a}</li>`).join('')}</ul>`:''}
    <h3 style="margin-bottom:0">Comparáveis usados</h3><p class="mudo" style="margin-top:2px">Preço do anúncio com desconto de negociação de ${dt.desconto_negociacao_pct} %, depois ajustado ao ano e km da viatura.</p>
    <div class="tabela"><table><thead><tr><th>ID</th><th>Fonte</th><th>Ano</th><th>Km</th><th>Caixa</th><th>Anúncio</th><th>Aj. km</th><th>Aj. ano</th><th>Ajustado</th><th>Peso</th></tr></thead><tbody>
    ${d.comparaveis.map(c=>{const a=c.anuncio;return `<tr><td>${a.id}</td><td>${a.fonte}</td><td>${a.ano}</td><td>${num(a.quilometros)}</td><td>${a.caixa}</td><td>${eur(a.preco)}</td><td>${c.ajuste_km>=0?'+':''}${eur(c.ajuste_km)}</td><td>${c.ajuste_ano>=0?'+':''}${eur(c.ajuste_ano)}</td><td><b>${eur(c.preco_ajustado)}</b></td><td>${c.peso.toFixed(2)}</td></tr>`}).join('')}
    </tbody></table></div>`;
}
</script>
</body>
</html>
"""


def criar_handler(fonte: FonteCSV, cfg: dict[str, Any]) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        def _enviar(self, codigo: int, corpo: bytes, tipo: str) -> None:
            self.send_response(codigo)
            self.send_header("Content-Type", tipo)
            self.send_header("Content-Length", str(len(corpo)))
            self.end_headers()
            self.wfile.write(corpo)

        def _json(self, codigo: int, dados: Any) -> None:
            self._enviar(codigo, json.dumps(dados, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

        def do_GET(self) -> None:  # noqa: N802
            caminho = urlparse(self.path).path
            if caminho == "/":
                self._enviar(200, PAGINA.encode("utf-8"), "text/html; charset=utf-8")
            elif caminho == "/api/catalogo":
                self._json(200, fonte.catalogo())
            else:
                self._json(404, {"erro": "não encontrado"})

        def do_POST(self) -> None:  # noqa: N802
            if urlparse(self.path).path != "/api/avaliar":
                self._json(404, {"erro": "não encontrado"})
                return
            tamanho = int(self.headers.get("Content-Length", 0))
            try:
                dados = json.loads(self.rfile.read(tamanho) or b"{}")
                viatura = Viatura(
                    marca=str(dados["marca"]),
                    modelo=str(dados["modelo"]),
                    ano=int(dados["ano"]),
                    quilometros=int(dados["quilometros"]),
                    combustivel=str(dados["combustivel"]),
                    caixa=str(dados.get("caixa") or ""),
                    potencia_cv=int(dados.get("potencia_cv") or 0),
                    estado=int(dados.get("estado") or 3),
                )
            except (KeyError, ValueError, TypeError, json.JSONDecodeError) as e:
                self._json(400, {"erro": f"pedido inválido: {e}"})
                return
            resultado = avaliar(viatura, fonte.obter(viatura.marca, viatura.modelo), cfg)
            self._json(200, resultado.para_dict())

        def log_message(self, formato: str, *args: Any) -> None:
            print(f"[web] {formato % args}")

    return Handler


def servir(porta: int = 8000, caminho_anuncios: str | None = None, caminho_config: str | None = None) -> None:
    fonte = FonteCSV(caminho_anuncios)
    fonte.carregar()  # falha cedo se o ficheiro não existir
    cfg = carregar_config(caminho_config)
    servidor = ThreadingHTTPServer(("127.0.0.1", porta), criar_handler(fonte, cfg))
    print(f"Avaliador disponível em http://localhost:{porta}  (Ctrl+C para parar)")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        servidor.server_close()
