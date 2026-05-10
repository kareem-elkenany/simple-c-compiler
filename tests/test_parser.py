"""
Parser test suite — runs scanner.exe then parser.py for each case.
Usage: python tests/test_parser.py  (from project root)
"""
#This is nothing more than an AI generated Tester to check Error handling in the parser. Only a sanity check to see if the parser can handle simple errors
import subprocess
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCANNER_DIR  = os.path.join(BASE_DIR, "scanner")
SCANNER_EXE  = os.path.join(SCANNER_DIR, "scanner.exe")
INPUT_FILE   = os.path.join(SCANNER_DIR, "input.txt")
PARSER_SCRIPT = os.path.join(BASE_DIR, "parser", "parser.py")

GREEN = "\033[92m"
RED   = "\033[91m"
RESET = "\033[0m"

passed = 0
failed = 0


def run_test(name, code, expect_success, expected_fragment=None):
    global passed, failed

    with open(INPUT_FILE, "w", encoding="utf-8") as f:
        f.write(code)

    # --- scanner ---
    scan = subprocess.run(
        [SCANNER_EXE],
        cwd=SCANNER_DIR,
        capture_output=True, text=True
    )

    if scan.returncode != 0:
        # Lexical error from the scanner itself
        err = scan.stderr.strip()
        if not expect_success:
            ok = (expected_fragment is None) or (expected_fragment.lower() in err.lower())
            _report(name, ok, err)
        else:
            _report(name, False, f"Unexpected scanner error: {err}")
        return

    # --- parser ---
    parse = subprocess.run(
        [sys.executable, PARSER_SCRIPT],
        capture_output=True, text=True
    )

    output = (parse.stdout + parse.stderr).strip()

    if expect_success:
        ok = "PARSING SUCCESSFUL" in output
        _report(name, ok, None if ok else f"Expected success, got:\n  {output}")
    else:
        is_error = "PARSING SUCCESSFUL" not in output
        if not is_error:
            _report(name, False, "Expected a parse error but parsing succeeded")
            return
        # Extract the error line for display
        error_line = next(
            (l for l in output.splitlines() if "error" in l.lower() or "Error" in l),
            output
        )
        if expected_fragment:
            ok = expected_fragment.lower() in output.lower()
            _report(name, ok,
                    error_line if ok else
                    f"Wrong error message.\n  Expected fragment: '{expected_fragment}'\n  Got: {error_line}")
        else:
            _report(name, True, error_line)


def _report(name, ok, detail):
    global passed, failed
    status = f"{GREEN}PASS{RESET}" if ok else f"{RED}FAIL{RESET}"
    print(f"  [{status}] {name}")
    if detail:
        for line in detail.splitlines():
            print(f"         {line}")
    if ok:
        passed += 1
    else:
        failed += 1


# ============================================================
print("=" * 65)
print(" PARSER TEST SUITE")
print("=" * 65)

# ----------------------------------------------------------------
print("\n--- VALID PROGRAMS ---\n")
# ----------------------------------------------------------------

run_test(
    "01. Simple assignment",
    "x is 2",
    expect_success=True,
)

run_test(
    "02. Multiple assignments",
    "x is 2\nw is 3\ny is x plus w",
    expect_success=True,
)

run_test(
    "03. Read and show",
    "read x\nshow x",
    expect_success=True,
)

run_test(
    "04. Arithmetic precedence  (* before +)",
    "y is 2 plus 3 multiplied by 4",
    expect_success=True,
)

run_test(
    "05. Parentheses override precedence",
    "y is (2 plus 3) multiplied by 4",
    expect_success=True,
)

run_test(
    "06. If — greater than",
    "x is 5\nif x greater than 3 {\ny is 1\n}",
    expect_success=True,
)

run_test(
    "07. If — less than or equal",
    "x is 5\nif x less than or equal 5 {\nshow x\n}",
    expect_success=True,
)

