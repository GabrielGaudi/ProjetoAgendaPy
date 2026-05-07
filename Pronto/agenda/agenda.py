import os
import re
import csv

# ─────────────────────────────────────────────
#  Configurações
# ─────────────────────────────────────────────
CAPACIDADE  = 100
ARQUIVO_CSV = "agendaTeste.csv"
CAMPOS_CSV  = ["id", "nome", "email", "telefone", "cep", "rua", "bairro", "numero", "complemento", "cidade", "uf"]

agenda: list[dict] = []          # armazenamento em lista


# ─────────────────────────────────────────────
#  Utilitários de tela
# ─────────────────────────────────────────────
def limpar():
    os.system("cls" if os.name == "nt" else "clear")

def linha(char="─", largura=160):
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
RE_CEP = re.compile(r"\b\d{5}-\d{3}\b")

def validar_email(email: str) -> bool:
    return bool(RE_EMAIL.match(email))

def validar_telefone(tel: str) -> bool:
    return bool(RE_TELEFONE.match(tel))

def validar_cep(cep: str) -> bool:
    return bool(RE_CEP.match(cep))

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
    print(f"  [{c['id']:>3}]  {c['nome']:<25}  📞 {c['telefone']}   {c['cep']}   {c['rua']}")
    if detalhe:
        print(f"        📧 {c['email']}")
        print(f"        🏠 {c['rua']}, {c['numero']} - {c['bairro']}")
        if c['complemento']:
            print(f"           Complemento: {c['complemento']}")
        print(f"        📍 {c['cidade']} - {c['uf']}")
        linha("·")


# ─────────────────────────────────────────────
#  Persistência CSV
# ─────────────────────────────────────────────
def salvar_csv() -> None:
    """Regrava o arquivo CSV com o estado atual da lista."""
    with open(ARQUIVO_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CAMPOS_CSV)
        writer.writeheader()
        writer.writerows(agenda)

