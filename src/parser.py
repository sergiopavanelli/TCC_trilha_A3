# =============================================================================
# parser.py — Analisador Sintático Recursivo Descendente do compilador TinyScript
# Disciplina: Teoria da Computação e Compiladores — UNIBH 2026/1
# Professora: Charlene Cássia de Resende
# =============================================================================

"""
O analisador sintático (parser) é a segunda fase do compilador. Ele consome a lista
de tokens produzida pelo lexer e constrói uma Árvore Sintática Abstrata (AST).

Estratégia utilizada: PARSER RECURSIVO DESCENDENTE (top-down)
  - Cada não-terminal da gramática corresponde a um método Python
  - A análise começa em parse_program() e desce até os terminais

Gramática da linguagem TinyScript (EBNF):
  program        → statement* EOF
  statement      → assignment | if_stmt | while_stmt | print_stmt
  assignment     → IDENT '=' expression ';'
  if_stmt        → 'if' '(' expression ')' block ('else' block)?
  while_stmt     → 'while' '(' expression ')' block
  print_stmt     → 'print' '(' expression ')' ';'
  block          → '{' statement* '}'
  expression     → comparison
  comparison     → additive (('=='|'!='|'<'|'>'|'<='|'>=') additive)?
  additive       → multiplicative (('+' | '-') multiplicative)*
  multiplicative → unary (('*' | '/') unary)*
  unary          → '-' unary | primary
  primary        → INTEGER | IDENT | '(' expression ')'
"""

from lexer import TokenType
from ast_nodes import (
    Program, Block, Assignment, IfStatement, WhileLoop, PrintStatement,
    BinaryOp, UnaryOp, IntegerLiteral, Variable,
)


# ---------------------------------------------------------------------------
# Erro Sintático
# ---------------------------------------------------------------------------

class ErroSintatico(Exception):
    """Exceção lançada quando o parser encontra uma construção inesperada."""

    def __init__(self, mensagem, linha, coluna):
        super().__init__(f"Erro sintático na linha {linha}, coluna {coluna}: {mensagem}")
        self.linha  = linha
        self.coluna = coluna


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

