# =============================================================================
# lexer.py — Analisador Léxico (Tokenizador) do compilador TinyScript
# Disciplina: Teoria da Computação e Compiladores — UNIBH 2026/1
# Professora: Charlene Cássia de Resende
# =============================================================================

"""
O analisador léxico (lexer) é a primeira fase do compilador. Ele lê o código-fonte
caractere a caractere e agrupa sequências em unidades significativas chamadas TOKENS.

Exemplo:
    Entrada:  x = 10 + y ;
    Saída:    [IDENT('x'), ASSIGN, INT(10), PLUS, IDENT('y'), SEMI, EOF]
"""

from enum import Enum, auto


# ---------------------------------------------------------------------------
# Tipos de token
# ---------------------------------------------------------------------------

class TokenType(Enum):
    # Literais
    INTEGER     = auto()   # número inteiro: 0, 42, 100

    # Identificadores e palavras reservadas
    IDENT       = auto()   # nome de variável: x, total, resultado
    IF          = auto()   # palavra reservada: if
    ELSE        = auto()   # palavra reservada: else
    WHILE       = auto()   # palavra reservada: while
    PRINT       = auto()   # palavra reservada: print

    # Operadores aritméticos
    PLUS        = auto()   # +
    MINUS       = auto()   # -
    STAR        = auto()   # *
    SLASH       = auto()   # /

    # Operadores de comparação
    EQ          = auto()   # ==
    NEQ         = auto()   # !=
    LT          = auto()   # <
    GT          = auto()   # >
    LE          = auto()   # <=
    GE          = auto()   # >=

    # Atribuição
    ASSIGN      = auto()   # =

    # Delimitadores
    LPAREN      = auto()   # (
    RPAREN      = auto()   # )
    LBRACE      = auto()   # {
    RBRACE      = auto()   # }
    SEMI        = auto()   # ;

    # Fim de arquivo
    EOF         = auto()


# Mapeamento de palavras reservadas
PALAVRAS_RESERVADAS = {
    "if":    TokenType.IF,
    "else":  TokenType.ELSE,
    "while": TokenType.WHILE,
    "print": TokenType.PRINT,
}


# ---------------------------------------------------------------------------
# Token
# ---------------------------------------------------------------------------

class Token:
    """Representa um token com tipo, valor e posição no código-fonte."""

    def __init__(self, tipo: TokenType, valor, linha: int, coluna: int):
        self.tipo   = tipo    # TokenType
        self.valor  = valor   # valor léxico (str ou int)
        self.linha  = linha   # linha no código-fonte (começa em 1)
        self.coluna = coluna  # coluna no código-fonte (começa em 1)

    def __repr__(self):
        return f"Token({self.tipo.name}, {self.valor!r}, L{self.linha}:C{self.coluna})"


# ---------------------------------------------------------------------------
# Erro Léxico
# ---------------------------------------------------------------------------

class ErroLexico(Exception):
    """Exceção lançada quando o lexer encontra um caractere inesperado."""

    def __init__(self, char, linha, coluna):
        super().__init__(
            f"Erro léxico na linha {linha}, coluna {coluna}: "
            f"caractere inesperado {char!r}"
        )
        self.linha  = linha
        self.coluna = coluna


# ---------------------------------------------------------------------------
# Lexer
# ---------------------------------------------------------------------------

