Documentação

#
```python
CAPACIDADE  = 100
ARQUIVO_CSV = "agenda_web.csv"
CAMPOS_CSV  = ["id", "nome", "email", "telefone", "cep"]
agenda: list[dict] = []
```
Define atributos representando o número máximo de contatos que a agenda armazena, o nome do arquivo que salva os dados dela e uma lista com os campos que são salvos no arquivo e dentro do programa.

```python
RE_EMAIL    = re.compile(r"^[\w\.\+\-]+@[\w\-]+\.[a-z]{2,}$", re.I)
RE_TELEFONE = re.compile(r"^[\d\s\(\)\-\+]{7,20}$")
```
Cria uma expressão regular, que é um objeto do python equivalente a um grupo de caracteres. <strong>\w</strong> é equivalente a todos os caracteres alfanuméricos, o mesmo se aplicando a <strong>\d</strong> e <strong>\s</strong> para números e espaços vazios. Os sinais <strong>\. \+ \-</strong> e <strong>\(\)</strong> representam os caracteres após a barra.  

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
