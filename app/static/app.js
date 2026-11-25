// Agenda de Treinos — front simples consumindo a API FastAPI.

const $ = (sel) => document.querySelector(sel);
let treinos = [];
let treinoAtual = null; // treino sendo editado nos modais

// ---------- chamadas à API ----------

async function api(metodo, url, corpo) {
  const r = await fetch(url, {
    method: metodo,
    headers: corpo ? { "Content-Type": "application/json" } : {},
    body: corpo ? JSON.stringify(corpo) : undefined,
  });
  if (r.status === 204) return null;
  const dados = await r.json();
  if (!r.ok) {
    const msg = Array.isArray(dados.detail) ? dados.detail.map((d) => d.msg).join("; ") : dados.detail;
    throw new Error(msg || `Erro ${r.status}`);
  }
  return dados;
}

function toast(msg) {
  const el = document.createElement("div");
  el.className = "toast";
  el.textContent = msg;
  document.body.appendChild(el);
  setTimeout(() => el.remove(), 2500);
}

async function executar(acao, sucesso) {
  try {
    await acao();
    if (sucesso) toast(sucesso);
    await carregar();
  } catch (e) {
    alert(e.message);
  }
}

// ---------- listagem ----------

async function carregar() {
  const el = $("#lista");
  if (location.protocol === "file:") {
    el.textContent = "Abra pelo servidor: http://127.0.0.1:8000 (rode o uvicorn dentro da pasta agenda-treinos).";
    return;
  }
  try {
    treinos = await api("GET", "/treinos");
  } catch (e) {
    el.textContent = "Erro: " + e.message;
    return;
  }
  el.innerHTML = "";
  if (!treinos.length) {
    el.innerHTML = '<p class="vazio">Nenhum treino agendado. Clique em "+ Novo treino".</p>';
    return;
  }

  let diaAnterior = "";
  for (const t of treinos) {
    const data = new Date(t.data_hora);
    const dia = data.toLocaleDateString("pt-BR", { weekday: "long", day: "2-digit", month: "long" });
    if (dia !== diaAnterior) {
      const h = document.createElement("div");
      h.className = "dia";
      h.textContent = dia;
      el.appendChild(h);
      diaAnterior = dia;
    }
    el.appendChild(cartao(t, data));
  }
}

function cartao(t, data) {
  const div = document.createElement("div");
  div.className = `treino ${t.modalidade}`;
  div.innerHTML = `
    <div class="meta"></div>
    <h3></h3>
    <p></p>
    <div class="pessoas"></div>
    <div class="acoes">
      <button data-acao="editar">Editar título/descrição</button>
      <button data-acao="pessoas">Alterar participantes</button>
      <button data-acao="excluir" class="perigo">Excluir treino</button>
    </div>`;
  const hora = data.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });
  const duracao = t.duracao_prevista_min ? ` · ${t.duracao_prevista_min} min` : "";
  div.querySelector(".meta").textContent = `${hora} · ${t.modalidade}${duracao}`;
  div.querySelector("h3").textContent = t.titulo;
  div.querySelector("p").textContent = t.descricao;

  const pessoas = div.querySelector(".pessoas");
  for (const p of t.participantes) {
    const chip = document.createElement("span");
    chip.className = `chip ${p.papel}`;
    chip.textContent = `${p.nome} (${p.papel})`;
    const x = document.createElement("button");
    x.className = "mini";
    x.title = `Remover ${p.nome}`;
    x.textContent = "×";
    x.onclick = () => {
      if (confirm(`Remover ${p.nome} deste treino?`))
        executar(() => api("DELETE", `/treinos/${t.id}/participantes/${p.id}`), `${p.nome} removido(a)`);
    };
    chip.appendChild(x);
    pessoas.appendChild(chip);
  }

  div.querySelector('[data-acao="editar"]').onclick = () => abrirEditar(t);
  div.querySelector('[data-acao="pessoas"]').onclick = () => abrirPessoas(t);
  div.querySelector('[data-acao="excluir"]').onclick = () => {
    if (confirm(`Excluir o treino "${t.titulo}"?`))
      executar(() => api("DELETE", `/treinos/${t.id}`), "Treino excluído");
  };
  return div;
}

// ---------- linhas de participante (usadas em dois modais) ----------

function linhaPessoa(container, pessoa = { nome: "", papel: "atleta" }) {
  const linha = document.createElement("div");
  linha.className = "pessoa-linha";
  linha.innerHTML = `
    <input placeholder="Nome">
    <select><option value="atleta">Atleta</option><option value="treinador">Treinador</option></select>
    <button type="button" class="mini" title="Remover linha">×</button>`;
  linha.querySelector("input").value = pessoa.nome;
  linha.querySelector("select").value = pessoa.papel;
  linha.querySelector("button").onclick = () => linha.remove();
  container.appendChild(linha);
}

function lerPessoas(container) {
  return [...container.querySelectorAll(".pessoa-linha")]
    .map((l) => ({ nome: l.querySelector("input").value.trim(), papel: l.querySelector("select").value }))
    .filter((p) => p.nome);
}

// ---------- modal: novo treino ----------

$("#btn-novo").onclick = () => {
  const form = $("#form-novo");
  form.reset();
  $("#novo-participantes").innerHTML = "";
  linhaPessoa($("#novo-participantes"));
  $("#dlg-novo").showModal();
};
$("#btn-add-linha").onclick = () => linhaPessoa($("#novo-participantes"));

$("#form-novo").onsubmit = (ev) => {
  ev.preventDefault();
  const f = new FormData(ev.target);
  const corpo = {
    data_hora: f.get("data_hora"),
    titulo: f.get("titulo").trim(),
    descricao: f.get("descricao").trim(),
    modalidade: f.get("modalidade"),
    participantes: lerPessoas($("#novo-participantes")),
  };
  if (f.get("duracao_prevista_min")) corpo.duracao_prevista_min = Number(f.get("duracao_prevista_min"));
  executar(async () => {
    await api("POST", "/treinos", corpo);
    $("#dlg-novo").close();
  }, "Treino cadastrado");
};

// ---------- modal: editar título/descrição ----------

function abrirEditar(t) {
  treinoAtual = t;
  const form = $("#form-editar");
  form.titulo.value = t.titulo;
  form.descricao.value = t.descricao;
  $("#dlg-editar").showModal();
}

$("#form-editar").onsubmit = (ev) => {
  ev.preventDefault();
  const form = ev.target;
  executar(async () => {
    await api("PATCH", `/treinos/${treinoAtual.id}`, {
      titulo: form.titulo.value.trim(),
      descricao: form.descricao.value.trim(),
    });
    $("#dlg-editar").close();
  }, "Treino atualizado");
};

// ---------- modal: alterar participantes ----------

function abrirPessoas(t) {
  treinoAtual = t;
  const c = $("#pessoas-linhas");
  c.innerHTML = "";
  t.participantes.forEach((p) => linhaPessoa(c, p));
  if (!t.participantes.length) linhaPessoa(c);
  $("#dlg-pessoas").showModal();
}
$("#btn-add-pessoa").onclick = () => linhaPessoa($("#pessoas-linhas"));

$("#form-pessoas").onsubmit = (ev) => {
  ev.preventDefault();
  executar(async () => {
    await api("PUT", `/treinos/${treinoAtual.id}/participantes`, lerPessoas($("#pessoas-linhas")));
    $("#dlg-pessoas").close();
  }, "Participantes atualizados");
};

// botões "Cancelar"
document.querySelectorAll("[data-fechar]").forEach((b) => (b.onclick = () => b.closest("dialog").close()));

carregar();
