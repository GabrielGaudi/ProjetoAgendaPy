#!/usr/bin/env python3
"""
Agenda de Contatos — Interface Web
===================================
Porta a agenda CLI para um servidor web usando APENAS a biblioteca padrão do
Python (http.server), sem dependências externas.

Conceitos web2py/MVC presentes neste arquivo:
  • Model   — lista `agenda` + persistência CSV  (estrutura original mantida)
  • View    — funções html_*() que geram o HTML de cada página
  • Controller — classe AgendaHandler que roteia URLs e processa formulários

Inicialização:
  1. Escolhe uma porta ALEATÓRIA no intervalo 18 000–28 000.
  2. Testa se a porta está livre antes de usá-la.
  3. Repete até encontrar uma porta disponível.
  4. Exibe no console a URL de acesso (local e rede).

Uso:
  python agenda_web.py
"""

import os
import re
import csv
import socket
import random
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse, unquote_plus, quote_plus


# ═══════════════════════════════════════════════════════════════════════════════
#  MODEL — Configurações e estrutura de dados (idênticos ao programa original)
# ═══════════════════════════════════════════════════════════════════════════════

CAPACIDADE  = 100
ARQUIVO_CSV = "agenda_web.csv"
CAMPOS_CSV  = ["id", "nome", "email", "telefone", "cep"]

agenda: list[dict] = []          # mesma estrutura do programa original


# ── Validações ────────────────────────────────────────────────────────────────

RE_EMAIL    = re.compile(r"^[\w\.\+\-]+@[\w\-]+\.[a-z]{2,}$", re.I)
RE_TELEFONE = re.compile(r"^[\d\s\(\)\-\+]{7,20}$")

def validar_email(email: str) -> bool:
    return bool(RE_EMAIL.match(email.strip()))

def validar_telefone(tel: str) -> bool:
    return bool(RE_TELEFONE.match(tel.strip()))


# ── Helpers de contato ────────────────────────────────────────────────────────

def proximo_id() -> int:
    return max((c["id"] for c in agenda), default=0) + 1

def buscar_por_id(cid: int) -> dict | None:
    for c in agenda:
        if c["id"] == cid:
            return c
    return None


# ── Persistência CSV ──────────────────────────────────────────────────────────

def salvar_csv() -> None:
    """Regrava o arquivo CSV com o estado atual da lista."""
    with open(ARQUIVO_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CAMPOS_CSV)
        writer.writeheader()
        writer.writerows(agenda)

