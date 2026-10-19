(function () {
  "use strict";

  var CFG = window.CC_CONFIG || {};

  // ---------- Menu móvel ----------
  var botaoMenu = document.querySelector(".menu-botao");
  var navegacao = document.querySelector(".navegacao");
  if (botaoMenu && navegacao) {
    botaoMenu.addEventListener("click", function () {
      var aberta = navegacao.classList.toggle("aberta");
      botaoMenu.setAttribute("aria-expanded", aberta ? "true" : "false");
    });
  }

  // ---------- Ano no rodapé ----------
  Array.prototype.forEach.call(document.querySelectorAll("[data-ano]"), function (el) {
    el.textContent = new Date().getFullYear();
  });

  // ---------- Aviso de cookies ----------
  var cookies = document.querySelector(".cookies");
  if (cookies) {
    var aceite = false;
    try { aceite = localStorage.getItem("cc_cookies") === "1"; } catch (e) {}
    if (!aceite) cookies.classList.add("visivel");
    cookies.querySelector("button").addEventListener("click", function () {
      try { localStorage.setItem("cc_cookies", "1"); } catch (e) {}
      cookies.classList.remove("visivel");
    });
  }

  // ---------- Listas do formulário de avaliação ----------
  var DISTRITOS = ["Aveiro", "Beja", "Braga", "Bragança", "Castelo Branco", "Coimbra", "Évora", "Faro",
    "Guarda", "Leiria", "Lisboa", "Portalegre", "Porto", "Santarém", "Setúbal", "Viana do Castelo",
    "Vila Real", "Viseu", "Região Autónoma dos Açores", "Região Autónoma da Madeira"];

  var MESES = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto",
    "Setembro", "Outubro", "Novembro", "Dezembro"];

  var MARCAS = {
    "Abarth": ["500", "595", "695", "124 Spider", "Outro"],
    "Alfa Romeo": ["Giulietta", "Giulia", "Stelvio", "Tonale", "MiTo", "159", "Outro"],
    "Audi": ["A1", "A3", "A4", "A5", "A6", "A7", "A8", "Q2", "Q3", "Q4 e-tron", "Q5", "Q7", "Q8", "e-tron", "TT", "Outro"],
    "BMW": ["Série 1", "Série 2", "Série 3", "Série 4", "Série 5", "Série 6", "Série 7", "X1", "X2", "X3", "X4", "X5", "X6", "X7", "i3", "i4", "iX", "iX1", "iX3", "Z4", "Outro"],
    "BYD": ["Atto 3", "Dolphin", "Seal", "Seal U", "Han", "Tang", "Outro"],
    "Citroën": ["C1", "C3", "C3 Aircross", "C4", "C4 Cactus", "C4 Picasso", "C5", "C5 Aircross", "C5 X", "Berlingo", "Jumpy", "Outro"],
    "Cupra": ["Born", "Formentor", "Leon", "Ateca", "Outro"],
    "Dacia": ["Sandero", "Logan", "Duster", "Jogger", "Spring", "Lodgy", "Dokker", "Outro"],
    "DS": ["DS 3", "DS 4", "DS 7", "DS 9", "Outro"],
    "Fiat": ["500", "500X", "500L", "Panda", "Tipo", "Punto", "Doblò", "Outro"],
    "Ford": ["Fiesta", "Focus", "Puma", "Kuga", "Mondeo", "EcoSport", "C-Max", "S-Max", "Galaxy", "Mustang", "Mustang Mach-E", "Ranger", "Transit", "Outro"],
    "Honda": ["Jazz", "Civic", "HR-V", "CR-V", "ZR-V", "e", "Outro"],
    "Hyundai": ["i10", "i20", "i30", "Bayon", "Kona", "Tucson", "Santa Fe", "IONIQ", "IONIQ 5", "IONIQ 6", "Outro"],
    "Jaguar": ["XE", "XF", "E-Pace", "F-Pace", "I-Pace", "Outro"],
    "Jeep": ["Renegade", "Compass", "Avenger", "Wrangler", "Grand Cherokee", "Outro"],
    "Kia": ["Picanto", "Rio", "Stonic", "Ceed", "XCeed", "Niro", "Sportage", "Sorento", "EV6", "Outro"],
    "Land Rover": ["Defender", "Discovery", "Discovery Sport", "Range Rover", "Range Rover Evoque", "Range Rover Sport", "Range Rover Velar", "Outro"],
    "Lexus": ["CT", "UX", "NX", "RX", "ES", "IS", "Outro"],
    "Mazda": ["Mazda2", "Mazda3", "Mazda6", "CX-3", "CX-30", "CX-5", "CX-60", "MX-5", "Outro"],
    "Mercedes-Benz": ["Classe A", "Classe B", "Classe C", "Classe E", "Classe S", "CLA", "CLS", "GLA", "GLB", "GLC", "GLE", "GLS", "EQA", "EQB", "EQC", "Vito", "Sprinter", "Outro"],
    "MG": ["MG4", "MG5", "ZS", "HS", "Marvel R", "Outro"],
    "Mini": ["One", "Cooper", "Cooper S", "Clubman", "Countryman", "Cabrio", "Outro"],
    "Mitsubishi": ["Space Star", "ASX", "Eclipse Cross", "Outlander", "L200", "Outro"],
    "Nissan": ["Micra", "Juke", "Qashqai", "X-Trail", "Leaf", "Ariya", "Navara", "Outro"],
    "Opel": ["Corsa", "Astra", "Insignia", "Mokka", "Crossland", "Grandland", "Zafira", "Combo", "Outro"],
    "Peugeot": ["108", "208", "2008", "308", "3008", "408", "508", "5008", "Partner", "Rifter", "Expert", "Outro"],
    "Polestar": ["2", "3", "4", "Outro"],
    "Porsche": ["911", "718", "Macan", "Cayenne", "Panamera", "Taycan", "Outro"],
    "Renault": ["Twingo", "Clio", "Captur", "Mégane", "Arkana", "Austral", "Kadjar", "Scénic", "Espace", "Zoe", "Kangoo", "Trafic", "Outro"],
    "Seat": ["Ibiza", "Leon", "Arona", "Ateca", "Tarraco", "Mii", "Alhambra", "Outro"],
    "Skoda": ["Fabia", "Scala", "Octavia", "Superb", "Kamiq", "Karoq", "Kodiaq", "Enyaq", "Outro"],
    "Smart": ["fortwo", "forfour", "#1", "Outro"],
    "Suzuki": ["Ignis", "Swift", "Vitara", "S-Cross", "Jimny", "Outro"],
    "Tesla": ["Model 3", "Model Y", "Model S", "Model X", "Outro"],
    "Toyota": ["Aygo", "Aygo X", "Yaris", "Yaris Cross", "Corolla", "C-HR", "RAV4", "Prius", "Auris", "Land Cruiser", "Hilux", "Proace", "Outro"],
    "Volkswagen": ["up!", "Polo", "Golf", "T-Cross", "T-Roc", "Taigo", "Tiguan", "Touran", "Passat", "Arteon", "ID.3", "ID.4", "ID.5", "Touareg", "Caddy", "Transporter", "Outro"],
    "Volvo": ["V40", "V60", "V90", "S60", "S90", "XC40", "XC60", "XC90", "EX30", "Outro"],
    "Outra": ["Outro"]
  };

  function preencher(select, valores) {
    var primeira = select.querySelector("option[value='']");
    select.innerHTML = "";
    if (primeira) select.appendChild(primeira);
    valores.forEach(function (v) {
      var o = document.createElement("option");
      o.value = String(v);
      o.textContent = String(v);
      select.appendChild(o);
    });
  }

  var sel = function (nome) { return document.querySelector("[data-lista='" + nome + "']"); };

  if (sel("distrito")) preencher(sel("distrito"), DISTRITOS);
  if (sel("mes")) preencher(sel("mes"), MESES);
  if (sel("ano")) {
    var anos = [];
    for (var a = new Date().getFullYear(); a >= 1990; a--) anos.push(a);
    preencher(sel("ano"), anos);
  }
  if (sel("marca") && sel("modelo")) {
    var marca = sel("marca"), modelo = sel("modelo");
    preencher(marca, Object.keys(MARCAS));
    marca.addEventListener("change", function () {
      preencher(modelo, MARCAS[marca.value] || []);
      modelo.value = "";
    });
  }

  // A matrícula é guardada em maiúsculas (AA-00-AA)
  var matricula = document.querySelector("input[name='matricula']");
  if (matricula) {
    matricula.addEventListener("input", function () { matricula.value = matricula.value.toUpperCase(); });
  }

  // ---------- Envio dos formulários ----------
  function resumo(form) {
    var linhas = [form.getAttribute("data-assunto") || "Pedido através do site"];
    Array.prototype.forEach.call(form.elements, function (el) {
      if (!el.name || el.name === "_gotcha" || el.type === "submit" || !el.value) return;
      var rotulo = el.getAttribute("aria-label") || el.name;
      linhas.push(rotulo + ": " + el.value);
    });
    return linhas.join("\n");
  }

  function mostrar(form, tipo, texto) {
    var caixa = form.querySelector(".mensagem-form");
    caixa.className = "mensagem-form " + tipo;
    caixa.textContent = texto;
  }

  Array.prototype.forEach.call(document.querySelectorAll("form[data-formulario]"), function (form) {
    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      if (form.elements._gotcha && form.elements._gotcha.value) return;

      var botao = form.querySelector("button[type='submit']");

      if (!CFG.formEndpoint) {
        var url = "https://wa.me/" + CFG.whatsapp + "?text=" + encodeURIComponent(resumo(form));
        window.open(url, "_blank", "noopener");
        mostrar(form, "sucesso", "Abrimos o WhatsApp com o seu pedido. Basta carregar em enviar para concluir.");
        return;
      }

      botao.disabled = true;
      var dados = new FormData(form);
      dados.append("_subject", form.getAttribute("data-assunto") || "Pedido através do site");
      fetch(CFG.formEndpoint, { method: "POST", body: dados, headers: { Accept: "application/json" } })
        .then(function (r) {
          if (!r.ok) throw new Error(r.status);
          form.reset();
          mostrar(form, "sucesso", "Obrigado! Recebemos o seu pedido e entraremos em contacto o mais brevemente possível.");
        })
        .catch(function () {
          mostrar(form, "erro", "Não foi possível enviar o pedido. Por favor ligue-nos para o " + CFG.telefone + " ou contacte-nos por WhatsApp.");
        })
        .then(function () { botao.disabled = false; });
    });
  });
})();
