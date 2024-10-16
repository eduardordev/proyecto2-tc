import time
from collections import defaultdict


# Gramática original
grammar = {
    'S': [['NP', 'VP']],
    'VP': [['VP', 'PP'], ['V', 'NP'], ['cooks'], ['drinks'], ['eats'], ['cuts']],
    'PP': [['P', 'NP']],
    'NP': [['Det', 'N'], ['he'], ['she']],
    'V': [['cooks'], ['drinks'], ['eats'], ['cuts']],
    'P': [['in'], ['with']],
    'N': [['cat'], ['dog'], ['beer'], ['cake'], ['juice'], ['meat'], ['soup'], ['fork'], ['knife'], ['oven'], ['spoon']],
    'Det': [['a'], ['the']]
}


# Reemplazar terminales por producciones unitarias
terminals = set()
for productions in grammar.values():
    for prod in productions:
        for symbol in prod:
            if symbol.islower():
                terminals.add(symbol)

# Crear variables para los terminales
terminal_rules = {}
for t in terminals:
    terminal_rules[f'T_{t}'] = [[t]]

# Actualizar la gramática reemplazando terminales
def replace_terminals(grammar):
    new_grammar = {}
    for lhs, productions in grammar.items():
        new_productions = []
        for prod in productions:
            new_prod = []
            for symbol in prod:
                if symbol in terminals:
                    new_prod.append(f'T_{symbol}')
                else:
                    new_prod.append(symbol)
            new_productions.append(new_prod)
        new_grammar[lhs] = new_productions
    return new_grammar

grammar = replace_terminals(grammar)
grammar.update(terminal_rules)

# Convertir la gramática a Forma Normal de Chomsky
def convert_to_cnf(grammar):
    cnf_grammar = {}
    new_var_count = 1
    for lhs in grammar:
        cnf_grammar[lhs] = []
        for prod in grammar[lhs]:
            if len(prod) <= 2:
                cnf_grammar[lhs].append(prod)
            else:
                prev_var = prod[0]
                for i in range(1, len(prod) - 1):
                    new_var = f'X{new_var_count}'
                    new_var_count += 1
                    cnf_grammar.setdefault(prev_var, []).append([prod[i], new_var])
                    prev_var = new_var
                cnf_grammar.setdefault(prev_var, []).append([prod[-2], prod[-1]])
    return cnf_grammar

grammar = convert_to_cnf(grammar)

# CYK (Cocke-Younger-Kasami) parsing de gramática CFG
def cyk(word, grammar):
    n = len(word)
    table = [[set() for _ in range(n)] for _ in range(n)]
    inverse_rules = defaultdict(set)
    for lhs in grammar:
        for rhs in grammar[lhs]:
            inverse_rules[tuple(rhs)].add(lhs)

    # Inicializar la tabla
    for i in range(n):
        for lhs in inverse_rules.get((word[i],), []):
            table[i][i].add(lhs)

    # Rellenar la tabla
    for l in range(2, n + 1):
        for i in range(n - l + 1):
            j = i + l - 1
            for k in range(i, j):
                for b in table[i][k]:
                    for c in table[k + 1][j]:
                        for lhs in inverse_rules.get((b, c), []):
                            table[i][j].add(lhs)
    accepted = 'S' in table[0][n - 1]
    return accepted, table

# Parse tree
def build_parse_tree(table, word, grammar):
    n = len(word)
    parse_trees = [[[] for _ in range(n)] for _ in range(n)]
    inverse_rules = defaultdict(list)
    for lhs in grammar:
        for rhs in grammar[lhs]:
            inverse_rules[tuple(rhs)].append(lhs)

    for i in range(n):
        for lhs in inverse_rules.get((word[i],), []):
            parse_trees[i][i].append((lhs, word[i]))

    for l in range(2, n + 1): 
        for i in range(n - l + 1):
            j = i + l - 1
            for k in range(i, j):
                left_trees = parse_trees[i][k]
                right_trees = parse_trees[k + 1][j]
                for left in left_trees:
                    for right in right_trees:
                        b = left[0]
                        c = right[0]
                        for lhs in inverse_rules.get((b, c), []):
                            parse_trees[i][j].append((lhs, left, right))

    # Extraer los árboles que tienen 'S' como raíz
    parse_trees_with_s = [tree for tree in parse_trees[0][n - 1] if tree[0] == 'S']

    return parse_trees_with_s

def print_parse_tree(tree, indent=0):
    if len(tree) == 2:
        print('  ' * indent + f'{tree[0]} -> {tree[1]}')
    else:
        print('  ' * indent + f'{tree[0]}')
        print_parse_tree(tree[1], indent + 1)
        print_parse_tree(tree[2], indent + 1)


def main():

    sentence = input("Ingrese una frase en inglés: ")
    tokens = sentence.lower().split()

    # Mapear tokens a variables terminales
    word = []
    terminal_symbols = set()
    for lhs, productions in grammar.items():
        for prod in productions:
            if len(prod) == 1 and prod[0].startswith('T_'):
                terminal_symbols.add(prod[0][2:])

    for token in tokens:
        if token in terminal_symbols:
            word.append(f'T_{token}')
        else:
            print(f"Palabra desconocida en la gramática: {token}")
            return

    start_time = time.time()
    accepted, table = cyk(word, grammar)
    end_time = time.time()
    execution_time = end_time - start_time

    if accepted:
        print("SÍ, la frase pertenece al lenguaje.")
    else:
        print("NO, la frase no pertenece al lenguaje.")

    print(f"Tiempo de ejecución: {execution_time:.6f} segundos")

    if accepted:
        parse_trees = build_parse_tree(table, word, grammar)
        print("\nÁrbol de derivación:")
        for tree in parse_trees:
            print_parse_tree(tree)
            print("\n")

if __name__ == "__main__":
    main()
