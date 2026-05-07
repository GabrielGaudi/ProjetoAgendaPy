Documentação

#
```python
CAPACIDADE  = 100
ARQUIVO_CSV = "agenda_web.csv"
CAMPOS_CSV  = ["id", "nome", "email", "telefone", "cep"]
agenda: list[dict] = []
```
Define atributos representando o número máximo de contatos que a agenda armazena, o nome do arquivo que salva os dados dela e uma lista com os campos que são salvos no arquivo (CAMPOS_CSV) e dentro do programa (agenda).

```python
RE_EMAIL    = re.compile(r"^[\w\.\+\-]+@[\w\-]+\.[a-z]{2,}$", re.I)
RE_TELEFONE = re.compile(r"^[\d\s\(\)\-\+]{7,20}$")
```
O método <strong>re.compile</strong> cria uma expressão regular, que é um objeto do python equivalente a um grupo de caracteres. 
<strong>\w</strong> é equivalente a todos os caracteres alfanuméricos, o mesmo se aplicando a <strong>\d</strong> e <strong>\s</strong> para números e espaços vazios. Os sinais <strong>\. \+ \-</strong> e <strong>\(\)</strong> representam os caracteres após a barra.
Em <strong>RE_EMAIL</strong>, a expressão regular define uma sequência de: caracteres alfanuméricos, ponto e/ou sinais de + e -; seguidas por um "@"; seguidos por caracteres alfanuméricos e/ou o sinal -; seguido por um ponto, seguido pelas letras minúsculas de "a" até "z"

```python
def validar_email(email: str) -> bool:
    return bool(RE_EMAIL.match(email.strip()))

def validar_telefone(tel: str) -> bool:
    return bool(RE_TELEFONE.match(tel.strip()))
```
Verifica se a entrada do usúario se encaixa nos caracteres definidos pelas expressões regulares (método match) após remover carateres especiais e espaços dela (método strip)

```python
def proximo_id() -> int:
    return max((c["id"] for c in agenda), default=0) + 1

def buscar_por_id(cid: int) -> dict | None:
    for c in agenda:
        if c["id"] == cid:
            return c
    return None
```
- proximo_id: retorna o maior valor entre os atributos "id" da agenda somado a um para criar um id novo.
- buscar_por_id: busca por todos os elementos da agenda por um cujo "id" seja igual ao valor dado, retornando o elemento encontrado ou valor nulo.

```python
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
  ```
- salvar_csv(): usa o método do módulo "csv" para escrever (definido pelo parâmetro "w") um arquivo deste tipo com o nome atribuido anteriormente.
- carregar_csv(): se um arquivo com o nome definido não for encontrado no caminho padrão, retorna False. Se encontrar, usa o método 'open' para receber o texto do arquivo.
Para cada linha (elemento) no arquivo csv, adiciona os atributos correspondentes á lista dentro do programa, então retornando True.

```python
def carregar_demo() -> None:
    """Dados de exemplo para a primeira execução."""
    demos = [
        {"id": 1, "nome": "Ana Silva",    "email": "ana@email.com",   "telefone": "(11) 91234-5678"},
        {"id": 2, "nome": "Bruno Costa",  "email": "bruno@email.com", "telefone": "(21) 98765-4321"},
        {"id": 3, "nome": "Carla Mendes", "email": "carla@email.com", "telefone": "(31) 97654-3210"},
    ]
    agenda.extend(demos)
```
Manualmente criaa novos objetos com contatos e valores para teste e os adiciona à lista do programa.

# Métodos das agendas do terminal
```python
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
```
- limpar(): executa um comando para limpar o terminal de acordo com o SO utilizado
- linha(char="─", largura=60): digita no terminal o caractere atribuído em 'char'
- cabeçalhi(titulo: str): recebe o título da página atual e gera um cabeçalho com o nome do programa e linhas separando os títulos
- pausar: quando não é necessária entrada do usuário, mostra um texto indicando que ele pode seguir para a próxima página

```python
def entrada(prompt: str, obrigatorio=True) -> str:
    while True:
        valor = input(f"  {prompt}").strip()
        if valor or not obrigatorio:
            return valor
        print("  ⚠  Campo obrigatório. Tente novamente.")
```
entrada(): recebe um texto indicando o que o usuário deve escrever, se o usuário não escrever nada em um texto obrigatório, mostra um aviso até que ele digite um valor.

# Métodos CRUD
## Criar cabeçalho
```python
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
    salvar_csv()

    print(f"\n  ✅  Contato #{contato['id']} salvo com sucesso!")
    pausar()
```
Usa o método "cabeçalho()" com o título da página, se o limite de contatos for atingido avisa o usuário e retorna, impedindo a criação do novo contato.
Se houver espaço, recebe os valores do contato novo, verificando se eles são válidos e avisando o usuário caso não sejam.
Quando todos os valores forem inseridos, cria um novo objeto de contato com eles e o id único, adicionando-os na agenda e salvando o conteúdo no arquivo csv.

## Listar contatos
```python
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
```
Se a agenda estiver vazia, informa o usuário e retorna.
Se houverem elementos na agenda, cria uma lista com o nome de cada campo. A sequência ":<{col}" alinha o texto para a direção do símbolo "<" com uma margem igual ao valor entre chaves. Então, os valores precedidos por "col" definem o espaço entre os títulos.
Com o método "sorted()", organiza os elementos da agenda por nome, convertendo o texto para minúsculo para que os códigos de caracteres maiúsculos não afetem a ordem.
Faz um loop pela lista, mostrando os elementos ordenados na tela seguindo a posição horizontal dos títulos.
Finalmente mostra a quantidade de contatos na agenda e a quantidade máxima.

## Buscar Contato
```python
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
```
Recebe o termo de busca, verifi
