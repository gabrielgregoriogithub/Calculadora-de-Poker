import streamlit as st
from treys import Card, Evaluator, Deck

# =========================
# CONFIGURAÇÃO
# =========================

st.set_page_config(
    page_title="Calculadora de Poker",
    page_icon="🃏",
    layout="wide"
)

evaluator = Evaluator()

# =========================
# CSS RESPONSIVO (deixa os botões menores em telas estreitas)
# =========================

st.markdown(
    """
    <style>
    div.stButton > button {
        padding: 0.2rem 0.1rem;
        font-size: 0.95rem;
        min-height: 2.6rem;
        line-height: 1.1;
    }

    @media (max-width: 640px) {
        div.stButton > button {
            font-size: 0.72rem;
            min-height: 2.1rem;
            padding: 0.05rem 0rem;
        }
        h1 {
            font-size: 1.5rem !important;
        }
        h3 {
            font-size: 1.05rem !important;
        }

        /* O Streamlit força min-width quase 100% nas colunas em telas
           estreitas, o que empilha os botões verticalmente. Isso
           sobrescreve esse comportamento para manter as cartas lado a lado. */
        div.stColumn {
            min-width: 30px !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================
# SÍMBOLOS
# =========================

simbolos = {
    "e": "♠",
    "c": "♥",
    "o": "♦",
    "p": "♣"
}

# =========================
# ESTADO (equivalente às variáveis globais do customtkinter)
# =========================

if "cartas_selecionadas" not in st.session_state:
    st.session_state.cartas_selecionadas = []

# =========================
# FUNÇÕES AUXILIARES
# =========================

def formatar_carta_visual(carta):
    valor = carta[0]
    naipe = carta[1]
    simbolo = simbolos[naipe]
    return f"{valor}{simbolo}"

# =========================
# FUNÇÕES POKER (idênticas ao código original)
# =========================

def criar_carta(texto):
    texto = texto.strip()
    texto = texto.replace("10", "T")

    valor = texto[0].upper()
    naipe = texto[1].lower()

    conversao = {
        "e": "s",
        "c": "h",
        "o": "d",
        "p": "c"
    }

    naipe = conversao.get(naipe, naipe)
    carta_final = valor + naipe

    return Card.new(carta_final)


def calcular_vitoria(player, board, simulacoes=5000):
    vitorias = 0
    empates = 0

    for _ in range(simulacoes):
        deck = Deck()
        usadas = player + board

        for carta in usadas:
            deck.cards.remove(carta)

        vilao = deck.draw(2)

        mesa_completa = board.copy()
        while len(mesa_completa) < 5:
            mesa_completa.append(deck.draw(1)[0])

        score_player = evaluator.evaluate(mesa_completa, player)
        score_vilao = evaluator.evaluate(mesa_completa, vilao)

        if score_player < score_vilao:
            vitorias += 1
        elif score_player == score_vilao:
            empates += 1

    winrate = (vitorias / simulacoes) * 100
    empate = (empates / simulacoes) * 100

    return winrate, empate


def sugestao_acao(winrate, board):
    if len(board) == 0:
        if winrate < 45:
            return "FOLD"
        elif winrate < 60:
            return "CALL"
        elif winrate < 75:
            return "RAISE"
        else:
            return "RAISE FORTE"
    else:
        if winrate < 35:
            return "FOLD"
        elif winrate < 55:
            return "CALL / CHECK"
        elif winrate < 70:
            return "BET"
        else:
            return "RAISE FORTE"

# =========================
# AÇÕES (equivalente ao selecionar_carta / resetar do customtkinter)
# =========================

def selecionar_carta(carta):
    cartas = st.session_state.cartas_selecionadas

    if len(cartas) >= 7:
        return
    if carta in cartas:
        return

    cartas.append(carta)


def resetar():
    st.session_state.cartas_selecionadas = []

# =========================
# CABEÇALHO
# =========================

col_titulo, col_reset = st.columns([5, 1])

with col_titulo:
    st.title("🃏 Calculadora de Poker")

with col_reset:
    st.write("")
    st.button("🔄 Nova Rodada", on_click=resetar, use_container_width=True)

cartas = st.session_state.cartas_selecionadas
mao = cartas[:2]
board = cartas[2:]

mao_visual = [formatar_carta_visual(c) for c in mao]
board_visual = [formatar_carta_visual(c) for c in board]

st.markdown(
    f"### Sua mão: {' '.join(mao_visual) if mao_visual else '—'}"
    f"&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;"
    f"Mesa: {' '.join(board_visual) if board_visual else '—'}"
)

# =========================
# RESULTADO
# =========================

if len(mao) < 2:
    st.info("Selecione as duas cartas da sua mão para ver os cálculos.")
else:
    player = [criar_carta(c) for c in mao]
    mesa = [criar_carta(c) for c in board]

    with st.spinner("Calculando..."):
        winrate, empate = calcular_vitoria(player, mesa)

    st.markdown(f"## Vitória - {winrate:.2f}%  |  Empate - {empate:.2f}%")

    mao_atual_texto = ""

    if len(mesa) >= 3:
        rank = evaluator.get_rank_class(
            evaluator.evaluate(mesa, player)
        )
        descricao_en = evaluator.class_to_string(rank)

        traducao_maos = {
            "High Card": "Carta Alta",
            "Pair": "Par",
            "Two Pair": "Dois Pares",
            "Three of a Kind": "Trinca",
            "Straight": "Sequência",
            "Flush": "Flush",
            "Full House": "Full House",
            "Four of a Kind": "Quadra",
            "Straight Flush": "Straight Flush",
            "Royal Flush": "Royal Flush"
        }

        descricao = traducao_maos.get(descricao_en, descricao_en)
        mao_atual_texto = f"Mão atual: {descricao}"

    sugestao = sugestao_acao(winrate, mesa)

    texto_final = " | ".join(
        t for t in [mao_atual_texto, f"Sugestão: {sugestao}"] if t
    )
    st.markdown(f"**{texto_final}**")

st.divider()

# =========================
# GRID DE CARTAS
# =========================

valores = [
    "A", "K", "Q", "J",
    "T", "9", "8", "7",
    "6", "5", "4", "3", "2"
]

naipes_info = [
    ("e", "ESPADAS"),
    ("c", "COPAS"),
    ("o", "OUROS"),
    ("p", "PAUS")
]

CARTAS_POR_LINHA = 7  # 13 cartas viram 2 linhas (7 + 6) em vez de 1 linha de 13

def dividir_em_linhas(lista, tamanho):
    return [lista[i:i + tamanho] for i in range(0, len(lista), tamanho)]

for naipe, nome_naipe in naipes_info:
    st.markdown(f"**{nome_naipe}**")

    for linha_valores in dividir_em_linhas(valores, CARTAS_POR_LINHA):
        colunas = st.columns(len(linha_valores), gap="small")

        for i, valor in enumerate(linha_valores):
            carta = valor + naipe
            selecionada = carta in cartas

            label = f"{valor}{simbolos[naipe]}"
            if selecionada:
                label = f"✅ {label}"

            with colunas[i]:
                st.button(
                    label,
                    key=f"btn_{carta}",
                    on_click=selecionar_carta,
                    args=(carta,),
                    disabled=selecionada,
                    use_container_width=True
                )
