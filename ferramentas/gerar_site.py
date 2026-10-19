#!/usr/bin/env python3
"""Gera as páginas estáticas do site Compramos Carros na pasta site/.

Cabeçalho, rodapé e textos de todas as páginas estão aqui: altere este ficheiro e
corra  python3 ferramentas/gerar_site.py  para atualizar os .html.
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "site"
DOMINIO = "https://compramoscarros.pt"
MAPA_Q = "MGB Automóveis, Estrada Nacional 249-4, 2785-574 São Domingos de Rana"
from urllib.parse import quote
MAPA_EMBED = "https://www.google.com/maps?q=" + quote(MAPA_Q) + "&output=embed"
MAPA_LINK = "https://www.google.com/maps/search/?api=1&query=" + quote(MAPA_Q)

def ic(path, extra=""):
    return ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" '
            'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"' + extra + '>' + path + '</svg>')

I = {
 "user": ic('<circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 3.6-7 8-7s8 3 8 7"/>'),
 "phone": ic('<rect x="6" y="2" width="12" height="20" rx="2"/><line x1="11" y1="18" x2="13" y2="18"/>'),
 "mail": ic('<rect x="2" y="4" width="20" height="16" rx="1"/><polyline points="2 5 12 13 22 5"/><line x1="2" y1="20" x2="9" y2="12"/><line x1="22" y1="20" x2="15" y2="12"/>'),
 "pin": ic('<path d="M12 22s7-6.1 7-12a7 7 0 1 0-14 0c0 5.9 7 12 7 12z"/><circle cx="12" cy="10" r="2.6"/>'),
 "gauge": ic('<circle cx="12" cy="12" r="9"/><polyline points="12 7 12 12 15 14"/>'),
 "car": ic('<path d="M3 15v-3l2-5a2 2 0 0 1 1.9-1.4h10.2A2 2 0 0 1 19 7l2 5v3"/><rect x="2" y="12" width="20" height="5" rx="1.5"/><circle cx="7" cy="17.5" r="1.8"/><circle cx="17" cy="17.5" r="1.8"/>'),
 "whats": '<svg viewBox="0 0 32 32" fill="currentColor" aria-hidden="true"><path d="M16 3a13 13 0 0 0-11.2 19.6L3 29l6.6-1.7A13 13 0 1 0 16 3zm0 23.7c-2 0-4-.5-5.7-1.6l-.4-.2-3.9 1 1-3.8-.3-.4A10.7 10.7 0 1 1 16 26.7zm5.9-8c-.3-.2-1.9-1-2.2-1.1-.3-.1-.5-.2-.7.2l-1 1.2c-.2.2-.4.2-.7.1-.3-.2-1.4-.5-2.6-1.6-1-.9-1.6-1.9-1.8-2.2-.2-.3 0-.5.1-.7l.5-.6.3-.5c.1-.2 0-.4 0-.6l-1-2.4c-.3-.6-.5-.5-.7-.5h-.6c-.2 0-.6.1-.9.4-.3.3-1.2 1.2-1.2 2.9s1.2 3.4 1.4 3.6c.2.2 2.4 3.7 5.9 5.2.8.4 1.5.6 2 .7.8.3 1.6.2 2.2.1.7-.1 1.9-.8 2.2-1.6.3-.8.3-1.4.2-1.6-.1-.1-.3-.2-.6-.4z"/></svg>',
 "menu": ic('<line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/>', ' stroke-width="2"'),
 "seta": ic('<line x1="12" y1="3" x2="12" y2="21"/><polyline points="5 14 12 21 19 14"/>', ' class="seta"'),
}

MENU = [("como-funciona.html", "Como funciona"), ("quem-somos.html", "Quem Somos"),
        ("centro-de-entregas.html", "Centro de Entregas"), ("contactos.html", "Contactos")]

def pagina(ficheiro, titulo, descricao, corpo, atual=None):
    menu = "".join(
        f'<li><a href="{href}"{" aria-current=\"page\"" if href == atual else ""}>{nome}</a></li>'
        for href, nome in MENU)
    canonical = DOMINIO + "/" + ("" if ficheiro == "index.html" else ficheiro)
    html = f"""<!doctype html>
