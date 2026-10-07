# Este arquivo guarda as funções e constantes que VÁRIOS arquivos usam.
# Ele NÃO importa o main.py (isso evita o problema do "import circular").
from pathlib import Path
import json, re

BASE_DIR = Path(__file__).resolve().parent
USERS_DIR = BASE_DIR / "registros"      # registros/<usuario>/UserInfo.txt  (login)
JOGADORES_DIR = BASE_DIR / "jogadores"  # jogadores/<usuario>/Info.txt + imagens (perfil)

# letras, números, espaço, "_" e "-" (máx. 30). Impede nomes como "../" que mexeriam em outras pastas
NOME_VALIDO = re.compile(r"[\w][\w \-]{0,29}")
COR_VALIDA = re.compile(r"#[0-9a-fA-F]{6}")                          # ex.: #90e0ef
ARQUIVO_VALIDO = re.compile(r"(avatar|fundo|jogo[123])\.(png|jpg|gif|webp)")

CORES_PADRAO = {"cor_moldura": "#90e0ef", "cor_destaque": "#0077b6", "cor_fundo": "#03045e"}


def cor_valida(valor, padrao):
    """Só aceita cores no formato #rrggbb; se vier qualquer outra coisa, usa a cor padrão."""
    if isinstance(valor, str) and COR_VALIDA.fullmatch(valor):
        return valor
    return padrao


def detectar_imagem(dados):
    """Descobre o tipo da imagem olhando os primeiros bytes (não confia no nome do arquivo)."""
    if dados.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if dados.startswith(b"\xff\xd8\xff"):
        return "jpg"
    if dados.startswith((b"GIF87a", b"GIF89a")):
        return "gif"
    if dados[:4] == b"RIFF" and dados[8:12] == b"WEBP":
        return "webp"
    return None


def ler_perfil(usuario):
    """Devolve o perfil (dicionário) do usuário, ou None se ele ainda não criou."""
    if not NOME_VALIDO.fullmatch(usuario):
        return None
    arquivo = JOGADORES_DIR / usuario / "Info.txt"
    if not arquivo.is_file():
        return None
    with open(arquivo, "r", encoding="utf-8") as f:
        return json.load(f)


def ler_todos():
    """Lista com todos os perfis, do mais antigo ao mais novo."""
    lista = []
    if JOGADORES_DIR.is_dir():
        for pasta in JOGADORES_DIR.iterdir():
            if not pasta.is_dir():
                continue
            perfil = ler_perfil(pasta.name)
            if perfil and perfil.get("usuario") == pasta.name:   # ignora pastas de versões antigas
                lista.append(perfil)
    lista.sort(key=lambda p: (p.get("criado_em", ""), p["usuario"]))
    return lista


def perfil_completo(usuario):
    """Perfil salvo + valores padrão para o que estiver faltando (sempre com 3 espaços de jogo)."""
    perfil = {
        "usuario": usuario, "nome": usuario, "descricao": "", "jogo_principal": "",
        "avatar": "", "fundo": "", "atualizado": 0, **CORES_PADRAO,
        "jogos": [],
    }
    perfil.update(ler_perfil(usuario) or {})
    jogos = list(perfil.get("jogos", []))[:3]
    while len(jogos) < 3:
        jogos.append({})
    perfil["jogos"] = [{"nome": j.get("nome", ""), "info": j.get("info", ""), "foto": j.get("foto", "")} for j in jogos]
    return perfil
