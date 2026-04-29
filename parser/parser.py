import os
import re
from graphviz import Digraph

# =====================================================
# Recursive Decent Parser
# -Top Down
# -Leftmost Derivation
# =====================================================

# =====================================================
# AST Node
# =====================================================
class Node:
    def __init__(self, value, children=None):
        self.value = value
        self.children = children if children else []

    def pretty(self, level=0):
        indent = "  " * level
        result = indent + str(self.value) + "\n"
        for child in self.children:
            if isinstance(child, Node):
                result += child.pretty(level + 1)
            else:
                result += indent + "  " + str(child) + "\n"
        return result


def read_tokens(filename):
    if not os.path.exists(filename):
        raise FileNotFoundError(f"{filename} not found")

    tokens = []

    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            # Match (line, value, TYPE)
            match = re.match(r'^\((\d+),\s*(.*?),\s*(.*?)\)$', line)

            if match:
                line_no = int(match.group(1).strip())
                value = match.group(2).strip()
                token_type = match.group(3).strip()
                tokens.append((token_type, value, line_no))

    return tokens


# =====================================================
# Recursive Descent Parser
# =====================================================
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    # ---------------------------------
    def current(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        last_line = self.tokens[-1][2] if self.tokens else 1
        return ("EOF", "", last_line)

    # ---------------------------------
    def match(self, expected):
        token = self.current()

        if token[0] == expected:
            self.pos += 1
            return token

        raise SyntaxError(
            f"Expected {expected}, found {token[0]} ({token[1]}) at line {token[2]}"
        )

    # =====================================================
    # PROGRAM → statement_list
    # =====================================================
    def parse_program(self):
        return Node("PROGRAM", self.parse_statement_list())

    # =====================================================
    # statement_list → statement { EOL statement }
    # =====================================================
    def parse_statement_list(self):
        statements = []

        while self.current()[0] != "EOF":
            if self.current()[0] == "EOL":
                self.match("EOL")
                continue

            statements.append(self.parse_statement())

            while self.current()[0] == "EOL":
                self.match("EOL")

        return statements

    # =====================================================
    # statement dispatcher
    # =====================================================
    def parse_statement(self):
        token = self.current()[0]

        if token == "READ":
            return self.parse_read()

        elif token == "PRINT":
            return self.parse_print()

        elif token == "IDENTIFIER":
            return self.parse_assign()

        elif token == "IF":
            return self.parse_if()

        elif token == "WHILE":
            return self.parse_while()

        else:
            token = self.current()
            raise SyntaxError(f"Unexpected token {token[0]} at line {token[2]}")

    # =====================================================
    # read x
    # =====================================================
    def parse_read(self):
        self.match("READ")
        ident = self.match("IDENTIFIER")
        return Node("READ", [Node(ident[1])])

    # =====================================================
    # show expr
    # =====================================================
    def parse_print(self):
        self.match("PRINT")
        expr = self.parse_expression()
        return Node("PRINT", [expr])

    # =====================================================
    # x is expr
    # =====================================================
    def parse_assign(self):
        ident = self.match("IDENTIFIER")
        self.match("ASSIGN")
        expr = self.parse_expression()
        return Node("ASSIGN", [Node(ident[1]), expr])

    # =====================================================
    # if condition { statements }
    # =====================================================
    def parse_if(self):
        self.match("IF")
        condition = self.parse_condition()

        self.match("OPENBRACE")
        body = self.parse_statement_list_inside_block()
        self.match("CLOSEBRACE")

        return Node("IF", [condition, Node("BLOCK", body)])

    # =====================================================
    # while condition { statements }
    # =====================================================
    def parse_while(self):
        self.match("WHILE")
        condition = self.parse_condition()

        self.match("OPENBRACE")
        body = self.parse_statement_list_inside_block()
        self.match("CLOSEBRACE")

        return Node("WHILE", [condition, Node("BLOCK", body)])

    # =====================================================
    # statements inside { }
    # =====================================================
    def parse_statement_list_inside_block(self):
        statements = []

        while self.current()[0] != "CLOSEBRACE":
            if self.current()[0] == "EOL":
                self.match("EOL")
                continue

            statements.append(self.parse_statement())

            while self.current()[0] == "EOL":
                self.match("EOL")

        return statements

    # =====================================================
    # condition → expr relop expr
    # =====================================================
    def parse_condition(self):
        left = self.parse_expression()

        op = self.current()[0]
        valid = [
            "LESSTHAN",
            "GREATERTHAN",
            "LESSOREQUAL",
            "GREATEROREQUAL",
            "EQUAL",
        ]

        if op not in valid:
            raise SyntaxError(f"Expected comparison operator at line {self.current()[2]}")

        self.match(op)

        right = self.parse_expression()

        return Node(op, [left, right])

    # =====================================================
    # expression → term { (+|-) term }
    # =====================================================
    def parse_expression(self):
        node = self.parse_term()

        while self.current()[0] in ("PLUS", "MINUS"):
            op = self.current()[0]
            self.match(op)
            right = self.parse_term()
            node = Node(op, [node, right])

        return node

    # =====================================================
    # term → factor { (*|/) factor }
    # =====================================================
    def parse_term(self):
        node = self.parse_factor()

        while self.current()[0] in ("MULTIPLICATION", "DIVISION"):
            op = self.current()[0]
            self.match(op)
            right = self.parse_factor()
            node = Node(op, [node, right])

        return node

    # =====================================================
    # factor → NUMBER | IDENTIFIER | STRING | ( expr )
    # =====================================================
    def parse_factor(self):
        token = self.current()

        if token[0] == "NUMBER":
            self.match("NUMBER")
            return Node(token[1])

        elif token[0] == "IDENTIFIER":
            self.match("IDENTIFIER")
            return Node(token[1])

        elif token[0] == "STRING":
            self.match("STRING")
            return Node(token[1])

        elif token[0] == "LEFTPAREN":
            self.match("LEFTPAREN")
            node = self.parse_expression()
            self.match("RIGHTPAREN")
            return node

        raise SyntaxError(f"Unexpected token {token[0]} at line {token[2]}")

# =====================================================
# AST Visualizer
# =====================================================
class ASTVisualizer:
    def __init__(self):
        self.graph = Digraph("AST", format="png")
        self.graph.attr(rankdir="TB")
        self.graph.attr("node", fontname="Arial", fontsize="12")
        self.node_count = 0

        self.statement_nodes = {
            "PROGRAM", "READ", "PRINT", "ASSIGN", "IF", "WHILE", "BLOCK"
        }

        self.expression_nodes = {
            "PLUS", "MINUS", "MULTIPLICATION", "DIVISION"
        }

        self.condition_nodes = {
            "LESSTHAN", "GREATERTHAN", "LESSOREQUAL",
            "GREATEROREQUAL", "EQUAL"
        }

    def get_shape(self, value):
        if value in self.statement_nodes:
            return "box"          # rectangle for statements
        elif value in self.expression_nodes:
            return "ellipse"      # oval for expressions
        elif value in self.condition_nodes:
            return "diamond"      # optional: diamond for conditions
        else:
            return "oval"         # identifiers, numbers, strings

    def new_id(self):
        self.node_count += 1
        return f"node{self.node_count}"

    def add_ast_node(self, ast_node, parent_id=None):
        current_id = self.new_id()

        self.graph.node(
            current_id,
            label=str(ast_node.value),
            shape=self.get_shape(ast_node.value)
        )

        if parent_id is not None:
            self.graph.edge(parent_id, current_id)

        for child in ast_node.children:
            if isinstance(child, Node):
                self.add_ast_node(child, current_id)
            else:
                child_id = self.new_id()
                self.graph.node(child_id, label=str(child), shape="oval")
                self.graph.edge(current_id, child_id)

    def render(self, ast_root, output_path):
        self.add_ast_node(ast_root)
        self.graph.render(output_path, cleanup=True)
        print(f"AST image exported to: {output_path}.png")

# =====================================================
# MAIN
# =====================================================
if __name__ == "__main__":
    try:
        # Get the project root folder
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # Input tokens file
        tokens_path = os.path.join(BASE_DIR, "scanner", "tokens.txt")

        # Output AST image path
        output_path = os.path.join(BASE_DIR, "output", "ast_output")

        tokens = read_tokens(tokens_path)

        parser = Parser(tokens)
        ast = parser.parse_program()

        print("===== PARSING SUCCESSFUL =====")
        print(ast.pretty())

        visualizer = ASTVisualizer()
        visualizer.render(ast, output_path)

    except Exception as e:
        print("ERROR:", e)