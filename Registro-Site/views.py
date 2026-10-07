from main import app
from flask import render_template, session, redirect, abort, send_from_directory
from dados import (JOGADORES_DIR, NOME_VALIDO, ARQUIVO_VALIDO, CORES_PADRAO,
                   cor_valida, ler_perfil, ler_todos, perfil_completo)


# Tudo que este "context_processor" devolve fica disponível em TODOS os HTMLs automaticamente.
@app.context_processor
def variaveis_globais():
    usuario = session.get("username")
    return {"usuario": usuario, "tem_perfil": bool(usuario and ler_perfil(usuario))}


# Este arquivo é responsável pra levar para as páginas do site
@app.route("/")  # vai levar para página inicial do site
def home():
    return render_template("index.html", jogadores=ler_todos())


@app.route("/jogador/<usuario>")   # <usuario> é uma variável: /jogador/ana -> usuario = "ana"
def perfil(usuario):
    todos = ler_todos()
    # procura o perfil na lista (não usamos o nome para montar caminho de pasta: mais seguro)
    jogador = next((j for j in todos if j["usuario"] == usuario), None)
    if jogador is None:
        abort(404)   # perfil não existe -> página "Not Found"

    for campo, padrao in CORES_PADRAO.items():   # garante que as cores são válidas
        jogador[campo] = cor_valida(jogador.get(campo), padrao)

    jogos = [j for j in jogador.get("jogos", []) if j.get("nome")]   # só os jogos preenchidos
    return render_template("perfil.html", jogador=jogador, jogos=jogos,
                           numero=todos.index(jogador) + 1, total=len(todos),
                           eh_dono=(session.get("username") == usuario))


@app.route("/meu-perfil")   # tela para CRIAR ou EDITAR o próprio perfil
def meu_perfil():
    usuario = session.get("username")
    if not usuario:
        return redirect("/login")
    return render_template("editar.html", perfil=perfil_completo(usuario))


# entrega as imagens do perfil (foto, fundo, capas dos jogos)
@app.route("/midia/<usuario>/<arquivo>")
def midia(usuario, arquivo):
    if not NOME_VALIDO.fullmatch(usuario) or not ARQUIVO_VALIDO.fullmatch(arquivo):
        abort(404)
    return send_from_directory(JOGADORES_DIR / usuario, arquivo)


@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/cadastro")
def cadastro():
    return render_template("cadastro.html")

@app.route("/sair")
def sair():
    session.clear()   # esquece quem estava logado
    return redirect("/")
