# =============================================================================
# ast_nodes.py — Nós da Árvore Sintática Abstrata (AST) do compilador TinyScript
# Disciplina: Teoria da Computação e Compiladores — UNIBH 2026/1
# Professora: Charlene Cássia de Resende
# =============================================================================

"""
Este módulo define todas as classes de nós que compõem a AST (Abstract Syntax Tree)
gerada pelo analisador sintático (parser). Cada construção da linguagem TinyScript
possui uma classe correspondente derivada de ASTNode.
"""


class ASTNode:
    """Classe base para todos os nós da AST."""

    def __repr__(self):
        campos = ", ".join(f"{k}={v!r}" for k, v in self.__dict__.items())
        return f"{self.__class__.__name__}({campos})"


# ---------------------------------------------------------------------------
# Nó raiz
# ---------------------------------------------------------------------------

class Program(ASTNode):
    """Representa o programa completo — sequência de statements no nível raiz."""

    def __init__(self, statements):
        self.statements = statements  # list[ASTNode]


# ---------------------------------------------------------------------------
# Agrupamento de statements
# ---------------------------------------------------------------------------

class Block(ASTNode):
    """Bloco delimitado por { } contendo uma sequência de statements."""

    def __init__(self, statements):
        self.statements = statements  # list[ASTNode]


# ---------------------------------------------------------------------------
# Statements
# ---------------------------------------------------------------------------

class Assignment(ASTNode):
    """Atribuição: IDENT = expression ;"""

    def __init__(self, name, value):
        self.name = name    # str — nome da variável
        self.value = value  # ASTNode — expressão atribuída


class IfStatement(ASTNode):
    """Condicional: if ( expression ) block [ else block ]"""

    def __init__(self, condition, then_block, else_block=None):
        self.condition = condition      # ASTNode — condição booleana
        self.then_block = then_block    # Block
        self.else_block = else_block    # Block | None


class WhileLoop(ASTNode):
    """Laço de repetição: while ( expression ) block"""

    def __init__(self, condition, body):
        self.condition = condition  # ASTNode
        self.body = body            # Block


class PrintStatement(ASTNode):
    """Instrução de saída: print ( expression ) ;"""

    def __init__(self, expression):
        self.expression = expression  # ASTNode


# ---------------------------------------------------------------------------
# Expressões
# ---------------------------------------------------------------------------

class BinaryOp(ASTNode):
    """Operação binária: left op right  (ex.: a + b, x < 10)"""

    def __init__(self, left, op, right):
        self.left = left    # ASTNode
        self.op = op        # str — operador (+, -, *, /, ==, !=, <, >, <=, >=)
        self.right = right  # ASTNode


class UnaryOp(ASTNode):
    """Operação unária: op operand  (ex.: -x)"""

    def __init__(self, op, operand):
        self.op = op            # str — operador (-)
        self.operand = operand  # ASTNode


class IntegerLiteral(ASTNode):
    """Literal inteiro: 42, 0, 100"""

    def __init__(self, value):
        self.value = value  # int


class Variable(ASTNode):
    """Referência a uma variável pelo nome."""

    def __init__(self, name):
        self.name = name  # str