<html lang="pt-PT">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titulo}</title>
<meta name="description" content="{descricao}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:title" content="{titulo}">
<meta property="og:description" content="{descricao}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{DOMINIO}/assets/img/quem-somos.jpg">
<meta property="og:locale" content="pt_PT">
<meta name="theme-color" content="#2e294e">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Barlow:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/css/style.css">
</head>
<body>
<header class="cabecalho">
  <div class="contentor">
    <a class="logo" href="index.html" aria-label="Compramos Carros — página inicial"><img src="assets/img/logo.svg" alt="Compramos Carros" width="170" height="41"></a>
    <button class="menu-botao" type="button" aria-label="Abrir menu" aria-expanded="false" aria-controls="navegacao">{I["menu"]}</button>
    <nav class="navegacao" id="navegacao" aria-label="Menu principal">
      <ul class="menu">{menu}</ul>
    </nav>
  </div>
</header>

<main>
{corpo.strip()}
</main>

<footer class="rodape">
  <div class="contentor">
    <img class="logo-rodape" src="assets/img/logo.svg" alt="Compramos Carros" width="160" height="38" loading="lazy">
    <ul class="rodape-menu">{"".join(f'<li><a href="{h}">{n}</a></li>' for h, n in MENU)}</ul>
    <ul class="rodape-legal">
      <li><a href="politica-de-privacidade.html">Política de privacidade</a></li>
      <li><a href="politica-de-cookies.html">Política de cookies</a></li>
      <li><a href="https://www.livroreclamacoes.pt/Inicio/" target="_blank" rel="noopener">Livro de reclamações</a></li>
    </ul>
    <p class="copyright">© <span data-ano>2024</span> Compramos Carros.<br>Todos os direitos reservados.</p>
  </div>
</footer>

<a class="whatsapp" href="https://wa.me/351912263717" target="_blank" rel="noopener" aria-label="Entre em contacto por WhatsApp">{I["whats"]}<span>Entre em contacto</span></a>

<div class="cookies" role="dialog" aria-live="polite" aria-label="Aviso de cookies">
  <p>Utilizamos cookies para melhorar a sua experiência no nosso site. Saiba mais na nossa <a href="politica-de-cookies.html">Política de cookies</a>.</p>
  <button class="botao" type="button">Aceitar</button>
</div>

<script src="assets/js/config.js"></script>
<script src="assets/js/main.js"></script>
</body>
</html>
"""
    (OUT / ficheiro).write_text(html, encoding="utf-8")

AVISO_DADOS = """<p class="aviso-dados">Os dados recolhidos serão incluídos na nossa agenda de contactos, de acordo com a legislação de proteção de dados em vigor, apenas para facilitar futuros contactos da Compramos Carros.<br>
<a href="politica-de-privacidade.html">Para saber mais sobre a nossa Política de Privacidade clique aqui.</a></p>"""

def campo(icone, html):
    return f'<div class="campo">{I[icone]}{html}</div>'

def entrada(nome, rotulo, tipo="text", extra=""):
    return f'<input type="{tipo}" name="{nome}" placeholder="{rotulo}" aria-label="{rotulo}" required{extra}>'

def escolha(nome, rotulo, lista=None, opcoes="", obrigatorio=True):
    dl = f' data-lista="{lista}"' if lista else ""
    req = " required" if obrigatorio else ""
    return f'<select name="{nome}" aria-label="{rotulo}"{dl}{req}><option value="" disabled selected>{rotulo}</option>{opcoes}</select>'

# ------------------------------------------------------------------ Início
inicio = f"""
<section class="heroi" id="avaliacao">
  <div class="contentor grelha">
    <div class="texto">
      <h1>A forma fácil de <span class="lima">vender</span> o seu carro</h1>
      <p class="subtitulo">Em apenas <b>3 etapas</b> compramos o seu carro de <b>forma simplificada e justa!</b></p>
      <h2 class="marque">Marque agora</h2>
      <p class="marque-sub">A avaliação do seu veículo!</p>
      {I["seta"]}
    </div>

    <form class="cartao-formulario" data-formulario data-assunto="Pedido de avaliação grátis">
      <h2>Preencha o formulário e aproveite uma avaliação gratuita!</h2>
      <input class="armadilha" type="text" name="_gotcha" tabindex="-1" autocomplete="off" aria-hidden="true">
      {campo("user", entrada("nome", "Nome", extra=' autocomplete="name"'))}
      {campo("phone", entrada("telefone", "Telefone", "tel", ' autocomplete="tel" inputmode="tel"'))}
      {campo("mail", entrada("email", "E-mail", "email", ' autocomplete="email"'))}
      {campo("pin", escolha("distrito", "Distrito", "distrito"))}
      {campo("gauge", entrada("km", "KM do carro", "number", ' min="0" step="1" inputmode="numeric"'))}
      {campo("car", entrada("matricula", "Matrícula do carro", extra=' maxlength="8" autocapitalize="characters"'))}
      {campo("car", escolha("ano", "Ano do Carro", "ano"))}
      {campo("car", escolha("mes", "Mês do Carro", "mes"))}
      {campo("car", escolha("marca", "Marca do carro", "marca"))}
      {campo("car", escolha("modelo", "Modelo do carro", "modelo"))}
      {campo("car", entrada("versao", "Versão do carro"))}
      {campo("car", escolha("transmissao", "Transmissão", opcoes="<option>Manual</option><option>Automática</option>"))}
      {AVISO_DADOS}
      <div class="formulario-acao"><button class="botao" type="submit">Pedir avaliação grátis</button></div>
      <div class="mensagem-form" role="status"></div>
    </form>
  </div>