def carregar_csv() -> bool:
    """Carrega contatos do CSV para a lista. Retorna True se o arquivo existia."""
    if not os.path.exists(ARQUIVO_CSV):
        return False
    with open(ARQUIVO_CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            agenda.append({
                "id":       int(row["id"]),
                "nome":     row["nome"],
                "email":    row["email"],
                "telefone": row["telefone"],
            })
    return True

def carregar_demo() -> None:
    """Dados de exemplo para a primeira execução."""
    demos = [
        {"id": 1, "nome": "Ana Silva",    "email": "ana@email.com",   "telefone": "(11) 91234-5678"},
        {"id": 2, "nome": "Bruno Costa",  "email": "bruno@email.com", "telefone": "(21) 98765-4321"},
        {"id": 3, "nome": "Carla Mendes", "email": "carla@email.com", "telefone": "(31) 97654-3210"},
    ]
    agenda.extend(demos)


# ═══════════════════════════════════════════════════════════════════════════════
#  VIEW — Templates HTML (geração de páginas)
# ═══════════════════════════════════════════════════════════════════════════════

# ── CSS global ────────────────────────────────────────────────────────────────
_CSS = """
<style>
  @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@400;600&display=swap');

  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --bg:       #f0f2f5;
    --card:     #ffffff;
    --primary:  #1a56db;
    --danger:   #c81e1e;
    --success:  #057a55;
    --text:     #111827;
    --muted:    #6b7280;
    --border:   #d1d5db;
    --accent:   #e0e7ff;
    --radius:   6px;
    --font:     'IBM Plex Sans', sans-serif;
    --mono:     'IBM Plex Mono', monospace;
  }

  body {
    font-family: var(--font);
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
  }

  /* ── Cabeçalho ── */
  header {
    background: var(--primary);
    color: #fff;
    padding: 16px 32px;
    display: flex;
    align-items: center;
    gap: 12px;
  }
  header h1 { font-size: 1.25rem; font-weight: 600; letter-spacing: .02em; }
  header .badge {
    font-family: var(--mono);
    font-size: .72rem;
    background: rgba(255,255,255,.2);
    padding: 2px 8px;
    border-radius: 99px;
  }

  /* ── Navegação ── */
  nav {
    background: var(--card);
    border-bottom: 1px solid var(--border);
    padding: 0 32px;
    display: flex;
    gap: 4px;
  }
  nav a {
    display: inline-block;
    padding: 12px 16px;
    font-size: .875rem;
    font-weight: 600;
    color: var(--muted);
    text-decoration: none;
    border-bottom: 3px solid transparent;
  }
  nav a:hover  { color: var(--primary); }
  nav a.active { color: var(--primary); border-bottom-color: var(--primary); }

  /* ── Conteúdo principal ── */
  main { padding: 32px; max-width: 960px; margin: 0 auto; }

  h2 { font-size: 1.125rem; font-weight: 600; margin-bottom: 20px; }

  /* ── Mensagens ── */
  .msg {
    padding: 10px 16px;
    border-radius: var(--radius);
    font-size: .875rem;
    margin-bottom: 20px;
  }
  .msg-ok  { background: #d1fae5; color: #065f46; border: 1px solid #a7f3d0; }
  .msg-err { background: #fee2e2; color: #991b1b; border: 1px solid #fecaca; }

  /* ── Tabela ── */
  .table-wrap { overflow-x: auto; background: var(--card); border-radius: var(--radius); border: 1px solid var(--border); }
  table { width: 100%; border-collapse: collapse; font-size: .875rem; }
  thead th {
    background: #f9fafb;
    padding: 11px 16px;
    text-align: left;
    font-size: .75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: .06em;
    color: var(--muted);
    border-bottom: 1px solid var(--border);
  }
  tbody td { padding: 11px 16px; border-bottom: 1px solid var(--border); }
  tbody tr:last-child td { border-bottom: none; }
  tbody tr:hover { background: #f9fafb; }
  .empty-row td { text-align: center; color: var(--muted); padding: 32px; }

  .id-cell { font-family: var(--mono); color: var(--muted); font-size: .8rem; }
  .actions { white-space: nowrap; }

  /* ── Botões ── */
  .btn {
    display: inline-block;
    padding: 7px 16px;
    border-radius: var(--radius);
    font-size: .8125rem;
    font-weight: 600;
    text-decoration: none;
    cursor: pointer;
    border: 1px solid transparent;
    font-family: var(--font);
  }
  .btn-primary   { background: var(--primary); color: #fff; }
  .btn-primary:hover { background: #1e429f; }
  .btn-danger    { background: var(--danger);  color: #fff; }
  .btn-danger:hover  { background: #9b1c1c; }
  .btn-secondary { background: var(--card); color: var(--text); border-color: var(--border); }
  .btn-secondary:hover { background: var(--bg); }
  .btn-sm { padding: 4px 10px; font-size: .75rem; }

  /* ── Formulário ── */
  .form-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 28px;
    max-width: 520px;
  }
  .field { margin-bottom: 18px; }
  .field label {
    display: block;
    font-size: .8125rem;
    font-weight: 600;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: .06em;
    margin-bottom: 6px;
  }
  .field input[type=text],
  .field input[type=email] {
    width: 100%;
    padding: 9px 12px;
    border: 1px solid var(--border);
    border-radius: var(--radius);
    font-family: var(--font);
    font-size: .9rem;
    color: var(--text);
    background: var(--bg);
  }
  .field input:focus {
    outline: none;
    border-color: var(--primary);
    background: #fff;
    box-shadow: 0 0 0 3px rgba(26,86,219,.12);
  }
  .form-actions { display: flex; gap: 10px; margin-top: 24px; }

  /* ── Busca ── */
  .search-bar { display: flex; gap: 10px; margin-bottom: 24px; }
  .search-bar input {
    flex: 1;
    padding: 9px 14px;
    border: 1px solid var(--border);
    border-radius: var(--radius);
    font-family: var(--font);
    font-size: .9rem;
    background: var(--card);
  }
  .search-bar input:focus {
    outline: none;
    border-color: var(--primary);
    box-shadow: 0 0 0 3px rgba(26,86,219,.12);
  }

  /* ── Rodapé ── */
  footer {
    text-align: center;
    font-size: .75rem;
    color: var(--muted);
    padding: 24px;
    font-family: var(--mono);
  }

  /* ── Detalhe exclusão ── */
  .detail-box {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 20px;
    max-width: 520px;
    margin-bottom: 20px;
  }
  .detail-row { display: flex; padding: 8px 0; border-bottom: 1px solid var(--border); font-size: .9rem; }
  .detail-row:last-child { border-bottom: none; }
  .detail-label { width: 100px; font-weight: 600; color: var(--muted); font-size: .8rem; text-transform: uppercase; letter-spacing: .05em; }
</style>
"""

# ── Layout base ───────────────────────────────────────────────────────────────

def _nav(ativo: str = "") -> str:
    """Barra de navegação com link ativo destacado."""
    links = [
        ("/listar",  "📋 Listar"),
        ("/novo",    "➕ Novo"),
        ("/buscar",  "🔍 Buscar"),
    ]
    items = "".join(
        f'<a href="{url}" class="{"active" if url == ativo else ""}">{label}</a>'
        for url, label in links
    )
    return f'<nav>{items}</nav>'

def _base(titulo: str, corpo: str, ativo: str = "") -> str:
    total = len(agenda)
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Agenda — {titulo}</title>
  {_CSS}
</head>
<body>
  <header>
    <span>📒</span>
    <h1>Agenda de Contatos</h1>
    <span class="badge">{total} / {CAPACIDADE} contatos</span>
  </header>
  {_nav(ativo)}
  <main>{corpo}</main>
  <footer>agenda_web.py · http.server · Python {__import__('sys').version.split()[0]}</footer>
</body>
</html>"""

def _mensagem(msg: str, tipo: str = "ok") -> str:
    return f'<p class="msg msg-{tipo}">{msg}</p>' if msg else ""


# ── Página: Lista ─────────────────────────────────────────────────────────────

def html_listar(msg: str = "", erro: str = "") -> str:
    linhas = "".join(
        f"""<tr>
          <td class="id-cell">#{c['id']}</td>
          <td>{c['nome']}</td>
          <td>{c['email']}</td>
          <td>{c['telefone']}</td>
          <td class="actions">
            <a class="btn btn-secondary btn-sm" href="/editar?id={c['id']}">✏️ Editar</a>
            <a class="btn btn-danger btn-sm"    href="/excluir?id={c['id']}">🗑️ Excluir</a>
          </td>
        </tr>"""
        for c in sorted(agenda, key=lambda x: x["nome"].lower())
    )
    corpo = f"""
    {_mensagem(msg)}
    {_mensagem(erro, "err")}
    <h2>Todos os Contatos</h2>
    <p style="margin-bottom:16px">
      <a class="btn btn-primary" href="/novo">➕ Novo Contato</a>
    </p>
    <div class="table-wrap">
      <table>
        <thead><tr><th>ID</th><th>Nome</th><th>E-mail</th><th>Telefone</th><th>Ações</th></tr></thead>
        <tbody>
          {linhas if linhas else '<tr class="empty-row"><td colspan="5">Nenhum contato cadastrado ainda.</td></tr>'}
        </tbody>
      </table>
    </div>"""
    return _base("Lista", corpo, "/listar")


# ── Página: Formulário (criar / editar) ───────────────────────────────────────

def html_formulario(acao: str, contato: dict | None = None, erro: str = "") -> str:
    c = contato or {"id": "", "nome": "", "email": "", "telefone": ""}
    novo    = contato is None
    titulo  = "Novo Contato" if novo else f"Editar Contato #{c['id']}"
    id_hidden = "" if novo else f'<input type="hidden" name="id" value="{c["id"]}">'
    corpo = f"""
    {_mensagem(erro, "err")}
    <h2>{"➕" if novo else "✏️"} {titulo}</h2>
    <div class="form-card">
      <form method="post" action="{acao}">
        {id_hidden}
        <div class="field">
          <label>Nome</label>
          <input type="text" name="nome" value="{c['nome']}" required placeholder="Ex: João Silva">
        </div>
        <div class="field">
          <label>E-mail</label>
          <input type="email" name="email" value="{c['email']}" required placeholder="Ex: joao@email.com">
        </div>
        <div class="field">
          <label>Telefone</label>
          <input type="text" name="telefone" value="{c['telefone']}" required placeholder="Ex: (11) 91234-5678">
        </div>
        <div class="form-actions">
          <button class="btn btn-primary" type="submit">💾 Salvar</button>
          <a class="btn btn-secondary" href="/listar">Cancelar</a>
        </div>
      </form>
    </div>"""
    ativo = "/novo" if novo else ""
    return _base(titulo, corpo, ativo)


# ── Página: Confirmar exclusão ────────────────────────────────────────────────

def html_confirmar_exclusao(c: dict) -> str:
    corpo = f"""
    <h2>🗑️ Confirmar Exclusão</h2>
    <p style="margin-bottom:16px;color:var(--muted);font-size:.9rem">
      Você está prestes a excluir o contato abaixo. Esta ação não pode ser desfeita.
    </p>
    <div class="detail-box">
      <div class="detail-row"><span class="detail-label">ID</span>       <span>#{c['id']}</span></div>
      <div class="detail-row"><span class="detail-label">Nome</span>     <span>{c['nome']}</span></div>
      <div class="detail-row"><span class="detail-label">E-mail</span>   <span>{c['email']}</span></div>
      <div class="detail-row"><span class="detail-label">Telefone</span> <span>{c['telefone']}</span></div>
    </div>
    <form method="post" action="/excluir" style="display:flex;gap:10px">
      <input type="hidden" name="id" value="{c['id']}">
      <button class="btn btn-danger"    type="submit">✅ Confirmar Exclusão</button>
      <a      class="btn btn-secondary" href="/listar">Cancelar</a>
    </form>"""
    return _base("Excluir", corpo)


# ── Página: Busca ─────────────────────────────────────────────────────────────

def html_buscar(termo: str = "", resultados: list | None = None) -> str:
    tabela = ""
    if resultados is not None:
        linhas = "".join(
            f"""<tr>
              <td class="id-cell">#{c['id']}</td>
              <td>{c['nome']}</td>
              <td>{c['email']}</td>
              <td>{c['telefone']}</td>
              <td class="actions">
                <a class="btn btn-secondary btn-sm" href="/editar?id={c['id']}">✏️ Editar</a>
                <a class="btn btn-danger btn-sm"    href="/excluir?id={c['id']}">🗑️ Excluir</a>
              </td>
            </tr>"""
            for c in resultados
        )
        tabela = f"""
        <p style="margin-bottom:12px;font-size:.875rem;color:var(--muted)">
          {len(resultados)} resultado(s) para <strong>"{termo}"</strong>
        </p>
        <div class="table-wrap">
          <table>
            <thead><tr><th>ID</th><th>Nome</th><th>E-mail</th><th>Telefone</th><th>Ações</th></tr></thead>
            <tbody>
              {linhas if linhas else '<tr class="empty-row"><td colspan="5">Nenhum resultado encontrado.</td></tr>'}
            </tbody>
          </table>
        </div>"""

    corpo = f"""
    <h2>🔍 Buscar Contato</h2>
    <form class="search-bar" method="get" action="/buscar">
      <input type="text" name="q" value="{termo}"
             placeholder="Buscar por nome ou e-mail...">
      <button class="btn btn-primary" type="submit">Buscar</button>
    </form>
    {tabela}"""
    return _base("Buscar", corpo, "/buscar")


# ═══════════════════════════════════════════════════════════════════════════════
#  CONTROLLER — Roteamento HTTP
# ═══════════════════════════════════════════════════════════════════════════════

class AgendaHandler(BaseHTTPRequestHandler):
    """
    Controlador HTTP.
    Cada método do_ mapeia para uma "action" do MVC web2py.
    """

    # ── Utilitários ───────────────────────────────────────────────────────────

    def _responder(self, html: str, status: int = 200) -> None:
        body = html.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type",   "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _redirecionar(self, url: str) -> None:
        """Redireciona para outra URL (Post/Redirect/Get pattern)."""
        self.send_response(303)
        self.send_header("Location", url)
        self.end_headers()

    def _ler_post(self) -> dict[str, str]:
        """Lê e decodifica os campos de um formulário POST."""
        n = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(n).decode("utf-8")
        return {k: unquote_plus(v[0]) for k, v in parse_qs(raw).items()}

    def log_message(self, fmt, *args):
        """Silencia os logs padrão do HTTPServer."""
        pass

    # ── GET ───────────────────────────────────────────────────────────────────

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path   = parsed.path
        qs     = parse_qs(parsed.query)

        def _qs(key: str) -> str:
            return unquote_plus(qs.get(key, [""])[0])

        # ── / ou /listar — lista todos os contatos ──
        if path in ("/", "/listar"):
            self._responder(html_listar(msg=_qs("msg"), erro=_qs("erro")))

        # ── /novo — formulário de criação ──
        elif path == "/novo":
            self._responder(html_formulario("/novo"))

        # ── /editar?id=N — formulário de edição ──
        elif path == "/editar":
            try:
                c = buscar_por_id(int(_qs("id")))
                if c:
                    self._responder(html_formulario("/editar", contato=c))
                else:
                    self._redirecionar(f"/listar?erro={quote_plus('Contato não encontrado.')}")
            except ValueError:
                self._redirecionar(f"/listar?erro={quote_plus('ID inválido.')}")

        # ── /excluir?id=N — confirmação de exclusão ──
        elif path == "/excluir":
            try:
                c = buscar_por_id(int(_qs("id")))
                if c:
                    self._responder(html_confirmar_exclusao(c))
                else:
                    self._redirecionar(f"/listar?erro={quote_plus('Contato não encontrado.')}")
            except ValueError:
                self._redirecionar(f"/listar?erro={quote_plus('ID inválido.')}")

        # ── /buscar?q=TERMO — pesquisa ──
        elif path == "/buscar":
            termo = _qs("q").strip()
            if termo:
                t = termo.lower()
                resultados = [
                    c for c in agenda
                    if t in c["nome"].lower() or t in c["email"].lower()
                ]
                self._responder(html_buscar(termo, resultados))
            else:
                self._responder(html_buscar())

        else:
            self._responder("<h1>404 — Página não encontrada</h1>", 404)

    # ── POST ──────────────────────────────────────────────────────────────────

    def do_POST(self) -> None:
        path   = urlparse(self.path).path
        campos = self._ler_post()

        # ── POST /novo — cria contato ──
        if path == "/novo":
            nome     = campos.get("nome", "").strip()
            email    = campos.get("email", "").strip()
            telefone = campos.get("telefone", "").strip()

            c_parcial = {"id": "", "nome": nome, "email": email, "telefone": telefone}

            if not (nome and email and telefone):
                self._responder(html_formulario("/novo", c_parcial,
                    erro="⚠ Todos os campos são obrigatórios."))
                return
            if not validar_email(email):
                self._responder(html_formulario("/novo", c_parcial,
                    erro="⚠ E-mail inválido. Ex: usuario@email.com"))
                return
            if not validar_telefone(telefone):
                self._responder(html_formulario("/novo", c_parcial,
                    erro="⚠ Telefone inválido. Use dígitos, espaços, +, -, (, )."))
                return
            if len(agenda) >= CAPACIDADE:
                self._redirecionar(f"/listar?erro={quote_plus('Agenda cheia!')}")
                return

            novo = {"id": proximo_id(), "nome": nome, "email": email, "telefone": telefone}
            agenda.append(novo)
            salvar_csv()
            msg_ok = f"Contato #{novo['id']} criado com sucesso! ✅"
            self._redirecionar(f"/listar?msg={quote_plus(msg_ok)}")

        # ── POST /editar — atualiza contato ──
        elif path == "/editar":
            try:
                cid = int(campos.get("id", 0))
            except ValueError:
                self._redirecionar("/listar")
                return

            c = buscar_por_id(cid)
            if not c:
                self._redirecionar(f"/listar?erro={quote_plus('Contato não encontrado.')}")
                return

            nome     = campos.get("nome", "").strip()
            email    = campos.get("email", "").strip()
            telefone = campos.get("telefone", "").strip()

            c_parcial = {"id": cid, "nome": nome, "email": email, "telefone": telefone}

            if not (nome and email and telefone):
                self._responder(html_formulario("/editar", c_parcial,
                    erro="⚠ Todos os campos são obrigatórios."))
                return
            if not validar_email(email):
                self._responder(html_formulario("/editar", c_parcial,
                    erro="⚠ E-mail inválido."))
                return
            if not validar_telefone(telefone):
                self._responder(html_formulario("/editar", c_parcial,
                    erro="⚠ Telefone inválido."))
                return

            c["nome"]     = nome
            c["email"]    = email
            c["telefone"] = telefone
            salvar_csv()
            msg_edit = f"Contato #{cid} atualizado com sucesso! ✅"
            self._redirecionar(f"/listar?msg={quote_plus(msg_edit)}")

        # ── POST /excluir — remove contato ──
        elif path == "/excluir":
            try:
                cid = int(campos.get("id", 0))
            except ValueError:
                self._redirecionar("/listar")
                return
            c = buscar_por_id(cid)
            if c:
                agenda.remove(c)
                salvar_csv()
                msg = f"Contato #{cid} removido com sucesso! ✅"
            else:
                msg = "Contato não encontrado."
            self._redirecionar(f"/listar?msg={quote_plus(msg)}")

        else:
            self._redirecionar("/")


# ═══════════════════════════════════════════════════════════════════════════════
#  INICIALIZADOR — Porta aleatória com teste de disponibilidade
# ═══════════════════════════════════════════════════════════════════════════════

PORTA_MIN = 18_000
PORTA_MAX = 28_000


def porta_esta_livre(porta: int) -> bool:
    """
    Tenta fazer bind na porta; se conseguir, ela está livre.
    O socket é fechado imediatamente após o teste (context manager).
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind(("0.0.0.0", porta))
            return True
        except OSError:
            return False


def encontrar_porta_livre() -> int:
    """
    Sorteia portas no intervalo [PORTA_MIN, PORTA_MAX] até encontrar
    uma disponível. Evita repetir sorteios já tentados.
    """
    total = PORTA_MAX - PORTA_MIN + 1
    testadas: set[int] = set()

    print(f"\n  Procurando porta livre em [{PORTA_MIN}–{PORTA_MAX}]...")

    while len(testadas) < total:
        porta = random.randint(PORTA_MIN, PORTA_MAX)
        if porta in testadas:
            continue
        testadas.add(porta)

        livre = porta_esta_livre(porta)
        status = "livre ✓" if livre else "ocupada ✗"
        print(f"    porta {porta} ... {status}")

        if livre:
            return porta

    raise RuntimeError(
        f"Nenhuma porta livre encontrada no intervalo [{PORTA_MIN}–{PORTA_MAX}]."
    )


# ═══════════════════════════════════════════════════════════════════════════════
#  PONTO DE ENTRADA
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 55)
    print("  📒  AGENDA DE CONTATOS — Interface Web")
    print("=" * 55)

    # 1. Carrega dados persistidos (ou cria demo)
    if carregar_csv():
        print(f"\n  💾 '{ARQUIVO_CSV}' carregado — {len(agenda)} contato(s).")
    else:
        carregar_demo()
        salvar_csv()
        print(f"\n  💾 '{ARQUIVO_CSV}' criado com dados de exemplo.")

    # 2. Seleciona porta aleatória e livre
    porta = encontrar_porta_livre()

    # 3. Inicia o servidor HTTP em todas as interfaces (0.0.0.0)
    servidor = HTTPServer(("0.0.0.0", porta), AgendaHandler)

    # 4. Descobre o IP real da interface de rede padrão.
    #    Abre um socket UDP apontado para 8.8.8.8 — nenhum dado é enviado,
    #    mas o SO precisa escolher a interface de saída, revelando o IP real.
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            ip_rede = s.getsockname()[0]
    except OSError:
        ip_rede = "0.0.0.0"
    url_rede = f"http://{ip_rede}:{porta}"

    print(f"\n  {'═' * 45}")
    print(f"  ✅  Servidor iniciado na porta {porta}")
    print(f"  {'─' * 45}")
    print(f"  Acesso →  {url_rede}")
    print(f"  {'─' * 45}")
    print("  Pressione Ctrl+C para encerrar.")
    print(f"  {'═' * 45}\n")

    # 5. Laço principal (bloqueante)
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        servidor.shutdown()
        print("\n\n  Servidor encerrado. Até logo! 👋\n")
