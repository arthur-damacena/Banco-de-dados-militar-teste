import json
import random
import hashlib
import re
from datetime import datetime
SENHA_OFICIAL = "admin123"
def carregar(nome):
    try:
        with open(nome, "r") as f:
            return json.load(f)
    except:
        return []
def salvar(nome, dados):
    with open(nome, "w") as f:
        json.dump(dados, f, indent=4)
usuarios = carregar("usuarios.json")
armas = carregar("armas.json")
logs = carregar("logs.json")
senhas_oficial = carregar("senhas_oficial.json")
def gerar_id():
    return random.randint(10000, 99999)
def gerar_senha_unica():
    while True:
        senha = str(random.randint(100000, 999999))
        if all(u["senha_raw"] != senha for u in senhas_oficial):
            return senha
def criptografar(senha):
    return hashlib.sha256(senha.encode()).hexdigest()
def log(acao, usuario, item):
    logs.append({
        "acao": acao,
        "usuario": usuario,
        "item": item,
        "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    })
    salvar("logs.json", logs)
def cadastrar_usuario():
    print("\n=== CADASTRO ===")
    grad = input("Graduação (max 3): ").upper()
    if len(grad) > 3:
        print("Erro")
        return
    nome = input("Nome: ")
    num = input("Número de guerra: ")
    esqd = input("Esquadrão: ")
    funcao = input("Função (normal/armeiro): ").lower()
    senha = gerar_senha_unica()
    senha_hash = criptografar(senha)
    print(f"Senha gerada: {senha}")
    usuario = {
        "id": gerar_id(),
        "grad": grad,
        "nome": nome,
        "num": num,
        "esqd": esqd,
        "senha": senha_hash,
        "funcao": funcao,
        "cautelas": []
    }
    usuarios.append(usuario)
    salvar("usuarios.json", usuarios)
    # salva senha real separada (simulação de segurança)
    senhas_oficial.append({
        "num": num,
        "senha_raw": senha
    })
    salvar("senhas_oficial.json", senhas_oficial)
# =========================
# LOGIN
# =========================
def login():
    num = input("Número de guerra: ")
    senha = input("Senha: ")
    senha_hash = criptografar(senha)
    for u in usuarios:
        if u["num"] == num and u["senha"] == senha_hash:
            print(f"Bem-vindo {u['nome']}")
            return u
    print("Acesso negado")
    return None
def cadastrar_arma(usuario):
    if usuario["funcao"] != "armeiro":
        print("Acesso negado")
        return
    numero = input("Número da arma (ex: FX002340): ").upper()
    if not re.match(r"^[A-Z]{2}[0-9]{6}$", numero):
        print("Formato inválido")
        return
    tipo = input("Tipo (fuzil/pistola/espingarda): ")
    arma = {
        "numero": numero,
        "tipo": tipo,
        "status": "disponivel",
        "responsavel": None
    }
    armas.append(arma)
    salvar("armas.json", armas)
def cautelar(usuario):
    numero = input("Número da arma: ")
    for arma in armas:
        if arma["numero"] == numero:
            if arma["status"] != "disponivel":
                print("Já cautelada")
                return
            arma["status"] = "cautelada"
            arma["responsavel"] = usuario["num"]
            usuario["cautelas"].append(numero)
            salvar("armas.json", armas)
            salvar("usuarios.json", usuarios)
            log("cautela", usuario["num"], numero)
            print("Cautelada")
            return
    print("Não encontrada")
def descautelar(usuario):
    numero = input("Número da arma: ")
    for arma in armas:
        if arma["numero"] == numero:
            if arma["responsavel"] != usuario["num"]:
                print("Você não é o responsável")
                return
            arma["status"] = "disponivel"
            arma["responsavel"] = None
            usuario["cautelas"].remove(numero)
            salvar("armas.json", armas)
            salvar("usuarios.json", usuarios)
            log("descautela", usuario["num"], numero)
            print("Descautelada")
            return
def ver_senhas():
    senha = input("Senha do oficial: ")
    if senha != SENHA_OFICIAL:
        print("Acesso negado")
        return
    for s in senhas_oficial:
        print(s)
while True:
    print("\n1 - Cadastrar usuário")
    print("2 - Login")
    print("3 - Ver senhas (oficial)")
    print("0 - Sair")
    op = input("Escolha: ")
    if op == "1":
        cadastrar_usuario()
    elif op == "2":
        user = login()
        if user:
            while True:
                print("\n1 - Cautelar arma")
                print("2 - Descautelar arma")
                if user["funcao"] == "armeiro":
                    print("3 - Cadastrar arma")
                print("0 - Logout")
                op2 = input("Escolha: ")
                if op2 == "1":
                    cautelar(user)
                elif op2 == "2":
                    descautelar(user)
                elif op2 == "3" and user["funcao"] == "armeiro":
                    cadastrar_arma(user)
                elif op2 == "0":
                    break
    elif op == "3":
        ver_senhas()
    elif op == "0":
        break