</section>

<section class="seccao processo">
  <div class="contentor grelha">
    <div class="imagem-deco esquerda"><img src="assets/img/inicio-processo.webp" alt="Aperto de mão na compra de um carro e fila de carros usados" width="651" height="603" loading="lazy" style="box-shadow:none"></div>
    <div>
      <h2 class="seccao-titulo">Processo simplificado</h2>
      <div class="passo">
        <img src="assets/img/icones/avaliamos.png" alt="" width="64" height="62" loading="lazy">
        <h3>Avaliamos o seu carro</h3>
        <p>Avalie o seu carro conosco e descubra o verdadeiro valor do seu veículo.</p>
      </div>
      <div class="passo">
        <img src="assets/img/icones/oferta.png" alt="" width="64" height="66" loading="lazy">
        <h3>Fazemos a oferta</h3>
        <p>Fazemos a oferta mais competitiva para o seu veículo. Confie em nós para obter o melhor negócio possível.</p>
      </div>
      <div class="passo">
        <img src="assets/img/icones/finalizamos.png" alt="" width="64" height="61" loading="lazy">
        <h3>Finalizamos a compra</h3>
        <p>Finalizamos a compra do seu carro de forma rápida e sem complicações.</p>
      </div>
    </div>
  </div>
</section>
"""
pagina("index.html", "Compramos Carros",
       "A forma fácil de vender o seu carro. Em apenas 3 etapas compramos o seu carro de forma simplificada e justa! Peça a sua avaliação grátis.",
       inicio)

# ------------------------------------------------------------------ Como funciona
CRITERIOS = [("impostos", "Ter os impostos em dia"), ("ipo", "Ter IPO válida"),
             ("matricula", "Ter matrícula portuguesa"), ("chaves", "Ter duplicado de chaves"),
             ("penhora", "Não estar penhorado"), ("proprietario", "Ser proprietário do carro*"),
             ("manuais", "Ter Manuais e Livro de Revisões atualizado"),
             ("perda-total", "Nunca ter sido considerado Perda Total, num sinistro"),
             ("taxi", "Nunca ter sido utilizado como Táxi, Rent-a-car, Escola de Condução ou Competição"),
             ("quilometragem", "Quilometragem não viciada")]
crit_html = "".join(
    f'<div class="criterio"><img src="assets/img/icones/{f}.png" alt="" width="64" height="64" loading="lazy"><h3>{t}</h3></div>'
    for f, t in CRITERIOS)
PECA = '<p class="acao"><a class="botao" href="index.html#avaliacao">Peça a sua avaliação grátis</a></p>'

como = f"""
<div class="titulo-pagina"><h1>Como funciona</h1></div>

<section class="seccao">
  <div class="contentor bloco">
    <div>
      <h2>Facilidade e simplicidade</h2>
      <p>Insira todos os detalhes relativos ao veículo que deseja vender e submeta para avaliação no Compramos Carros. É de vital importância que seja sincero e honesto nas condições do seu automóvel, pois é com base nessa informação que será efectuada a proposta (sempre sujeita a uma inspeção presencial).</p>
      <p><b>Em 24 horas irá receber uma proposta (por email ou contacto telefónico) que será válida por 7 dias úteis.</b></p>
      <p>Quando receber o email com a nossa proposta, agende directamente no nosso calendário a inspeção final e entrega do seu veículo.</p>
      {PECA}
    </div>
    <div class="bloco-imagem imagem-deco"><img src="assets/img/como-funciona-facilidade.jpg" alt="Cliente satisfeito junto ao seu carro" width="651" height="428" loading="lazy"></div>
  </div>