class Lexer:
    """
    Analisador léxico da linguagem TinyScript.

    Percorre o código-fonte e produz uma lista de tokens.
    Ignora espaços em branco e comentários de linha ( // ... ).
    """

    def __init__(self, codigo_fonte: str):
        self.fonte  = codigo_fonte
        self.pos    = 0             # posição atual no string
        self.linha  = 1
        self.coluna = 1

    # ------------------------------------------------------------------
    # Interface pública
    # ------------------------------------------------------------------

    def tokenizar(self) -> list:
        """Percorre todo o código-fonte e retorna a lista completa de tokens."""
        tokens = []
        while True:
            tok = self._proximo_token()
            tokens.append(tok)
            if tok.tipo == TokenType.EOF:
                break
        return tokens

    # ------------------------------------------------------------------
    # Navegação no texto
    # ------------------------------------------------------------------

    def _atual(self):
        """Retorna o caractere atual sem avançar."""
        if self.pos >= len(self.fonte):
            return None
        return self.fonte[self.pos]

    def _proximo(self):
        """Retorna o próximo caractere (lookahead de 1) sem avançar."""
        if self.pos + 1 >= len(self.fonte):
            return None
        return self.fonte[self.pos + 1]

    def _avancar(self):
        """Avança uma posição, atualizando linha e coluna."""
        ch = self.fonte[self.pos]
        self.pos += 1
        if ch == '\n':
            self.linha  += 1
            self.coluna  = 1
        else:
            self.coluna += 1
        return ch

    # ------------------------------------------------------------------
    # Produção de tokens
    # ------------------------------------------------------------------

    def _proximo_token(self) -> Token:
        """Lê e retorna o próximo token do código-fonte."""

        # Pula espaços em branco e comentários
        self._pular_espacos_e_comentarios()

        # Fim de arquivo
        if self._atual() is None:
            return Token(TokenType.EOF, None, self.linha, self.coluna)

        linha_ini  = self.linha
        coluna_ini = self.coluna
        ch = self._atual()

        # --- Número inteiro ---
        if ch.isdigit():
            return self._ler_inteiro(linha_ini, coluna_ini)

        # --- Identificador ou palavra reservada ---
        if ch.isalpha() or ch == '_':
            return self._ler_identificador(linha_ini, coluna_ini)

        # --- Operadores e delimitadores ---
        self._avancar()

        if ch == '+':
            return Token(TokenType.PLUS,   '+', linha_ini, coluna_ini)
        if ch == '-':
            return Token(TokenType.MINUS,  '-', linha_ini, coluna_ini)
        if ch == '*':
            return Token(TokenType.STAR,   '*', linha_ini, coluna_ini)
        if ch == '/':
            return Token(TokenType.SLASH,  '/', linha_ini, coluna_ini)
        if ch == '(':
            return Token(TokenType.LPAREN, '(', linha_ini, coluna_ini)
        if ch == ')':
            return Token(TokenType.RPAREN, ')', linha_ini, coluna_ini)
        if ch == '{':
            return Token(TokenType.LBRACE, '{', linha_ini, coluna_ini)
        if ch == '}':
            return Token(TokenType.RBRACE, '}', linha_ini, coluna_ini)
        if ch == ';':
            return Token(TokenType.SEMI,   ';', linha_ini, coluna_ini)

        # Operadores com possível segundo caractere
        if ch == '=':
            if self._atual() == '=':
                self._avancar()
                return Token(TokenType.EQ,     '==', linha_ini, coluna_ini)
            return Token(TokenType.ASSIGN, '=',  linha_ini, coluna_ini)

        if ch == '!':
            if self._atual() == '=':
                self._avancar()
                return Token(TokenType.NEQ, '!=', linha_ini, coluna_ini)
            raise ErroLexico('!', linha_ini, coluna_ini)

        if ch == '<':
            if self._atual() == '=':
                self._avancar()
                return Token(TokenType.LE, '<=', linha_ini, coluna_ini)
            return Token(TokenType.LT, '<', linha_ini, coluna_ini)

        if ch == '>':
            if self._atual() == '=':
                self._avancar()
                return Token(TokenType.GE, '>=', linha_ini, coluna_ini)
            return Token(TokenType.GT, '>', linha_ini, coluna_ini)

        # Caractere desconhecido
        raise ErroLexico(ch, linha_ini, coluna_ini)

    # ------------------------------------------------------------------
    # Auxiliares de leitura
    # ------------------------------------------------------------------

    def _pular_espacos_e_comentarios(self):
        """Avança além de espaços, tabs, quebras de linha e comentários //."""
        while self._atual() is not None:
            ch = self._atual()

            # Espaço em branco
            if ch in (' ', '\t', '\r', '\n'):
                self._avancar()
                continue

            # Comentário de linha: // até o fim da linha
            if ch == '/' and self._proximo() == '/':
                while self._atual() is not None and self._atual() != '\n':
                    self._avancar()
                continue

            break  # caractere significativo encontrado

    def _ler_inteiro(self, linha_ini, coluna_ini) -> Token:
        """Lê uma sequência de dígitos e retorna um token INTEGER."""
        buf = []
        while self._atual() is not None and self._atual().isdigit():
            buf.append(self._avancar())
        return Token(TokenType.INTEGER, int(''.join(buf)), linha_ini, coluna_ini)

    def _ler_identificador(self, linha_ini, coluna_ini) -> Token:
        """Lê um identificador e verifica se é palavra reservada."""
        buf = []
        while self._atual() is not None and (self._atual().isalnum() or self._atual() == '_'):
            buf.append(self._avancar())
        texto = ''.join(buf)
        tipo  = PALAVRAS_RESERVADAS.get(texto, TokenType.IDENT)
        return Token(tipo, texto, linha_ini, coluna_ini)
