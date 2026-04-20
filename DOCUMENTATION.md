# Simple C Compiler Documentation

This document explains the core workings of the `parser.py` file, its recent upgrades for accurate syntax error reporting, and the corresponding changes applied to the scanner (`lexer.l`).

## 1. Scanner (`lexer.l`) Updates

The scanner (Lexer) splits a sequence of characters into a sequence of semantic tokens. 

### What We Changed
Originally, the scanner emitted standard 2-tuple tokens without line numbers: `(value, TYPE)`. While fast, this resulted in a loss of context—the parser didn't know which line a token originally belonged to when a syntax error occurred.

We utilized Flex's built-in `%option yylineno` to track line counts natively. Every rule matching an expression was updated to dump a 3-tuple including the current line dynamically.

**Example Change:**
```diff
-  fprintf(tokenFile, "(%s, IDENTIFIER)\n", yytext);
+  fprintf(tokenFile, "(%d, %s, IDENTIFIER)\n", yylineno, yytext);
```
Outputs: `(1, result, IDENTIFIER)`


## 2. Parser (`parser.py`) Internal Mechanics

The parser in `parser.py` implements a **Recursive Descent Parser**, which belongs to the top-down parsing family. It builds the Abstract Syntax Tree (AST) by stepping through the tokens.

### How The File Works
- **Node Class (`Node`)**: The foundational building block of the Abstract Syntax Tree. Each Node contains a value (like `ASSIGN` or `PLUS`) and a list of internal `children` nodes that trace down recursively.
- **Tokenizer (`read_tokens`)**: Opens `tokens.txt` produced by the scanner and parses the contents utilizing a regex: `^\((\d+),\s*(.*?),\s*(.*?)\)$`. It assembles and returns a usable Python list of `(TYPE, value, line_number)`.
- **Parsing Flow**: The `parse_program` function kicks off the process. It routes through various "dispatcher" functions (`parse_statement`) mapping identical grammar rules out of the language:
    - **`parse_assign()`**: Triggers over an `IDENTIFIER` mapping assignment bindings (e.g. `x is 10`).
    - **`parse_if()` & `parse_while()`**: Resolves loops and conditions recursively reading into its own internal `BLOCK` boundaries ` { } `.
    - **`parse_expression() & parse_term()`**: Safely resolves **operator precedence**, parsing multiplication and division inside terms before processing additions and subtractions across the broader expressions!

### Handling Syntax Errors
We updated the parser mechanics to intercept the injected `line_number` emitted by our updated scanner. 

Functions like `match()` and the base error fallbacks within `parse_statement` and `parse_factor` extract index `2` of the current token:
```python
raise SyntaxError(f"Unexpected token {token[0]} at line {token[2]}")
```
Because `EOF` scenarios dynamically break index constraints, `Parser.current()` checks the end explicitly block tracing back the previous token's valid line index:
```python
last_line = self.tokens[-1][2] if self.tokens else 1
return ("EOF", "", last_line)
```
This guarantees accurate syntax error messages pointing exactly to the specific offending character lines without blindly relying on positional array counts.