</section>

<section class="seccao" style="background:var(--fundo-suave)">
  <div class="contentor">
    <h2 class="seccao-titulo">Critérios de avaliação</h2>
    <p class="introducao">Além dos dados que nos fornece ao inserir as informações do seu veículo, nossa avaliação leva em conta os seguintes critérios:</p>
    <div class="criterios">{crit_html}</div>
    <p class="nota">Caso haja incertezas ou se suspeitar que o seu veículo possa não cumprir com estes critérios, por favor mencione isso ao inserir os dados do seu carro para avaliação.</p>
    <p class="nota">*Se o seu carro estiver sob financiamento, também estamos aptos a adquiri-lo. Nesse caso, solicitaremos o valor de quitação à instituição financeira e cuidaremos de todo o processo, mediante a sua autorização. O pagamento será realizado por meio de ajuste de contas.</p>
    {PECA}
  </div>
</section>

<section class="seccao">
  <div class="contentor bloco inverso">
    <div>
      <h2>Inspeção antes de entrega</h2>
      <p>Nem todos somos especialistas na avaliação dos danos e estado geral do automóvel, essa é a nossa função e com a nossa vasta experiência sabemos fazê-lo muito bem. Pedimos apenas que seja sincero e objectivo na informação fornecida.</p>
      <p><b>De forma a ser um processo completamente justo para ambas as partes, reservamo-nos o direito de realizar uma inspeção no carro para determinar se desejamos ou não adquiri-lo e qual será o valor definitivo da compra.</b></p>
    </div>
    <div class="bloco-imagem imagem-deco"><img src="assets/img/como-funciona-inspecao.jpg" alt="Carros num stand" width="651" height="428" loading="lazy"></div>
  </div>
</section>

<section class="seccao">
  <div class="contentor bloco">
    <div>
      <h2>Conclusão da venda</h2>
      <p>Após a verificação do veículo e a conclusão do acordo referente ao valor de transação, será pedida uma Certidão do veículo para verificar se o mesmo está apto para o processo de transferência de propriedade. Todo o processo será verificado e devidamente documentado (com cópias de todos os documentos)</p>
      <p><b>O pagamento será efectuado por transferência bancária</b>, sendo necessário o NIB (Número de Identificação Bancária) ou SPIN (Identificador para derivação de Conta). <b>O processo de transferência de registo de propriedade, será efectuado no máximo em 48H.</b></p>
      <p>Com este processo concluído evitamos todos os problemas que por vezes sucedem na venda a particulares (multas, portagens sem pagamento, IUC’s sem pagamento, etc)</p>
    </div>
    <div class="bloco-imagem imagem-deco esquerda"><img src="assets/img/como-funciona-conclusao.jpg" alt="Verificação de um carro antes da compra" width="651" height="428" loading="lazy"></div>
  </div>
</section>
"""
pagina("como-funciona.html", "Como Funciona - Compramos Carros",
       "Saiba como funciona a venda do seu carro ao Compramos Carros: proposta em 24 horas, critérios de avaliação, inspeção e conclusão da venda.",
       como, "como-funciona.html")

# ------------------------------------------------------------------ Quem somos
EQUIPA = [("francisco-matos", "Francisco Matos"), ("manuel-gama-barros", "Manuel Gama Barros"),
          ("bernardo-soares", "Bernardo Soares")]
equipa_html = "".join(
    f'<div class="membro"><img src="assets/img/equipa-{f}.jpg" alt="{n}" width="429" height="550" loading="lazy"><h3>{n}</h3></div>'
    for f, n in EQUIPA)
quem = f"""
<div class="titulo-pagina"><h1>Quem somos</h1></div>

<section class="seccao">
  <div class="contentor bloco">
    <div>
      <p class="boas-vindas">Bem-vindo ao Compramos Carros, uma marca desenvolvida pela MGB Automóveis.</p>
      <p>Nossa missão é oferecer um processo simples, rápido e transparente para si que deseja vender o seu carro!</p>
      {PECA.replace('class="acao"', 'class="acao" style="text-align:inherit"')}
    </div>
    <div class="bloco-imagem imagem-deco"><img src="assets/img/quem-somos.jpg" alt="Aperto de mão junto a um carro vermelho" width="651" height="428"></div>
  </div>
