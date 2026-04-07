# 🖥️ Compilador TinyScript

> **Avaliação A3 — Teoria da Computação e Compiladores**  
> **UNIBH — 2026/1 | Professora: Charlene Cássia de Resende**  
> **Aluno:** Sérgio Pinton Pavanelli | **RA:** 123220202


Protótipo funcional de compilador para a linguagem **TinyScript** — uma linguagem imperativa minimalista criada para fins didáticos. O compilador cobre as três fases clássicas: **análise léxica**, **análise sintática** e **geração de código intermediário**.

---

## 📦 Estrutura do Repositório

```
TCC_trilha_A3/
│
├── 📄 README.md                        ← este arquivo
│
├── 📁 docs/                            ← documentação (entregáveis)
│   ├── 📝 01_estudo_de_caso.md         ← Entregável 1: estudo do CPython
│   ├── 🏛️  02_arquitetura_compilador.md ← Entregável 2: arquitetura do TinyScript
│   └── 📋 03_relatorio_final.md        ← Entregável 4: relatório final
│
├── 📁 src/                             ← código-fonte do compilador
│   ├── 🌳 ast_nodes.py                 ← nós da AST
│   ├── 🔍 lexer.py                     ← analisador léxico
│   ├── 🧩 parser.py                    ← analisador sintático
│   ├── ⚙️  codegen.py                   ← gerador de código TAC
│   └── 🚀 compiler.py                  ← orquestrador + CLI
│
└── 📁 examples/                        ← programas de exemplo em TinyScript
    ├── exemplo1_aritmetica.tiny        ← variáveis e operações aritméticas
    ├── exemplo2_condicional.tiny       ← estrutura if/else
    └── exemplo3_laco.tiny             ← laço while (soma e fatorial)
```

---

## ⚡ Como Executar

### Pré-requisitos

- Python 3.10 ou superior
- Nenhuma biblioteca externa necessária

### Compilando um arquivo TinyScript

```bash
cd src
python compiler.py ../examples/exemplo1_aritmetica.tiny
```

### Testando todos os exemplos

```bash
cd src
python compiler.py ../examples/exemplo1_aritmetica.tiny
python compiler.py ../examples/exemplo2_condicional.tiny
python compiler.py ../examples/exemplo3_laco.tiny
```

---

## 🔤 A Linguagem TinyScript

TinyScript é uma linguagem imperativa com:

| Construção | Sintaxe |
|---|---|
| Variável inteira | `x = 42;` |
| Atribuição | `resultado = a + b * 2;` |
| Impressão | `print(resultado);` |
| Condicional | `if (x > 0) { ... } else { ... }` |
| Laço | `while (i < 10) { ... }` |
| Comentário | `// texto ignorado` |

### 🔢 Operadores

| Tipo | Operadores |
|---|---|
| Aritméticos | `+`, `-`, `*`, `/` |
| Comparação | `==`, `!=`, `<`, `>`, `<=`, `>=` |
| Atribuição | `=` |
| Unário | `-` (negação) |

### 📝 Exemplo completo

```tiny
// Calcula o fatorial de 5
n = 5;
fat = 1;
while (n > 1) {
    fat = fat * n;
    n = n - 1;
}
print(fat);
```

---

## 🏗️ Arquitetura do Compilador

```
Código-fonte (.tiny)
        │
        ▼
  ┌─────────────┐
  │   LEXER     │  ← src/lexer.py
  │             │    Produz: List[Token]
  └──────┬──────┘
         │
         ▼
  ┌─────────────┐
  │   PARSER    │  ← src/parser.py + ast_nodes.py
  │             │    Produz: AST (Program)
  └──────┬──────┘
         │
         ▼
  ┌─────────────┐
  │   CODEGEN   │  ← src/codegen.py
  │             │    Produz: Código TAC (texto)
  └──────┬──────┘
         │
         ▼
   [Saída no terminal]
```

---

## 📄 Entregáveis

| # | Documento | Arquivo |
|---|---|---|
| 1 | Estudo de caso — CPython | `docs/01_estudo_de_caso.md` |
| 2 | Arquitetura do compilador TinyScript | `docs/02_arquitetura_compilador.md` |
| 3 | Protótipo funcional (léxico + sintático + codegen) | `src/` |
| 4 | Relatório final | `docs/03_relatorio_final.md` |

---

## 🧪 Saída esperada — exemplo

Executando `python compiler.py ../examples/exemplo1_aritmetica.tiny`:

```
════════════════════════════════════════════════════════════
  FASE 1 — ANÁLISE LÉXICA  |  Tokens produzidos
════════════════════════════════════════════════════════════
  [IDENT     ]  valor='a'             L3:C1
  [ASSIGN    ]  valor='='             L3:C3
  [INTEGER   ]  valor=10              L3:C5
  [SEMI      ]  valor=';'             L3:C7
  ...

════════════════════════════════════════════════════════════
  FASE 2 — ANÁLISE SINTÁTICA  |  AST gerada
════════════════════════════════════════════════════════════
  Program
    Assignment  [a]
      IntegerLiteral  [10]
  ...

════════════════════════════════════════════════════════════
  FASE 3 — GERAÇÃO DE CÓDIGO  |  Código intermediário (TAC)
════════════════════════════════════════════════════════════
      _t0 = 10
      a = _t0
      _t1 = 3
      b = _t1
      _t2 = a + b
      soma = _t2
      PRINT soma
  ...
```

---

## 📚 Referências Bibliográficas

- **AHO, A. V.; LAN, M. S.; SETHI, R.; ULLMAN, J. D.** Compiladores: princípios, técnicas e ferramentas. 2. ed. Pearson, 2008. *(Dragon Book)*
- **MENDEZ, P.; BLAUTH, P.** Linguagens formais e autômatos. 6. ed. Bookman, 2010.
- **SANTOS, P. R.; LANGLOIS, T.** Compiladores: da teoria à prática. LTC, 2019.
- **CPython Source.** github.com/python/cpython

---

> 🎓 Projeto desenvolvido como avaliação A3 — UNIBH 2026/1