def carregar_csv() -> bool:
    """
    Carrega contatos do CSV para a lista.
    Retorna True se o arquivo existia, False caso contrário.
    """
    if not os.path.exists(ARQUIVO_CSV):
        return False
    with open(ARQUIVO_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            agenda.append({
                "id":       int(row["id"]),
                "nome":     row["nome"],
                "email":    row["email"],
                "telefone": row["telefone"],
                "cep": 	    row.get("cep", ""),
                "rua":      row.get("rua", ""),
                "bairro":   row.get("bairro", ""),
                "numero":   row.get("numero", ""),
                "complemento": row.get("complemento", ""),
                "cidade":   row.get("cidade", ""),
                "uf":       row.get("uf", "")
            })
    return True


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

    while True:
        cep = entrada("CEP : ")
        if validar_cep(cep):
           break
        print(" CEP inválido")
    rua = entrada("Rua       : ")
    bairro = entrada("Bairro    : ")
    numero = entrada("Número    : ")
    complemento = entrada("Complemento: ", obrigatorio=False)
    cidade = entrada("Cidade    : ")
    uf = entrada("UF        : ")
    contato = {"id": proximo_id(), "nome": nome,
               "email": email, "telefone": telefone, "cep": cep, "rua": rua,
               "bairro": bairro, "numero": numero, "complemento": complemento,
               "cidade": cidade, "uf": uf}
    agenda.append(contato)
    salvar_csv()

    print(f"\n  ✅  Contato{contato['id']} salvo com sucesso!")
    pausar()


def listar_contatos():
    cabecalho("📋  LISTA DE CONTATOS")

    if not agenda:
        print("\n  Nenhum contato cadastrado ainda.")
        pausar()
        return

    col_id  = 3
    col_nom = 18
    col_tel = 14
    col_ema = 22
    col_cep = 9
    col_rua = 15
    col_bairro = 12
    col_num = 6
    col_comp = 12
    col_cid = 12
    col_uf = 2
    cabecalho_tabela = (
        f"{'ID':>{col_id}}   "
        f"{'Nome':<{col_nom}}   "
        f"{'Telefone':<{col_tel}}   "
        f"{'E-mail':<{col_ema}}   "
        f"{'CEP':<{col_cep}}   "
        f"{'Rua':<{col_rua}}   "
        f"{'Bairro':<{col_bairro}}   "
        f"{'Num':<{col_num}}   "
        f"{'Compl':<{col_comp}}   "
        f"{'Cidade':<{col_cid}}   "
        f"{'UF':<{col_uf}}"
    )
    print(cabecalho_tabela)
    linha(largura=160)
    for c in sorted(agenda, key=lambda x: x["nome"].lower()):
        print(
            f"{c['id']:>{col_id}}   "
            f"{c['nome']:<{col_nom}}   "
            f"{c['telefone']:<{col_tel}}   "
            f"{c['email']:<{col_ema}}   "
            f"{c['cep']:<{col_cep}}   "
            f"{c['rua']:<{col_rua}}   "
            f"{c['bairro']:<{col_bairro}}   "
            f"{c['numero']:<{col_num}}   "
            f"{c['complemento']:<{col_comp}}   "
            f"{c['cidade']:<{col_cid}}   "
            f"{c['uf']:<{col_uf}}"
        )
    linha(largura=160)
    print(f"  Total: {len(agenda)} / {CAPACIDADE} contatos")
    pausar()


def buscar_contato():
    cabecalho("🔍  BUSCAR CONTATO")
    termo = entrada("Buscar por nome, e-mail, telefone, CEP, rua, bairro, cidade ou UF: ").lower()

    resultados = [
        c for c in agenda
        if termo in c["nome"].lower() or termo in c["email"].lower() or
           termo in c["telefone"].lower() or termo in c["cep"] or
           termo in c["rua"].lower() or termo in c["bairro"].lower() or
           termo in c["cidade"].lower() or termo in c["uf"].lower()
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

    while True: 
        novo_cep = entrada(f"Novo CEP [{contato['cep']}]: ", obrigatorio=False)
        if not novo_cep or validar_cep(novo_cep):
            break
        print("CEP inválido")
    novo_rua = entrada(f"Nova Rua [{contato['rua']}]: ", obrigatorio=False)
    novo_bairro = entrada(f"Novo Bairro [{contato['bairro']}]: ", obrigatorio=False)
    novo_numero = entrada(f"Novo Número [{contato['numero']}]: ", obrigatorio=False)
    novo_complemento = entrada(f"Novo Complemento [{contato['complemento']}]: ", obrigatorio=False)
    novo_cidade = entrada(f"Nova Cidade [{contato['cidade']}]: ", obrigatorio=False)
    novo_uf = entrada(f"Novo UF [{contato['uf']}]: ", obrigatorio=False)


    if novo_nome:    contato["nome"]     = novo_nome
    if novo_email:   contato["email"]    = novo_email
    if novo_tel:     contato["telefone"] = novo_tel
    if novo_cep:     contato["cep"]      = novo_cep
    if novo_rua:     contato["rua"]      = novo_rua
    if novo_bairro:  contato["bairro"]   = novo_bairro
    if novo_numero:  contato["numero"]   = novo_numero
    if novo_complemento: contato["complemento"] = novo_complemento
    if novo_cidade:  contato["cidade"]   = novo_cidade
    if novo_uf:      contato["uf"]       = novo_uf

    salvar_csv()
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

    print(f"\n  Contato selecionado: {contato['nome']} | {contato['email']} | {contato['telefone']} | {contato['cep']} | {contato['rua']}, {contato['numero']} - {contato['bairro']} | {contato['cidade']} - {contato['uf']}")
    conf = entrada("  Confirmar exclusão? (s/N): ", obrigatorio=False).lower()

    if conf == "s":
        agenda.remove(contato)
        salvar_csv()
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
        print(f"  ID          : {contato['id']}")
        print(f"  Nome        : {contato['nome']}")
        print(f"  E-mail      : {contato['email']}")
        print(f"  Telefone    : {contato['telefone']}")
        print(f"  CEP         : {contato['cep']}")
        print(f"  Rua         : {contato['rua']}")
        print(f"  Número      : {contato['numero']}")
        print(f"  Bairro      : {contato['bairro']}")
        print(f"  Complemento : {contato['complemento']}")
        print(f"  Cidade      : {contato['cidade']}")
        print(f"  UF          : {contato['uf']}")
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
#  Dados de demonstração (opcional)
# ─────────────────────────────────────────────
def carregar_demo():
    demos = [
        {"id": 1, "nome": "Ana Silva",      "email": "ana@email.com",    "telefone": "(11) 91234-5678", "cep": "06030-260", "rua": "Rua das Flores", "bairro": "Centro", "numero": "123", "complemento": "Apto 45", "cidade": "São Paulo", "uf": "SP"},
        {"id": 2, "nome": "Bruno Costa",    "email": "bruno@email.com",  "telefone": "(21) 98765-4321", "cep": "20000-000", "rua": "Av. Rio Branco", "bairro": "Centro", "numero": "456", "complemento": "", "cidade": "Rio de Janeiro", "uf": "RJ"},
        {"id": 3, "nome": "Carla Mendes",   "email": "carla@email.com",  "telefone": "(31) 97654-3210", "cep": "30000-000", "rua": "Rua da Bahia", "bairro": "Savassi", "numero": "789", "complemento": "Casa", "cidade": "Belo Horizonte", "uf": "MG"},
    ]
    agenda.extend(demos)


# ─────────────────────────────────────────────
#  Ponto de entrada
# ─────────────────────────────────────────────
if __name__ == "__main__":
    arquivo_existia = carregar_csv()
    if not arquivo_existia:
        # Primeira execução: carrega demos e já persiste
        carregar_demo()
        salvar_csv()
        print(f"  💾  Novo arquivo '{ARQUIVO_CSV}' criado com dados de exemplo.")
    else:
        print(f"  💾  Dados carregados de '{ARQUIVO_CSV}'  ({len(agenda)} contato(s)).")
    pausar()
    menu_principal()