</section>

<section class="seccao">
  <div class="contentor">
    <h2 class="seccao-titulo">A equipa</h2>
    <p class="introducao"><b class="destaque-escuro">A nossa força reside na equipa dedicada e disponível!</b> Cada um de nós, com nossa experiência única e paixão pelo negócio, esforça-se para lhe proporcionar a experiência mais tranquila e confortável no processo de venda do seu carro.</p>
    <div class="equipa">{equipa_html}</div>
  </div>
</section>

<section class="seccao">
  <div class="contentor bloco inverso">
    <div>
      <h2>O que nos distingue</h2>
      <p>O que nos diferencia face à nossa concorrência, é a rapidez na formalização da oferta para o seu carro. Temos critérios de velocidade ambiciosos, e num prazo de 24 horas recebe a nossa oferta (durante o horário laboral, das 10h às 19h).</p>
      <p>Além disso, garantimos segurança em todo o processo. Todo o procedimento é acompanhado de documentos que comprovam e validam a transação. Para maior conforto, realizamos o pagamento por transferência bancária imediata.</p>
    </div>
    <div class="bloco-imagem imagem-deco"><img src="assets/img/quem-somos-distingue.jpg" alt="Aperto de mão junto a um carro azul" width="651" height="428" loading="lazy"></div>
  </div>
</section>
"""
pagina("quem-somos.html", "Quem Somos - Compramos Carros",
       "Bem-vindo ao Compramos Carros, uma marca desenvolvida pela MGB Automóveis. Um processo simples, rápido e transparente para vender o seu carro.",
       quem, "quem-somos.html")

# ------------------------------------------------------------------ Centro de entregas
MAPA = f"""<div class="mapa"><iframe src="{MAPA_EMBED}" title="Mapa — Stand Automóveis MGB, São Domingos de Rana" loading="lazy" referrerpolicy="no-referrer-when-downgrade" allowfullscreen></iframe></div>"""
centro = f"""
<div class="titulo-pagina"><h1>Centro de entregas</h1></div>

<section class="seccao">
  <div class="contentor">
    <p class="introducao">Bem-vindo ao Centro de Entrega, onde oferecemos um atendimento excepcional para garantir sua total satisfação.</p>
    <div class="infos">
      <div class="info"><img src="assets/img/icones/morada.png" alt="" width="64" height="64"><p><b>Stand Automóveis MGB</b>Estrada Nacional 249-4 Vivenda Garcia.<br>2785-574 S. Domingos de Rana</p></div>
      <div class="info"><img src="assets/img/icones/horario.png" alt="" width="64" height="64"><p><b>Seg a Sex das 9h às 19h. Sábado das 10h às 18h</b>Disponibilidade extra mediante marcação</p></div>
      <div class="info"><img src="assets/img/icones/telefone.png" alt="" width="64" height="64"><p><b><a href="tel:+351912263717" style="text-decoration:none">912 263 717</a></b>(Chamada para rede móvel nacional)</p></div>
    </div>
    {MAPA}
    <p class="mapa-ligacao">Para ver o mapa no google Maps <a href="{MAPA_LINK}" target="_blank" rel="noopener">clique aqui</a></p>
  </div>
</section>
"""
pagina("centro-de-entregas.html", "Centro de Entregas - Compramos Carros",
       "Centro de Entregas Compramos Carros: Stand Automóveis MGB, Estrada Nacional 249-4, São Domingos de Rana. Seg a Sex das 9h às 19h, Sábado das 10h às 18h.",
       centro, "centro-de-entregas.html")

# ------------------------------------------------------------------ Contactos
contactos = f"""
<div class="titulo-pagina"><h1>Contactos</h1></div>

