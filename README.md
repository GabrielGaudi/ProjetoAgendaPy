Documentação

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
Cria uma expressão regular, que é um objeto do python equivalente a um grupo de caracteres

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
- carregar_csv(): se um arquivo com o nome definido não for encontrado no caminho padrão, retorna False. Se encontrar, usa o método 'open' para receber o texto do arquivo
