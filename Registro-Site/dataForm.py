from main import app
from flask import request, render_template, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json, time
from dados import (USERS_DIR, JOGADORES_DIR, NOME_VALIDO, CORES_PADRAO,
                   cor_valida, detectar_imagem, ler_perfil, perfil_completo)

# (nome do arquivo, limite em MB) de cada imagem que a pessoa pode enviar
IMAGENS = [("avatar", 3), ("fundo", 10), ("jogo1", 3), ("jogo2", 3), ("jogo3", 3)]

# limita o tamanho total do que o navegador pode enviar de uma vez
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024


@app.route("/FazerCadastro", methods=["POST"])
def FazerCadastro():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')

    if not NOME_VALIDO.fullmatch(username) or len(username) < 3:
        return render_template("cadastro.html", erro="Usuário inválido (mínimo 3 letras/números).")
    if len(password) < 3:
        return render_template("cadastro.html", erro="A senha precisa ter pelo menos 3 caracteres.")

    pasta = USERS_DIR / username
    if pasta.is_dir():
        return render_template("cadastro.html", erro="Esse usuário já existe.")

    pasta.mkdir(parents=True)
    cadastro = {
        "nome": username,
        "senha": generate_password_hash(password),  # guarda a senha embaralhada, nunca o texto puro
    }
    with open(pasta / "UserInfo.txt", 'w', encoding='utf-8') as f:  # w -> write; a -> append
        json.dump(cadastro, f, ensure_ascii=False, indent=2)

    session["username"] = username   # <- já deixa a pessoa LOGADA, sem precisar fazer login
    return redirect("/meu-perfil")   # e leva direto para criar o perfil


@app.route("/FazerLogin", methods=["POST"])
def FazerLogin():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')

    arquivo = USERS_DIR / username / "UserInfo.txt"
    if not NOME_VALIDO.fullmatch(username) or not arquivo.is_file():
        return render_template("login.html", erro="Usuário ou senha incorretos.")

    with open(arquivo, 'r', encoding='utf-8') as f:
        dados = json.load(f)

    if not check_password_hash(dados["senha"], password):
        return render_template("login.html", erro="Usuário ou senha incorretos.")

    session["username"] = username   # "lembra" que esse usuário está logado
    return redirect("/")


def apagar_imagens(pasta, base):
    """Apaga avatar.png, avatar.jpg, avatar.gif... (qualquer formato) da pasta."""
    for ext in ("png", "jpg", "gif", "webp"):
        (pasta / f"{base}.{ext}").unlink(missing_ok=True)


@app.route("/SalvarPerfil", methods=["POST"])
def SalvarPerfil():
    usuario = session.get("username")
    if not usuario:
        return redirect("/login")

    # O perfil é SEMPRE gravado em jogadores/<usuario>. Por isso cada conta só tem 1 perfil:
    # se ele já existe, esta rota EDITA; se não existe, cria.
    antigo = perfil_completo(usuario)
    pasta = JOGADORES_DIR / usuario
    form = request.form

    # 1) monta o perfil com os textos e cores do formulário
    perfil = dict(antigo)
    perfil["nome"] = form.get("nome", "").strip()[:30] or usuario   # [:30] corta em 30 caracteres
    perfil["jogo_principal"] = form.get("jogo_principal", "").strip()[:40]
    perfil["descricao"] = form.get("descricao", "").strip()[:500]
    for campo, padrao in CORES_PADRAO.items():
        perfil[campo] = cor_valida(form.get(campo), padrao)

    jogos = []
    for i in (1, 2, 3):
        jogos.append({
            "nome": form.get(f"jogo{i}_nome", "").strip()[:40],
            "info": form.get(f"jogo{i}_info", "").strip()[:80],
            "foto": antigo["jogos"][i - 1]["foto"],
        })
    perfil["jogos"] = jogos

    # 2) confere TODAS as imagens enviadas antes de gravar qualquer coisa
    novas = {}   # nome -> (bytes, extensão)
    for base, limite_mb in IMAGENS:
        arquivo = request.files.get(base)
        if arquivo and arquivo.filename:
            dados = arquivo.read()
            if len(dados) > limite_mb * 1024 * 1024:
                return render_template("editar.html", perfil=perfil,
                                       erro=f"A imagem '{base}' passa de {limite_mb} MB.")
            ext = detectar_imagem(dados)
            if ext is None:
                return render_template("editar.html", perfil=perfil,
                                       erro="Use apenas imagens PNG, JPG, GIF ou WEBP.")
            novas[base] = (dados, ext)

    # 3) tudo certo: grava as imagens
    pasta.mkdir(parents=True, exist_ok=True)

    def imagem_final(base, atual):
        if base in novas:                          # enviou uma nova -> troca a antiga
            dados, ext = novas[base]
            apagar_imagens(pasta, base)
            (pasta / f"{base}.{ext}").write_bytes(dados)
            return f"{base}.{ext}"
        if form.get(f"remover_{base}"):            # marcou "remover"
            apagar_imagens(pasta, base)
            return ""
        return atual                               # não mexeu -> continua a mesma

    perfil["avatar"] = imagem_final("avatar", antigo["avatar"])
    perfil["fundo"] = imagem_final("fundo", antigo["fundo"])
    for i, jogo in enumerate(perfil["jogos"], start=1):
        if jogo["nome"]:
            jogo["foto"] = imagem_final(f"jogo{i}", jogo["foto"])
        else:                                      # sem nome = jogo apagado (junto com a foto)
            apagar_imagens(pasta, f"jogo{i}")
            jogo["info"], jogo["foto"] = "", ""

    perfil["usuario"] = usuario
    perfil["criado_em"] = (ler_perfil(usuario) or {}).get("criado_em") or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    perfil["atualizado"] = int(time.time())        # usado para o navegador não mostrar imagem velha

    with open(pasta / "Info.txt", "w", encoding="utf-8") as f:
        json.dump(perfil, f, ensure_ascii=False, indent=2)

    return redirect(url_for("perfil", usuario=usuario))


@app.errorhandler(413)   # arquivos grandes demais
def arquivo_grande(erro):
    return 'Os arquivos enviados são grandes demais (máximo 20 MB no total). <a href="/meu-perfil">Voltar</a>', 413