<section class="seccao">
  <div class="contentor">
    <h2 class="seccao-titulo">Fale connosco</h2>
    <p class="introducao">A nossa equipa está aqui para o ajudar. Entre em contacto connosco e iremos atender o seu pedido o mais brevemente possível.</p>

    <div class="contactos-grelha">
      <form class="cartao-formulario" data-formulario data-assunto="Contacto através do site">
        <input class="armadilha" type="text" name="_gotcha" tabindex="-1" autocomplete="off" aria-hidden="true">
        {campo("user", entrada("nome", "Nome", extra=' autocomplete="name"'))}
        {campo("phone", entrada("telefone", "Telefone", "tel", ' autocomplete="tel" inputmode="tel"'))}
        {campo("mail", entrada("email", "E-mail", "email", ' autocomplete="email"'))}
        <div class="campo vertical"><label for="mensagem">Mensagem</label><textarea id="mensagem" name="mensagem" aria-label="Mensagem" required></textarea></div>
        {AVISO_DADOS}
        <div class="formulario-acao"><button class="botao" type="submit">Enviar</button></div>
        <div class="mensagem-form" role="status"></div>
      </form>

      <div>
        {MAPA}
        <ul class="lista-contactos">
          <li>{I["pin"]}<span><b>Stand Automóveis MGB</b><br>Estrada Nacional 249-4 Vivenda Garcia<br>2785-574. São Domingos de Rana</span></li>
          <li><span style="color:var(--verde);display:flex">{I["whats"].replace('aria-hidden="true"', 'aria-hidden="true" style="width:22px;height:22px"')}</span><a href="https://wa.me/351912263717" target="_blank" rel="noopener">912 263 717</a></li>
          <li>{I["phone"]}<a href="tel:+351912263717">912 263 717</a></li>
          <li>{I["mail"]}<a href="mailto:comercial@compramos-carros.com">comercial@compramos-carros.com</a></li>
        </ul>
      </div>
    </div>
  </div>
</section>
"""
pagina("contactos.html", "Contactos - Compramos Carros",
       "Fale connosco. A equipa Compramos Carros está aqui para o ajudar: 912 263 717, Stand Automóveis MGB, São Domingos de Rana.",
       contactos, "contactos.html")

# ------------------------------------------------------------------ Política de privacidade
privacidade = """
<div class="titulo-pagina"><h1>Política de privacidade</h1></div>

