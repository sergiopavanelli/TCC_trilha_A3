# =============================================================================
# compiler.py — Orquestrador do compilador TinyScript + Interface de Linha de Comando
# Disciplina: Teoria da Computação e Compiladores — UNIBH 2026/1
# Professora: Charlene Cássia de Resende
# =============================================================================

"""
Este módulo integra todas as fases do compilador TinyScript:
  1. Análise Léxica  (Lexer)
  2. Análise Sintática (Parser)
  3. Geração de Código Intermediário (GeradorDeCodigo)

Uso via linha de comando:
  python compiler.py <arquivo.tiny>

Exemplo:
  python compiler.py ../examples/exemplo1_aritmetica.tiny
"""

import sys
import os

# Garante que os módulos src/ sejam encontrados ao executar diretamente
sys.path.insert(0, os.path.dirname(__file__))

# Força UTF-8 no stdout para suportar caracteres especiais no Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from lexer   import Lexer,   ErroLexico
from parser  import Parser,  ErroSintatico
from codegen import GeradorDeCodigo


# ---------------------------------------------------------------------------
# Classe principal
# ---------------------------------------------------------------------------

class CompiladorTinyScript:
    """
    Orquestra as três fases do compilador e expõe o resultado de cada etapa.
    """

    def __init__(self):
        self._lexer   = None
        self._parser  = None
        self._gerador = GeradorDeCodigo()

    def compilar(self, codigo_fonte: str) -> dict:
        """
        Compila o código-fonte TinyScript e retorna um dicionário com:
          - 'tokens'   : lista de tokens produzida pelo lexer
          - 'ast'      : AST produzida pelo parser (repr)
          - 'codigo'   : código intermediário gerado (string)

        Lança ErroLexico ou ErroSintatico em caso de erros.
        """
        # --- Fase 1: Análise Léxica ---
        lexer  = Lexer(codigo_fonte)
        tokens = lexer.tokenizar()

        # --- Fase 2: Análise Sintática ---
        parser = Parser(tokens)
        ast    = parser.parse()

        # --- Fase 3: Geração de Código ---
        codigo = self._gerador.gerar(ast)

        return {
            'tokens': tokens,
            'ast':    ast,
            'codigo': codigo,
        }

    def compilar_arquivo(self, caminho: str) -> dict:
        """Lê um arquivo .tiny e compila seu conteúdo."""
        with open(caminho, 'r', encoding='utf-8') as f:
            codigo_fonte = f.read()
        return self.compilar(codigo_fonte)


# ---------------------------------------------------------------------------
# Funções de exibição
# ---------------------------------------------------------------------------

SEPARADOR = '─' * 60

def _imprimir_tokens(tokens):
    print(f"\n{'═'*60}")
    print("  FASE 1 — ANÁLISE LÉXICA  |  Tokens produzidos")
    print(f"{'═'*60}")
    for tok in tokens:
        # Não exibe o token EOF na listagem
        if tok.tipo.name != 'EOF':
            print(f"  [{tok.tipo.name:<10}]  valor={tok.valor!r:<15}  L{tok.linha}:C{tok.coluna}")
    print(f"  Total: {sum(1 for t in tokens if t.tipo.name != 'EOF')} tokens")

def _imprimir_ast(ast):
    print(f"\n{'═'*60}")
    print("  FASE 2 — ANÁLISE SINTÁTICA  |  AST gerada")
    print(f"{'═'*60}")
    _repr_ast(ast, nivel=0)

def _repr_ast(no, nivel):
    """Exibe a AST de forma indentada e legível."""
    indent = "  " * nivel
    nome   = type(no).__name__

    from ast_nodes import (Program, Block, Assignment, IfStatement, WhileLoop,
                           PrintStatement, BinaryOp, UnaryOp, IntegerLiteral, Variable)

    if isinstance(no, Program):
        print(f"{indent}Program")
        for s in no.statements:
            _repr_ast(s, nivel + 1)

    elif isinstance(no, Block):
        print(f"{indent}Block")
        for s in no.statements:
            _repr_ast(s, nivel + 1)

    elif isinstance(no, Assignment):
        print(f"{indent}Assignment  [{no.name}]")
        _repr_ast(no.value, nivel + 1)

    elif isinstance(no, IfStatement):
        print(f"{indent}If")
        print(f"{indent}  condição:")
        _repr_ast(no.condition, nivel + 2)
        print(f"{indent}  then:")
        _repr_ast(no.then_block, nivel + 2)
        if no.else_block:
            print(f"{indent}  else:")
            _repr_ast(no.else_block, nivel + 2)

    elif isinstance(no, WhileLoop):
        print(f"{indent}While")
        print(f"{indent}  condição:")
        _repr_ast(no.condition, nivel + 2)
        print(f"{indent}  corpo:")
        _repr_ast(no.body, nivel + 2)

    elif isinstance(no, PrintStatement):
        print(f"{indent}Print")
        _repr_ast(no.expression, nivel + 1)

    elif isinstance(no, BinaryOp):
        print(f"{indent}BinaryOp  [{no.op}]")
        _repr_ast(no.left,  nivel + 1)
        _repr_ast(no.right, nivel + 1)

    elif isinstance(no, UnaryOp):
        print(f"{indent}UnaryOp  [{no.op}]")
        _repr_ast(no.operand, nivel + 1)

    elif isinstance(no, IntegerLiteral):
        print(f"{indent}IntegerLiteral  [{no.value}]")

    elif isinstance(no, Variable):
        print(f"{indent}Variable  [{no.name}]")

    else:
        print(f"{indent}{repr(no)}")

def _imprimir_codigo(codigo):
    print(f"\n{'═'*60}")
    print("  FASE 3 — GERAÇÃO DE CÓDIGO  |  Código intermediário (TAC)")
    print(f"{'═'*60}")
    for linha in codigo.splitlines():
        # Rótulos aparecem sem indentação; demais instruções com recuo
        if linha.endswith(':'):
            print(f"  {linha}")
        else:
            print(f"      {linha}")
    print(f"{'═'*60}\n")


# ---------------------------------------------------------------------------
# Ponto de entrada CLI
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) != 2:
        print("Uso: python compiler.py <arquivo.tiny>")
        print("Exemplo: python compiler.py ../examples/exemplo1_aritmetica.tiny")
        sys.exit(1)

    caminho = sys.argv[1]

    if not os.path.isfile(caminho):
        print(f"Erro: arquivo não encontrado: {caminho}")
        sys.exit(1)

    compilador = CompiladorTinyScript()

    print(f"\n  Compilando: {caminho}")
    print(SEPARADOR)

    try:
        resultado = compilador.compilar_arquivo(caminho)
    except ErroLexico as e:
        print(f"\n  *** {e}")
        sys.exit(1)
    except ErroSintatico as e:
        print(f"\n  *** {e}")
        sys.exit(1)

    _imprimir_tokens(resultado['tokens'])
    _imprimir_ast(resultado['ast'])
    _imprimir_codigo(resultado['codigo'])


if __name__ == '__main__':
    main()
