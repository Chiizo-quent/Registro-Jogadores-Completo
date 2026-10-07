from main import app
from flask import request, jsonify
from pathlib import Path   # <- faltava este import (dava erro no Path)

BASE_DIR = Path(__file__).resolve().parent

# O JavaScript (cadastro.js) chama esta rota enquanto a pessoa digita o usuário
@app.route("/checkUser")
def checkUser():
    username = request.args.get('usernameCheck', '').strip()
    caminho = BASE_DIR / "registros" / username
    verify = bool(username) and caminho.is_dir()   # True se já existe uma pasta com esse nome
    return jsonify({"verify": verify})             # devolve True/False para o JavaScript