<section class="seccao">
  <div class="contentor legal">
    <p><b class="destaque-escuro">Termos e Condições | Política de Privacidade | Informação sobre Protecção de Dados</b></p>

    <h2>Quem somos?</h2>
    <p>Cumprindo o REGULAMENTO (UE) 2016/679 DO PARLAMENTO EUROPEU E DO CONSELHO de 27 de abril de 2016 relativo à proteção das pessoas singulares no que diz respeito ao tratamento de dados pessoais e à livre circulação desses dados, informamos que a ADSALES LDA é uma Sociedade Limitada, com sede na Rua António Gomes Soares Pereira, n.º 88, 4470-139 Maia, Portugal, registada na Conservatória do Registo Comercial, sob o número único de matrícula e pessoa colectiva 509036228 doravante designada por "OXY", que actua na área do marketing digital.</p>

    <h2>Quem é o responsável pelo tratamento de dados?</h2>
    <p>As entidades Responsáveis pelo Tratamento dos dados pessoais são a OXY e os seus Clientes, neste caso específico a Barros Matos e Soares Automóveis Lda. Ambos decidem quais os dados recolhidos, os meios de tratamento dos dados e as finalidades para que são utilizados. A OXY é contratada pela Barros Matos e Soares Automóveis Lda., fazendo a recolha e tratamento dos mesmos apenas de acordo com as instruções destes.</p>

    <h2>Porquê uma política de privacidade?</h2>
    <p>Porque a OXY e a Barros Matos e Soares Automóveis Lda. estão empenhados em proteger a privacidade dos seus Utilizadores, e neste contexto, elaboraram a presente Política de Privacidade com a finalidade de demonstrar o seu compromisso e respeito para com as regras de privacidade e de protecção de dados pessoais. Caso não concorde com a nossa Política de Privacidade, não deverá avançar com o preenchimento do formulário.</p>

    <h2>O que é abrangido por esta política de privacidade?</h2>
    <p>Esta Política de Privacidade aplica-se exclusivamente à recolha e tratamento de dados pessoais efectuados pela OXY e pela Barros Matos e Soares Automóveis Lda. no âmbito da sua actividade.</p>

    <h2>Titularidade dos dados</h2>
    <p>Ao registar os seus dados, o registado declara ser o Titular legal destes dados e ser maior de 18 anos.</p>

    <h2>Que tipo de dados pessoais são recolhidos e como os recolhemos?</h2>
    <p>A OXY e a Barros Matos e Soares Automóveis Lda. recolhem dados pessoais que são sempre fornecidos pelo Utilizador quando preenche os respectivos formulários. Os dados recolhidos são os adequados, pertinentes e não excessivos em relação ao âmbito, finalidades e serviços determinados, explícitos e legítimos da OXY e da Barros Matos e Soares Automóveis Lda. Neste caso, os dados recolhidos são os que constam neste site: Nome e apelido, email, telefone, mensagem, kilómetros, matrícula, ano, mês, marca, modelo, versão e transmissão do carro.</p>

    <h2>Para que são utilizados os dados?</h2>
    <p>Os dados fornecidos pelo Utilizador serão utilizados pela Barros Matos e Soares Automóveis Lda. para contacto telefónico com a finalidade de fornecer mais informação sobre os seus produtos e serviços. Posteriormente, poderão ser utilizados pela mesma Barros Matos e Soares Automóveis Lda., para enviar informação sobre estes ou outros produtos e serviços via email, telefone ou via sms.</p>

    <h2>Por quanto tempo vamos conservar esses dados?</h2>
    <p>Os dados serão conservados até que o utilizador pretenda proceder à eliminação dos mesmos.</p>

    <h2>Como exercer os seus direitos?</h2>
    <p>O Utilizador poderá exercer os seus direitos de acesso, rectificação, limitação ao tratamento, oposição, portabilidade e apagamento dos seus dados pessoais. O exercício deste direito poderá ser feito através de email para o seguinte endereço: <a href="mailto:dpo@oxy.agency">dpo@oxy.agency</a>.</p>
    <p>Poderá ainda apresentar uma queixa junto da Comissão Nacional de Proteção de Dados em <a href="http://www.cnpd.pt/" target="_blank" rel="noopener">http://www.cnpd.pt/</a></p>

    <h2>Como é assegurada a segurança dos seus dados pessoais?</h2>
    <p>Os dados pessoais disponibilizados pelos Utilizadores serão incorporados num ficheiro automatizado nos termos e condições estabelecidos na já referida Lei 2016/679, de 27 de Abril. A OXY e a Barros Matos e Soares Automóveis Lda. respeitam as melhores práticas no domínio da segurança e da protecção dos dados pessoais, tendo para o efeito um sistema que garante a segurança, a confidencialidade dos seus dados pessoais bem como a privacidade das comunicações electrónicas.</p>
    <p>A política de segurança de recolha e armazenamento de dados da OXY e da Barros Matos e Soares Automóveis Lda. prevê, além de outros aspectos, um elevado investimento em infraestruturas tecnológicas que impedem o acesso aos dados pessoais por pessoas não autorizadas. São tomadas todas as medidas de segurança que a OXY e a Barros Matos e Soares Automóveis Lda. entendem serem indispensáveis à protecção dos seus dados pessoais. Contudo, a OXY e a Barros Matos e Soares Automóveis Lda. alertam os Utilizadores para a necesidade de adoptarem medidas adicionais de segurança, designadamente o assegurarem–se que utilizam um browser actualizado em termos de patches de segurança adequadamente configurados, com firewall activa, antivírus e anti-spyware e certificarem-se da autenticidade dos sites que visitam na internet, devendo evitar sites em cuja reputação não confiem.</p>

    <h2>Protecção de spamming</h2>
    <p>O spamming consiste no envio indiferenciado de e-mails a desconhecidos. A OXY garante que não utilizará os dados recolhidos neste página para nenhum outro fim que não o do seu cliente Barros Matos e Soares Automóveis Lda.</p>
  </div>
