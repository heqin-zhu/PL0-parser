from token_scanner import genToken, Token


def test_token_scanner():
    target = [
        Token("NAME", "func", 1),
        Token("NAME", "fib", 1),
        Token("LEFT", "(", 1),
        Token("NAME", "n", 1),
        Token("RIGHT", ")", 1),
        Token("NAME", "begin", 1),
        Token("NAME", "if", 1),
        Token("NAME", "n", 1),
        Token("EQ", "=", 1),
        Token("NUM", "1", 1),
        Token("OR", "||", 1),
        Token("NAME", "n", 1),
        Token("EQ", "=", 1),
        Token("NUM", "2", 1),
        Token("NAME", "then", 1),
        Token("NAME", "return", 1),
        Token("NUM", "1", 1),
        Token("SEMICOLON", ";", 1),
        Token("NAME", "return", 1),
        Token("NAME", "fib", 1),
        Token("LEFT", "(", 1),
        Token("NAME", "n", 1),
        Token("SUB", "-", 1),
        Token("NUM", "1", 1),
        Token("RIGHT", ")", 1),
        Token("ADD", "+", 1),
        Token("NAME", "fib", 1),
        Token("LEFT", "(", 1),
        Token("NAME", "n", 1),
        Token("SUB", "-", 1),
        Token("NUM", "2", 1),
        Token("RIGHT", ")", 1),
        Token("SEMICOLON", ";", 1),
        Token("NAME", "end", 1),
        Token("SEMICOLON", ";", 1),
    ]

    s = 'func fib(n) begin if n=1 || n=2 then return 1; return fib(n-1)+fib(n-2); end;'
    results = genToken(s)
    assert target == list(results)


if __name__ == "__main__":
    test_token_scanner()
