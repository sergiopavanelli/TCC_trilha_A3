# =============================================================================
# codegen.py — Gerador de Código Intermediário do compilador TinyScript
# Disciplina: Teoria da Computação e Compiladores — UNIBH 2026/1
# Professora: Charlene Cássia de Resende
# =============================================================================

"""
O gerador de código é a terceira fase do compilador. Ele percorre a AST produzida
pelo parser (usando o padrão VISITOR) e emite instruções de código intermediário
no formato de CÓDIGO DE TRÊS ENDEREÇOS (Three-Address Code — TAC).

Formato das instruções geradas:
  - Atribuição simples:  _t0 = 42
  - Operação binária:    _t1 = _t0 + x
  - Negação unária:      _t2 = - _t1
  - Impressão:           PRINT _t1
  - Desvio condicional:  IF _t1 < 10 GOTO L0
  - Desvio incondicional: GOTO L1
  - Rótulo:              L0:
"""

from ast_nodes import (
    Program, Block, Assignment, IfStatement, WhileLoop, PrintStatement,
    BinaryOp, UnaryOp, IntegerLiteral, Variable,
)


class GeradorDeCodigo:
    """
    Percorre a AST e produz código intermediário de três endereços.

    Utiliza o padrão Visitor: para cada tipo de nó existe um método
    visitar_<NomeDoNo> que retorna o nome do temporário onde o resultado
    foi armazenado (quando aplicável).
    """

    def __init__(self):
        self._instrucoes: list  = []  # lista de strings com as instruções
        self._contador_temp: int = 0  # contador de variáveis temporárias
        self._contador_label: int = 0  # contador de rótulos (labels)

    # ------------------------------------------------------------------
    # Interface pública
    # ------------------------------------------------------------------

    def gerar(self, ast) -> str:
        """
        Recebe a AST raiz (Program) e retorna o código intermediário
        como uma string com uma instrução por linha.
        """
        self._instrucoes = []
        self._contador_temp  = 0
        self._contador_label = 0
        self._visitar(ast)
        return '\n'.join(self._instrucoes)

    # ------------------------------------------------------------------
    # Despacho (dispatch) — decide qual método visitar chamar
    # ------------------------------------------------------------------

    def _visitar(self, no):
        """Despacha a visita para o método correto com base no tipo do nó."""
        nome_metodo = '_visitar_' + type(no).__name__
        metodo = getattr(self, nome_metodo, None)
        if metodo is None:
            raise NotImplementedError(
                f"GeradorDeCodigo não suporta nó do tipo: {type(no).__name__}"
            )
        return metodo(no)

    # ------------------------------------------------------------------
    # Auxiliares
    # ------------------------------------------------------------------

    def _novo_temp(self) -> str:
        """Gera um novo nome de variável temporária: _t0, _t1, ..."""
        nome = f"_t{self._contador_temp}"
        self._contador_temp += 1
        return nome

    def _novo_label(self) -> str:
        """Gera um novo rótulo: L0, L1, ..."""
        nome = f"L{self._contador_label}"
        self._contador_label += 1
        return nome

    def _emitir(self, instrucao: str):
        """Adiciona uma instrução à lista de saída."""
        self._instrucoes.append(instrucao)

    def _emitir_label(self, label: str):
        """Emite um rótulo (sem indentação para facilitar visualização)."""
        self._instrucoes.append(f"{label}:")

    # ------------------------------------------------------------------
    # Visitores — Statements
    # ------------------------------------------------------------------

    def _visitar_Program(self, no: Program):
        """Visita todos os statements do programa."""
        for stmt in no.statements:
            self._visitar(stmt)

    def _visitar_Block(self, no: Block):
        """Visita todos os statements de um bloco."""
        for stmt in no.statements:
            self._visitar(stmt)

    def _visitar_Assignment(self, no: Assignment):
        """
        Atribuição: avalia a expressão e armazena na variável.
        Exemplo:  x = _t0 + _t1  →  instrução:  x = _t0 + _t1
        """
        temp = self._visitar(no.value)
        self._emitir(f"{no.name} = {temp}")

    def _visitar_IfStatement(self, no: IfStatement):
        """
        if ( cond ) { then } else { else }

        Padrão gerado:
          <avaliar cond em _tX>
          IF NOT _tX GOTO L_else
          <then block>
          GOTO L_fim
          L_else:
          <else block>        ← só se houver else
          L_fim:
        """
        temp_cond = self._visitar(no.condition)

        label_else = self._novo_label()
        label_fim  = self._novo_label()

        # Se a condição for falsa, pula para o else (ou fim)
        self._emitir(f"IF NOT {temp_cond} GOTO {label_else}")

        # Bloco then
        self._visitar(no.then_block)
        self._emitir(f"GOTO {label_fim}")

        # Rótulo else
        self._emitir_label(label_else)
        if no.else_block is not None:
            self._visitar(no.else_block)

        # Rótulo fim
        self._emitir_label(label_fim)

    def _visitar_WhileLoop(self, no: WhileLoop):
        """
        while ( cond ) { body }

        Padrão gerado:
          L_inicio:
          <avaliar cond em _tX>
          IF NOT _tX GOTO L_fim
          <body>
          GOTO L_inicio
          L_fim:
        """
        label_inicio = self._novo_label()
        label_fim    = self._novo_label()

        self._emitir_label(label_inicio)
        temp_cond = self._visitar(no.condition)
        self._emitir(f"IF NOT {temp_cond} GOTO {label_fim}")
        self._visitar(no.body)
        self._emitir(f"GOTO {label_inicio}")
        self._emitir_label(label_fim)

    def _visitar_PrintStatement(self, no: PrintStatement):
        """print(expr) → PRINT <temp>"""
        temp = self._visitar(no.expression)
        self._emitir(f"PRINT {temp}")

    # ------------------------------------------------------------------
    # Visitores — Expressões (retornam nome do temporário com resultado)
    # ------------------------------------------------------------------

    def _visitar_BinaryOp(self, no: BinaryOp) -> str:
        """
        Gera código para operação binária.
        Exemplo: a + b  →  _t2 = a + b
        """
        esq  = self._visitar(no.left)
        dir_ = self._visitar(no.right)
        temp = self._novo_temp()
        self._emitir(f"{temp} = {esq} {no.op} {dir_}")
        return temp

    def _visitar_UnaryOp(self, no: UnaryOp) -> str:
        """
        Gera código para operação unária (negação).
        Exemplo: -x  →  _t3 = - x
        """
        operando = self._visitar(no.operand)
        temp = self._novo_temp()
        self._emitir(f"{temp} = {no.op} {operando}")
        return temp

    def _visitar_IntegerLiteral(self, no: IntegerLiteral) -> str:
        """
        Literal inteiro: cria um temporário com o valor.
        Exemplo: 42  →  _t0 = 42
        """
        temp = self._novo_temp()
        self._emitir(f"{temp} = {no.value}")
        return temp

    def _visitar_Variable(self, no: Variable) -> str:
        """
        Variável: retorna o próprio nome (já existe no ambiente).
        Não emite instrução; apenas propaga o nome.
        """
        return no.name