</section>
"""
pagina("politica-de-privacidade.html", "Política de Privacidade - Compramos Carros",
       "Política de Privacidade e informação sobre proteção de dados do site Compramos Carros.",
       privacidade)

# ------------------------------------------------------------------ Política de cookies
COOKIES = [
 ("Cookies próprios", "são aqueles que são enviados para o equipamento terminal do utilizador a partir de um computador ou domínio gerido pelo próprio editor e do qual fornece o serviço solicitado pelo utilizador."),
 ("Cookies de terceiros", "Os que são enviados para o equipamento terminal do utilizador a partir de um computador ou domínio que não é gerido pelo editor, mas por outra entidade que trata os dados obtidos por meio de cookies."),
 ("Cookies de sessão", "São um tipo de cookies projectados para angariar e armazenar dados enquanto o utilizador acede a uma página web."),
 ("Cookies persistentes", "São um tipo de cookies em que os dados permanecem armazenados no terminal e podem ser acedidos e tratados durante um período definido pelo responsável do cookie, e que pode variar de alguns minutos a vários anos."),
 ("Cookies técnicos", "São aqueles que permitem ao utilizador a navegação através de site, plataforma ou aplicação e a utilização das diferentes opções ou serviços que nele existam como por exemplo, controlar o tráfego e a comunicação de dados, identificar a sessão, aceder a áreas restritas, recordar os elementos que integram um pedido, realizar o processo de compra de um pedido, realizar a solicitação de inscrição ou participação num evento, utilizar recursos de segurança enquanto navega, armazenar conteúdos para a difusão de vídeos ou sons ou compartilhar conteúdos através de redes sociais."),
 ("Cookies de personalização", "São aqueles que permitem ao utilizador aceder ao serviço com algumas características de carácter geral predefinidas com base numa série de critérios no terminal do utilizador como por exemplo o idioma, tipo de browser através do qual acede ao serviço, a configuração regional de onde acede o serviço, etc."),
 ("Cookies de análise", "São aqueles que permitem aos seus responsáveis acompanhar e analisar o comportamento dos utilizadores dos sites aos quais estejam vinculados. A informação recolhida através de tais cookies é usada para medir a actividade dos sites, aplicativos ou plataformas e para a criação de perfis de navegação dos utilizadores desses sites, aplicativos e plataformas, a fim de realizar melhorias em base na análise dos dados de uso feito pelos utilizadores do serviço."),
 ("Cookies publicitárias", "São aqueles que permitem a gestão, da forma mais eficaz possível, dos espaços publicitários que, o editor haja incluído num site, aplicativo ou plataforma de onde presta o serviço solicitado com base em critérios como o conteúdo editado ou a frequência em que os anúncios são exibidos."),
 ("Cookies de publicidade comportamental", "São aqueles que armazenam informações sobre o comportamento do utilizador obtido através da observação contínua de seus hábitos de navegação, permitindo desenvolver um perfil específico para exibir anúncios com base no mesmo."),
]
cookies = f"""
<div class="titulo-pagina"><h1>Política de cookies</h1></div>

<section class="seccao">
  <div class="contentor legal">
    <h2>Como usamos os cookies?</h2>
    <p>Um cookie é um arquivo que é instalado no computador quando se acede a determinadas páginas na Internet. Os Cookies que utilizamos são os seguintes:</p>
    <ul>{"".join(f"<li><b>{t}:</b> {d}</li>" for t, d in COOKIES)}</ul>
  </div>
</section>
"""
pagina("politica-de-cookies.html", "Política de Cookies - Compramos Carros",
       "Política de Cookies do site Compramos Carros.", cookies)

# ------------------------------------------------------------------ 404
erro = """
<div class="titulo-pagina"><h1>Página não encontrada</h1></div>
<section class="seccao"><div class="contentor centro">
  <p class="introducao">A página que procura não existe ou foi movida.</p>
  <p class="acao"><a class="botao" href="index.html">Voltar à página inicial</a></p>
</div></section>
"""
pagina("404.html", "Página não encontrada - Compramos Carros", "Página não encontrada.", erro)
# Num 404 servido noutro caminho, os endereços relativos falham: usar absolutos.
p = OUT / "404.html"
s = p.read_text(encoding="utf-8")
for a in ['href="', 'src="']:
    for alvo in ["assets/", "index.html", "como-funciona", "quem-somos", "centro-de", "contactos", "politica-de", "favicon"]:
        s = s.replace(a + alvo, a + "/" + alvo)
p.write_text(s, encoding="utf-8")

# ------------------------------------------------------------------ SEO / alojamento
paginas = ["", "como-funciona.html", "quem-somos.html", "centro-de-entregas.html", "contactos.html",
           "politica-de-privacidade.html", "politica-de-cookies.html"]
(OUT / "sitemap.xml").write_text(
    '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + "".join(f"  <url><loc>{DOMINIO}/{p}</loc></url>\n" for p in paginas) + "</urlset>\n", encoding="utf-8")
(OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {DOMINIO}/sitemap.xml\n", encoding="utf-8")
(OUT / "CNAME").write_text("compramoscarros.pt\n", encoding="utf-8")
print("ok")
