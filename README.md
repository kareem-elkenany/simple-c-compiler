# Simple C Compiler (Frontend)

A compiler front-end that scans and parses a toy language and generates a syntax tree with GUI visualization.

---

## Project Architecture

Pipeline:

Input Code → Scanner (Flex) → tokens.txt → Parser → AST → Visualizer → GUI

---

## Project Structure

- scanner/ → Flex lexer (C)
- parser/ → Python parser (builds AST)
- gui/ → GUI + visualization
- data/
  - tiny_code.txt → input code
  - tokens.txt → generated tokens
- output/ → generated syntax tree image

---

## ⚙️ How It Works

1. User writes code in `data/tiny_code.txt`
2. Scanner (Flex) reads input and generates `tokens.txt`
3. Parser reads tokens and builds AST
4. AST is visualized and displayed in GUI

---

## Token Format

All tokens must follow this format:

(value, TYPE)

Example:
(5, NUMBER)
(x, ID)
(plus, PLUS)

---

## Team Responsibilities

- Scanner (Flex): Tokenization → writes tokens.txt
- Parser (Python): Builds AST from tokens
- GUI + Visualization: Displays tree
