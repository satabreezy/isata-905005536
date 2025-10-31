import os
from stack import Stack
# ---------- tokeniser ----------
def tokenize(expr: str):
    i, n = 0, len(expr)
    while i < n:
        ch = expr[i]
        if ch.isspace():
            i += 1
            continue
        if ch in '()+-*/%':
            i += 1
            yield ch
            continue
        if ch == '/' and i + 1 < n and expr[i + 1] == '/':
            i += 2
            yield '//'
            continue
        if ch == '*' and i + 1 < n and expr[i + 1] == '*':
            i += 2
            yield '**'
            continue
        if ch.isdigit():
            j = i
            while j < n and expr[j].isdigit():
                j += 1
            yield expr[i:j]
            i = j
            continue
        raise ValueError(f"Bad char '{ch}'")

# ---------- precedence ----------
PREC = {'+': 1, '-': 1, '*': 2, '/': 2, '//': 2, '%': 2, '**': 3}
RIGHT_ASSOC = {'**'}

# ---------- apply operator ----------
def apply_op(op: str, b: int, a: int) -> int:
    if op == '+': return a + b
    if op == '-': return a - b
    if op == '*': return a * b
    if op == '/':
        if b == 0: raise ZeroDivisionError
        return a // b if a % b == 0 else a / b
    if op == '//':
        if b == 0: raise ZeroDivisionError
        return a // b
    if op == '%':
        if b == 0: raise ZeroDivisionError
        return a % b
    if op == '**': return a ** b
    raise ValueError("Unknown operator")

# ---------- evaluate ----------
def evaluate(expr: str) -> int:
    vals = Stack()
    ops = Stack()
    tokens = list(tokenize(expr))
    unary_ok = True

    def reduce_once():
        op = ops.pop()
        b = vals.pop()
        a = vals.pop()
        vals.push(apply_op(op, b, a))

    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if tok == '(':
            ops.push(tok); unary_ok = True; i += 1
        elif tok == ')':
            while not ops.is_empty() and ops.peek() != '(':
                reduce_once()
            if ops.is_empty() or ops.peek() != '(':
                raise ValueError("Mismatched parentheses")
            ops.pop(); unary_ok = False; i += 1
        elif tok in '+-' and unary_ok:
            if tok == '-':
                vals.push(-1); ops.push('*')
            unary_ok = False; i += 1
        elif tok in PREC:
            prec_tok = PREC[tok]
            while (not ops.is_empty() and ops.peek() != '(' and
                   (PREC[ops.peek()] > prec_tok or
                    (PREC[ops.peek()] == prec_tok and tok not in RIGHT_ASSOC))):
                reduce_once()
            ops.push(tok); unary_ok = True; i += 1
        else:  # number
            vals.push(int(tok)); unary_ok = False; i += 1

    while not ops.is_empty():
        if ops.peek() in '()':
            raise ValueError("Mismatched parentheses")
        reduce_once()

    if vals.size() != 1:
        raise ValueError("Malformed expression")
    return vals.pop()

# ---------- file I/O ----------
def main():
    IN, OUT = 'input.txt', 'output.txt'
    if not os.path.isfile(IN):
        with open(IN, 'w') as f:
            f.write("3 + 4 * 2 / ( 1 - 5 )\n2 ** 3 ** 2\n-5 + 12 % 5\n10 / 0\n")

    with open(IN) as fin, open(OUT, 'w') as fout:
        for raw in fin:
            raw = raw.rstrip('\n')
            if not raw or raw.isspace():
                fout.write('\n')
                continue
            try:
                fout.write(f"{evaluate(raw)}\n")
            except Exception:
                fout.write("ERROR\n")

if __name__ == '__main__':
    main()