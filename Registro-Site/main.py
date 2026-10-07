from flask import Flask
app = Flask(__name__)
app.secret_key = "troque-isso-por-qualquer-texto"  # o Flask precisa disso para usar a "session" (lembrar quem está logado)

# o bagulho responsável por juntar tudo e fazer o site funcionar.
from views import *
from dataForm import *
from dataScript import *   # <- faltava esta linha: sem ela a rota /checkUser nunca era registrada

# Este código inicia o servidor Flask
if __name__ == "__main__":  # Checa se este arquivo é o que foi rodado no terminal, é tipo uma alavanca
    app.run(debug=True)     # 'inicia' o site