class Parser:
    """
    Analisador sintático da linguagem TinyScript.

    Recebe a lista de tokens gerada pelo Lexer e produz uma AST.
    """

    def __init__(self, tokens: list):
        self.tokens = tokens
        self.pos    = 0  # índice do token atual

    # ------------------------------------------------------------------
    # Interface pública
    # ------------------------------------------------------------------

    def parse(self) -> Program:
        """Ponto de entrada: analisa o programa completo e retorna a AST."""
        programa = self._parse_program()
        self._consumir(TokenType.EOF)
        return programa

    # ------------------------------------------------------------------
    # Navegação na lista de tokens
    # ------------------------------------------------------------------

    def _atual(self):
        """Retorna o token na posição atual sem avançar."""
        return self.tokens[self.pos]

    def _peek(self, offset=1):
        """Retorna o token offset posições à frente (lookahead)."""
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return self.tokens[-1]  # EOF

    def _avancar(self):
        """Retorna o token atual e avança a posição."""
        tok = self.tokens[self.pos]
        if tok.tipo != TokenType.EOF:
            self.pos += 1
        return tok

    def _consumir(self, tipo_esperado: TokenType):
        """
        Verifica que o token atual é do tipo esperado e avança.
        Lança ErroSintatico se o tipo não corresponder.
        """
        tok = self._atual()
        if tok.tipo != tipo_esperado:
            raise ErroSintatico(
                f"esperado {tipo_esperado.name}, encontrado {tok.tipo.name} ({tok.valor!r})",
                tok.linha, tok.coluna,
            )
        return self._avancar()

    # ------------------------------------------------------------------
    # Regras gramaticais (não-terminais)
    # ------------------------------------------------------------------

    def _parse_program(self) -> Program:
        """program → statement* EOF"""
        stmts = []
        while self._atual().tipo != TokenType.EOF:
            stmts.append(self._parse_statement())
        return Program(stmts)

    def _parse_statement(self):
        """
        statement → assignment | if_stmt | while_stmt | print_stmt

        Usa lookahead para decidir qual regra aplicar.
        """
        tok = self._atual()

        if tok.tipo == TokenType.IF:
            return self._parse_if()

        if tok.tipo == TokenType.WHILE:
            return self._parse_while()

        if tok.tipo == TokenType.PRINT:
            return self._parse_print()

        # assignment: IDENT '=' expression ';'
        if tok.tipo == TokenType.IDENT and self._peek().tipo == TokenType.ASSIGN:
            return self._parse_assignment()

        raise ErroSintatico(
            f"statement inválido começando com {tok.tipo.name} ({tok.valor!r})",
            tok.linha, tok.coluna,
        )

    def _parse_assignment(self) -> Assignment:
        """assignment → IDENT '=' expression ';'"""
        nome_tok = self._consumir(TokenType.IDENT)
        self._consumir(TokenType.ASSIGN)
        valor = self._parse_expression()
        self._consumir(TokenType.SEMI)
        return Assignment(nome_tok.valor, valor)

    def _parse_if(self) -> IfStatement:
        """if_stmt → 'if' '(' expression ')' block ('else' block)?"""
        self._consumir(TokenType.IF)
        self._consumir(TokenType.LPAREN)
        condicao = self._parse_expression()
        self._consumir(TokenType.RPAREN)
        bloco_then = self._parse_block()

        bloco_else = None
        if self._atual().tipo == TokenType.ELSE:
            self._consumir(TokenType.ELSE)
            bloco_else = self._parse_block()

        return IfStatement(condicao, bloco_then, bloco_else)

    def _parse_while(self) -> WhileLoop:
        """while_stmt → 'while' '(' expression ')' block"""
        self._consumir(TokenType.WHILE)
        self._consumir(TokenType.LPAREN)
        condicao = self._parse_expression()
        self._consumir(TokenType.RPAREN)
        corpo = self._parse_block()
        return WhileLoop(condicao, corpo)

    def _parse_print(self) -> PrintStatement:
        """print_stmt → 'print' '(' expression ')' ';'"""
        self._consumir(TokenType.PRINT)
        self._consumir(TokenType.LPAREN)
        expr = self._parse_expression()
        self._consumir(TokenType.RPAREN)
        self._consumir(TokenType.SEMI)
        return PrintStatement(expr)

    def _parse_block(self) -> Block:
        """block → '{' statement* '}'"""
        self._consumir(TokenType.LBRACE)
        stmts = []
        while self._atual().tipo != TokenType.RBRACE:
            if self._atual().tipo == TokenType.EOF:
                tok = self._atual()
                raise ErroSintatico(
                    "bloco não fechado — esperado '}'",
                    tok.linha, tok.coluna,
                )
            stmts.append(self._parse_statement())
        self._consumir(TokenType.RBRACE)
        return Block(stmts)

    # ------------------------------------------------------------------
    # Expressões (hierarquia de precedência)
    # ------------------------------------------------------------------

    def _parse_expression(self):
        """expression → comparison"""
        return self._parse_comparison()

    def _parse_comparison(self):
        """
        comparison → additive (('=='|'!='|'<'|'>'|'<='|'>=') additive)?

        Apenas UMA comparação por expressão (sem encadeamento).
        """
        esq = self._parse_additive()

        ops_comparacao = {
            TokenType.EQ:  '==',
            TokenType.NEQ: '!=',
            TokenType.LT:  '<',
            TokenType.GT:  '>',
            TokenType.LE:  '<=',
            TokenType.GE:  '>=',
        }

        if self._atual().tipo in ops_comparacao:
            tok_op = self._avancar()
            op     = ops_comparacao[tok_op.tipo]
            dir_   = self._parse_additive()
            return BinaryOp(esq, op, dir_)

        return esq

    def _parse_additive(self):
        """additive → multiplicative (('+' | '-') multiplicative)*"""
        no = self._parse_multiplicative()

        while self._atual().tipo in (TokenType.PLUS, TokenType.MINUS):
            tok_op = self._avancar()
            op     = tok_op.valor          # '+' ou '-'
            dir_   = self._parse_multiplicative()
            no     = BinaryOp(no, op, dir_)

        return no

    def _parse_multiplicative(self):
        """multiplicative → unary (('*' | '/') unary)*"""
        no = self._parse_unary()

        while self._atual().tipo in (TokenType.STAR, TokenType.SLASH):
            tok_op = self._avancar()
            op     = tok_op.valor          # '*' ou '/'
            dir_   = self._parse_unary()
            no     = BinaryOp(no, op, dir_)

        return no

    def _parse_unary(self):
        """unary → '-' unary | primary"""
        if self._atual().tipo == TokenType.MINUS:
            self._avancar()
            operando = self._parse_unary()
            return UnaryOp('-', operando)
        return self._parse_primary()

    def _parse_primary(self):
        """primary → INTEGER | IDENT | '(' expression ')'"""
        tok = self._atual()

        if tok.tipo == TokenType.INTEGER:
            self._avancar()
            return IntegerLiteral(tok.valor)

        if tok.tipo == TokenType.IDENT:
            self._avancar()
            return Variable(tok.valor)

        if tok.tipo == TokenType.LPAREN:
            self._consumir(TokenType.LPAREN)
            expr = self._parse_expression()
            self._consumir(TokenType.RPAREN)
            return expr

        raise ErroSintatico(
            f"expressão inválida: token inesperado {tok.tipo.name} ({tok.valor!r})",
            tok.linha, tok.coluna,
        )
