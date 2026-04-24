import os
import re

# ─────────────────────────────────────────────
#  Configurações
# ─────────────────────────────────────────────
CAPACIDADE = 100
agenda: list[dict] = []          # armazenamento em lista


# ─────────────────────────────────────────────
#  Utilitários de tela
# ─────────────────────────────────────────────
def limpar():
    os.system("cls" if os.name == "nt" else "clear")

def linha(char="─", largura=60):
    print(char * largura)

def cabecalho(titulo: str):
    limpar()
    linha("═")
    print(f"{'📒  AGENDA DE CONTATOS':^60}")
    linha("─")
    print(f"  {titulo}")
    linha("─")

def pausar():
    input("\n  ↵  Pressione ENTER para continuar...")


# ─────────────────────────────────────────────
#  Validações
# ─────────────────────────────────────────────
RE_EMAIL    = re.compile(r"^[\w\.\+\-]+@[\w\-]+\.[a-z]{2,}$", re.I)
RE_TELEFONE = re.compile(r"^[\d\s\(\)\-\+]{7,20}$")

def validar_email(email: str) -> bool:
    return bool(RE_EMAIL.match(email))

def validar_telefone(tel: str) -> bool:
    return bool(RE_TELEFONE.match(tel))

def entrada(prompt: str, obrigatorio=True) -> str:
    while True:
        valor = input(f"  {prompt}").strip()
        if valor or not obrigatorio:
            return valor
        print("  ⚠  Campo obrigatório. Tente novamente.")


# ─────────────────────────────────────────────
#  Helpers de contato
# ─────────────────────────────────────────────
def proximo_id() -> int:
    return max((c["id"] for c in agenda), default=0) + 1

def buscar_por_id(cid: int) -> dict | None:
    for c in agenda:
        if c["id"] == cid:
            return c
    return None

def exibir_contato(c: dict, detalhe=False):
    print(f"  [{c['id']:>3}]  {c['nome']:<25}  📞 {c['telefone']}")
    if detalhe:
        print(f"        📧 {c['email']}")
        linha("·")


# ─────────────────────────────────────────────
#  CRUD
# ─────────────────────────────────────────────
def criar_contato():
    cabecalho("➕  NOVO CONTATO")

    if len(agenda) >= CAPACIDADE:
        print(f"\n  ⛔  Agenda cheia! Capacidade máxima: {CAPACIDADE} contatos.")
        pausar()
        return

    nome = entrada("Nome       : ")

    while True:
        email = entrada("E-mail     : ")
        if validar_email(email):
            break
        print("  ⚠  E-mail inválido. Ex: usuario@email.com")

    while True:
        telefone = entrada("Telefone   : ")
        if validar_telefone(telefone):
            break
        print("  ⚠  Telefone inválido. Use apenas dígitos, espaços, +, -, (, )")

    contato = {"id": proximo_id(), "nome": nome,
               "email": email, "telefone": telefone}
    agenda.append(contato)

    print(f"\n  ✅  Contato #{contato['id']} salvo com sucesso!")
    pausar()


def listar_contatos():
    cabecalho("📋  LISTA DE CONTATOS")

    if not agenda:
        print("\n  Nenhum contato cadastrado ainda.")
        pausar()
        return

    col_id  = 4
    col_nom = 22
    col_tel = 18
    col_ema = 28

    cabecalho_tabela = (
        f"  {'ID':>{col_id}}  "
        f"{'Nome':<{col_nom}}  "
        f"{'Telefone':<{col_tel}}  "
        f"{'E-mail':<{col_ema}}"
    )
    print(cabecalho_tabela)
    linha()
    for c in sorted(agenda, key=lambda x: x["nome"].lower()):
        print(
            f"  [{c['id']:>{col_id-2}}]  "
            f"{c['nome']:<{col_nom}}  "
            f"📞 {c['telefone']:<{col_tel-2}}  "
            f"📧 {c['email']}"
        )
    linha()
    print(f"  Total: {len(agenda)} / {CAPACIDADE} contatos")
    pausar()


def buscar_contato():
    cabecalho("🔍  BUSCAR CONTATO")
    termo = entrada("Buscar por nome ou e-mail: ").lower()

    resultados = [
        c for c in agenda
        if termo in c["nome"].lower() or termo in c["email"].lower()
    ]

    if not resultados:
        print("\n  Nenhum contato encontrado.")
    else:
        print(f"\n  {len(resultados)} resultado(s):\n")
        linha()
        for c in resultados:
            exibir_contato(c, detalhe=True)

    pausar()


