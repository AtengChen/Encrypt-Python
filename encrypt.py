#! python3

import argparse
import ast
import builtins
import keyword
import itertools
import string
import sys
import os

whitelist = set()

def convert(ind, n):
    if n > 1:
        return ["".join(pair) for pair in itertools.product(string.ascii_letters, repeat=n)][ind]
    else:
        return string.ascii_lowercase[ind]


def is_valid_variable(name, whitelist):
    return (
        name.isidentifier()
        and name not in dir(builtins)
        and not keyword.iskeyword(name)
        and name not in whitelist
        and not name.startswith("_")
    )


def parse_code(code_str, whitelist):
    tree = ast.parse(code_str)
    variables_list = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and is_valid_variable(node.name, whitelist):
            variables_list.add(node.name)
            for param in node.args.args:
                variables_list.add(param.arg)
        elif isinstance(node, ast.Name) and is_valid_variable(node.id, whitelist):
            variables_list.add(node.id)
        elif isinstance(node, ast.ImportFrom):
            add_module_functions_to_whitelist(node.module, is_module=True)
        elif isinstance(node, ast.Import):
            for m in node.names:
                add_module_functions_to_whitelist(m.name)
    return variables_list


def encrypt(code_str, complexity, verbose):
    global whitelist
    
    tree = ast.parse(code_str)
    
    variables_list = parse_code(code_str, whitelist)
    
    n = 0
    for i in variables_list:
        new_var = convert(n, complexity)
        if keyword.iskeyword(new_var):
            n += 1
            new_var = convert(n, complexity)
        if verbose:
            print(f"{i} -> {new_var}")
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id == i:
                node.id = new_var
            elif isinstance(node, ast.FunctionDef) and node.name == i:
                node.name = new_var
            elif isinstance(node, ast.arg) and node.arg == i:
                node.arg = new_var
        n += 1
    
    modified_code = ast.unparse(tree)
    
    modified_code = modified_code.replace("\n\n\n", "\n\n")
    
    return modified_code


def add_module_functions_to_whitelist(name, is_module=False):
    if is_module:
        module = __import__(name)
        functions = dir(module)
        for function in functions:
            whitelist.add(function)
    else:
        whitelist.add(name)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='A command-line tool to encrypt python code')
    
    parser.add_argument("filepath", type=str)
    parser.add_argument("complexity", default=3, type=int)
    parser.add_argument("--output", default=0)
    parser.add_argument("-v", "--verbose", action="store_true")
    
    args = parser.parse_args()
    
    filename = args.filepath
    complexity = args.complexity
    
    code = open(filename, encoding="UTF-8").read()
    encrypted_code = encrypt(code, complexity, args.verbose)
    
    if not args.output:
        print(encrypted_code)
        sys.exit()
    
    with open(args.output, "w", encoding="UTF-8") as f:
        f.write(encrypted_code)
