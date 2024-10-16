import time

# Gramática en CNF
grammar = {
    "S": [["NP", "VP"]],
    "VP": [["VP", "PP"], ["V", "NP"], ["cooks"], ["drinks"], ["eats"], ["cuts"]],
    "PP": [["P", "NP"]],
    "NP": [["Det", "N"], ["he"], ["she"]],
    "V": [["cooks"], ["drinks"], ["eats"], ["cuts"]],
    "P": [["in"], ["with"]],
    "N": [["cat"], ["dog"], ["beer"], ["cake"], ["juice"], ["meat"], ["soup"], ["fork"], ["knife"], ["oven"], ["spoon"]],
    "Det": [["a"], ["the"]]
}

# Función para invertir la gramática (por terminal y por lista de no terminales)
def convert_grammar(grammar):
    reverse_grammar = {}
    for head, bodies in grammar.items():
        for body in bodies:
            key = tuple(body)
            if key in reverse_grammar:
                reverse_grammar[key].append(head)
            else:
                reverse_grammar[key] = [head]
    return reverse_grammar

# Gramática invertida
reverse_grammar = convert_grammar(grammar)

# Algoritmo CYK
def cyk_parse(sentence, grammar):
    words = sentence.split()
    n = len(words)
    
    # Crear tabla CYK
    table = [[set() for _ in range(n)] for _ in range(n)]
    
    # Llenar la primera fila de la tabla con las producciones de un solo terminal
    for i, word in enumerate(words):
        for lhs, bodies in grammar.items():
            for body in bodies:
                if body == [word]:
                    table[i][i].add(lhs)
    
    # Llenar la tabla usando la programación dinámica
    for span in range(2, n + 1):
        for start in range(n - span + 1):
            end = start + span - 1
            for mid in range(start, end):
                for X in table[start][mid]:
                    for Y in table[mid + 1][end]:
                        if (X, Y) in reverse_grammar:
                            table[start][end].update(reverse_grammar[(X, Y)])
    
    return table

# Función para verificar si la frase es parte del lenguaje
def is_sentence_in_language(sentence, grammar):
    start_time = time.time()
    table = cyk_parse(sentence, grammar)
    parsing_time = time.time() - start_time
    
    # Verificar si el símbolo inicial 'S' está en la celda superior derecha de la tabla
    if 'S' in table[0][-1]:
        print("SÍ, la frase pertenece al lenguaje.")
    else:
        print("NO, la frase no pertenece al lenguaje.")
    
    print(f"Tiempo de parsing: {parsing_time:.6f} segundos.")
    return table

# Función para construir el árbol de análisis sintáctico (parse tree)
def build_parse_tree(table, sentence, grammar):
    words = sentence.split()
    n = len(words)
    
    def construct_tree(start, end, symbol):
        if start == end:
            return (symbol, words[start])
        
        for mid in range(start, end):
            for X in table[start][mid]:
                for Y in table[mid + 1][end]:
                    if (X, Y) in reverse_grammar and symbol in reverse_grammar[(X, Y)]:
                        left_tree = construct_tree(start, mid, X)
                        right_tree = construct_tree(mid + 1, end, Y)
                        return (symbol, left_tree, right_tree)
    
    if 'S' in table[0][n - 1]:
        return construct_tree(0, n - 1, 'S')
    else:
        return None

# Función auxiliar para imprimir el parse tree
def print_parse_tree(tree, indent=0):
    if tree is None:
        return
    if isinstance(tree, tuple):
        print("  " * indent + tree[0])
        if len(tree) > 1:
            for subtree in tree[1:]:
                print_parse_tree(subtree, indent + 1)
    else:
        print("  " * indent + tree)

# Ejemplo de uso
sentence = "She eats a cake with a fork"
table = is_sentence_in_language(sentence, grammar)

# Construcción e impresión del árbol de análisis sintáctico
parse_tree = build_parse_tree(table, sentence, grammar)
if parse_tree:
    print("Árbol de análisis sintáctico:")
    print_parse_tree(parse_tree)
else:
    print("No se pudo construir el árbol de análisis sintáctico.")