run_test(
    "08. If — greater than or equal",
    "x is 5\nif x greater than or equal 5 {\nshow x\n}",
    expect_success=True,
)

run_test(
    "09. If — equal",
    "x is 5\nif x equal 5 {\nshow x\n}",
    expect_success=True,
)

run_test(
    "10. If — less than",
    "x is 5\nif x less than 10 {\nshow x\n}",
    expect_success=True,
)

run_test(
    "11. While loop",
    "x is 0\nwhile x less than 5 {\nx is x plus 1\n}",
    expect_success=True,
)

run_test(
    "12. Nested if inside while",
    "x is 0\nwhile x less than 10 {\nif x greater than 5 {\nshow x\n}\nx is x plus 1\n}",
    expect_success=True,
)

run_test(
    "13. String assignment and show",
    'x is "hello"\nshow x',
    expect_success=True,
)

run_test(
    "14. Division and subtraction",
    "y is 10 minus 4 divided by 2",
    expect_success=True,
)

run_test(
    "15. Chained additions",
    "y is 1 plus 2 plus 3 plus 4",
    expect_success=True,
)

run_test(
    "16. Complex expression in condition",
    "x is 3\ny is 4\nif x plus 1 equal y {\nshow x\n}",
    expect_success=True,
)

run_test(
    "17. Deeply nested arithmetic",
    "z is (2 plus 3) multiplied by (4 minus 1) divided by 5",
    expect_success=True,
)

run_test(
    "18. Read then compute then show",
    "read x\nread y\nz is x plus y\nshow z",
    expect_success=True,
)

# ----------------------------------------------------------------
print("\n--- ERROR PROGRAMS ---\n")
# ----------------------------------------------------------------

run_test(
    "19. Stray identifier after expression  (y is x w)",
    "y is x w",
    expect_success=False,
    expected_fragment="Expected EOL or EOF after statement",
)

run_test(
    "20. Stray token in block  (y is x w inside while)",
    "while x less than 5 {\ny is x w\nx is x plus 1\n}",
    expect_success=False,
    expected_fragment="Expected EOL or EOF after statement",
)

run_test(
    "21. Lone identifier — missing 'is'  (x alone)",
    "x",
    expect_success=False,
    expected_fragment="Expected ASSIGN",
)

run_test(
    "22. Missing expression after assign  (y is)",
    "y is",
    expect_success=False,
    expected_fragment="Unexpected token",
)

run_test(
    "23. Missing operand after operator  (y is x plus)",
    "y is x plus",
    expect_success=False,
    expected_fragment="Unexpected token",
)

run_test(
    "24. Number as statement start  (5 is x)",
    "5 is x",
    expect_success=False,
    expected_fragment="Unexpected token NUMBER",
)

run_test(
    "25. Unclosed block — missing }",
    "if x equal 2 {\ny is 3",
    expect_success=False,
    expected_fragment="Unexpected token",
)

run_test(
    "26. Missing relational operator in if  (if x { ... })",
    "if x {\ny is 3\n}",
    expect_success=False,
    expected_fragment="Expected comparison operator",
)

run_test(
    "27. show without argument",
    "show",
    expect_success=False,
    expected_fragment="Unexpected token",
)

run_test(
    "28. read without identifier",
    "read",
    expect_success=False,
    expected_fragment="Expected IDENTIFIER",
)

run_test(
    "29. Invalid character  (@)",
    "x is @",
    expect_success=False,
    expected_fragment="Unexpected character",
)

run_test(
    "30. Two stray tokens after expression  (y is x w z)",
    "y is x w z",
    expect_success=False,
    expected_fragment="Expected EOL or EOF after statement",
)

# ----------------------------------------------------------------
print("\n" + "=" * 65)
total = passed + failed
print(f" Results: {passed}/{total} passed", end="")
if failed:
    print(f"  ({RED}{failed} failed{RESET})")
else:
    print(f"  {GREEN}All passed!{RESET}")
print("=" * 65)