def editar_contato():
    cabecalho("✏️  EDITAR CONTATO")

    if not agenda:
        print("\n  Nenhum contato para editar.")
        pausar()
        return

    try:
        cid = int(entrada("ID do contato a editar: "))
    except ValueError:
        print("  ⚠  ID inválido.")
        pausar()
        return

    contato = buscar_por_id(cid)
    if not contato:
        print(f"\n  ⚠  Contato #{cid} não encontrado.")
        pausar()
        return

    print(f"\n  Editando: {contato['nome']}  (deixe em branco para manter)\n")

    novo_nome = entrada(f"Novo nome [{contato['nome']}]: ", obrigatorio=False)

    while True:
        novo_email = entrada(f"Novo e-mail [{contato['email']}]: ", obrigatorio=False)
        if not novo_email or validar_email(novo_email):
            break
        print("  ⚠  E-mail inválido.")

    while True:
        novo_tel = entrada(f"Novo telefone [{contato['telefone']}]: ", obrigatorio=False)
        if not novo_tel or validar_telefone(novo_tel):
            break
        print("  ⚠  Telefone inválido.")

    if novo_nome:    contato["nome"]     = novo_nome
    if novo_email:   contato["email"]    = novo_email
    if novo_tel:     contato["telefone"] = novo_tel

    print(f"\n  ✅  Contato #{cid} atualizado!")
    pausar()


def excluir_contato():
    cabecalho("🗑️  EXCLUIR CONTATO")

    if not agenda:
        print("\n  Nenhum contato para excluir.")
        pausar()
        return

    try:
        cid = int(entrada("ID do contato a excluir: "))
    except ValueError:
        print("  ⚠  ID inválido.")
        pausar()
        return

    contato = buscar_por_id(cid)
    if not contato:
        print(f"\n  ⚠  Contato #{cid} não encontrado.")
        pausar()
        return

    print(f"\n  Contato selecionado: {contato['nome']} | {contato['email']} | {contato['telefone']}")
    conf = entrada("  Confirmar exclusão? (s/N): ", obrigatorio=False).lower()

    if conf == "s":
        agenda.remove(contato)
        print(f"\n  ✅  Contato #{cid} removido.")
    else:
        print("\n  ❌  Exclusão cancelada.")

    pausar()


def exibir_detalhes():
    cabecalho("🔎  DETALHES DO CONTATO")

    try:
        cid = int(entrada("ID do contato: "))
    except ValueError:
        print("  ⚠  ID inválido.")
        pausar()
        return

    contato = buscar_por_id(cid)
    if not contato:
        print(f"\n  ⚠  Contato #{cid} não encontrado.")
    else:
        linha()
        print(f"  ID       : {contato['id']}")
        print(f"  Nome     : {contato['nome']}")
        print(f"  E-mail   : {contato['email']}")
        print(f"  Telefone : {contato['telefone']}")
        linha()

    pausar()


# ─────────────────────────────────────────────
#  Menu principal
# ─────────────────────────────────────────────
MENU = [
    ("1", "➕  Adicionar contato",   criar_contato),
    ("2", "📋  Listar contatos",     listar_contatos),
    ("3", "🔍  Buscar contato",      buscar_contato),
    ("4", "🔎  Ver detalhes",        exibir_detalhes),
    ("5", "✏️  Editar contato",      editar_contato),
    ("6", "🗑️  Excluir contato",     excluir_contato),
    ("0", "🚪  Sair",               None),
]

def menu_principal():
    while True:
        cabecalho("MENU PRINCIPAL")
        print(f"  Contatos: {len(agenda)} / {CAPACIDADE}\n")
        for chave, descricao, _ in MENU:
            print(f"  [{chave}]  {descricao}")
        linha()

        opcao = entrada("Opção: ", obrigatorio=False).strip()

        acao = next((fn for k, _, fn in MENU if k == opcao), ...)

        if opcao == "0":
            limpar()
            print("\n  Até logo! 👋\n")
            break
        elif acao is ...:
            print("  ⚠  Opção inválida.")
            pausar()
        else:
            acao()


# ─────────────────────────────────────────────
#  Dados de demonstração
# ─────────────────────────────────────────────
def carregar_demo():
    demos = [
        {"id": 1, "nome": "Ana Silva",      "email": "ana@email.com",    "telefone": "(11) 91234-5678"},
        {"id": 2, "nome": "Bruno Costa",    "email": "bruno@email.com",  "telefone": "(21) 98765-4321"},
        {"id": 3, "nome": "Carla Mendes",   "email": "carla@email.com",  "telefone": "(31) 97654-3210"},
    ]
    agenda.extend(demos)


# ─────────────────────────────────────────────
#  Ponto de entrada
# ─────────────────────────────────────────────
if __name__ == "__main__":
    carregar_demo()
    menu_principal()
