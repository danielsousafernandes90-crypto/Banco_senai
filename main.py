from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import os
import re


Banco_senai = FastAPI(
    title="API Simulador Banco do Brasil - Trabalho Acadêmico"
)


CONTAS_MOCK = {
    "1234-5": {
        "titular": "Fulano de Tal",
        "saldo": 1500.50,
        "tipo": "Conta Corrente BB",
        "agencia": "0001"
    },
    "5678-9": {
        "titular": "Ciclana de Sousa",
        "saldo": 50000.00,
        "tipo": "Poupança Ouro BB",
        "agencia": "0001"
    }
}


# =========================
# CADASTRO DE CLIENTE
# =========================

class CadastroCliente(BaseModel):
    agencia: str
    conta: str
    titular: str
    saldo_inicial: float
    tipo: str


# =========================
# CADASTRO DE FUNCIONÁRIO
# =========================

class CadastroFuncionario(BaseModel):
    nome: str
    cpf: str
    cargo: str


# Lista temporária de funcionários
FUNCIONARIOS = []


# =========================
# VALIDAÇÃO DO CPF
# =========================

def validar_cpf(cpf: str):

    # Remove pontos, traços e outros caracteres
    cpf = re.sub(r"\D", "", cpf)

    # Verifica se possui 11 dígitos
    if len(cpf) != 11:
        return False

    # Verifica se todos os números são iguais
    if cpf == cpf[0] * 11:
        return False

    # Primeiro dígito verificador
    soma = 0

    for i in range(9):
        soma += int(cpf[i]) * (10 - i)

    digito1 = (soma * 10) % 11

    if digito1 == 10:
        digito1 = 0

    if digito1 != int(cpf[9]):
        return False

    # Segundo dígito verificador
    soma = 0

    for i in range(10):
        soma += int(cpf[i]) * (11 - i)

    digito2 = (soma * 10) % 11

    if digito2 == 10:
        digito2 = 0

    if digito2 != int(cpf[10]):
        return False

    return True


# =========================
# LOGIN
# =========================

@Banco_senai.get("/api/v1/auth/login")
def realizar_login(agencia: str, conta: str):

    if conta in CONTAS_MOCK and CONTAS_MOCK[conta]["agencia"] == agencia:
        return {
            "autenticado": True,
            "dados": CONTAS_MOCK[conta]
        }

    raise HTTPException(
        status_code=401,
        detail="Agência ou Conta inválidas no Banco do Brasil"
    )


# =========================
# CADASTRO DE CLIENTE
# =========================

@Banco_senai.post("/api/v1/auth/cadastrar")
def realizar_cadastro(cliente: CadastroCliente):

    if cliente.conta in CONTAS_MOCK:
        raise HTTPException(
            status_code=400,
            detail="Esta conta já está cadastrada no Banco do Brasil"
        )

    CONTAS_MOCK[cliente.conta] = {
        "titular": cliente.titular,
        "saldo": cliente.saldo_inicial,
        "tipo": cliente.tipo,
        "agencia": cliente.agencia
    }

    return {
        "status": "sucesso",
        "mensagem": "Cliente cadastrado com sucesso!"
    }


# =========================
# CADASTRAR FUNCIONÁRIO
# =========================

@Banco_senai.post("/api/v1/funcionarios/cadastrar")
def cadastrar_funcionario(funcionario: CadastroFuncionario):

    # Verifica se o CPF é válido
    if not validar_cpf(funcionario.cpf):
        raise HTTPException(
            status_code=400,
            detail="CPF inválido!"
        )

    # Limpa o CPF antes de salvar
    cpf_limpo = re.sub(r"\D", "", funcionario.cpf)

    # Verifica se o CPF já foi cadastrado
    for funcionario_cadastrado in FUNCIONARIOS:
        if funcionario_cadastrado["cpf"] == cpf_limpo:
            raise HTTPException(
                status_code=400,
                detail="CPF já cadastrado!"
            )

    # Cria o funcionário
    novo_funcionario = {
        "nome": funcionario.nome,
        "cpf": cpf_limpo,
        "cargo": funcionario.cargo
    }

    # Adiciona à lista
    FUNCIONARIOS.append(novo_funcionario)

    return {
        "status": "sucesso",
        "mensagem": "Funcionário cadastrado!",
        "funcionario": novo_funcionario
    }


# =========================
# LISTAR FUNCIONÁRIOS
# =========================

@Banco_senai.get("/api/v1/funcionarios")
def listar_funcionarios():

    return {
        "funcionarios": FUNCIONARIOS
    }


# =========================
# PÁGINA PRINCIPAL
# =========================

@Banco_senai.get("/", response_class=HTMLResponse)
def interface_grafica():

    caminho_html = os.path.join(
        "Banco_senai",
        "templates",
        "index.html"
    )

    with open(caminho_html, "r", encoding="utf-8") as arquivo:
        return arquivo.read()

