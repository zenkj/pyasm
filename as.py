from re import match, fullmatch, sub

# .byte 0, 0x10, 'ab"c\n', "a\nb'c", 'a'
# .utf8 0, "abc'd", 'def"s\'\n'
# 

def splitargs(argline):
    argline = fullmatch(r'(.*),?', argline).group(1)
    i = 0
    length = len(argline)

    if length == 0: return []

    single_quote = False
    double_quote = False
    rstack = []
    while i < length:
        c = argline[i]
        i += 1
        if single_quote:
            if c == '\\': i += 1
            elif c == "'": single_quote = False
        elif double_quote:
            if c == '\\': i += 1
            elif c == '"': double_quote = False
        else:
            if c == '(': rstack.append(')')
            elif c == '[': rstack.append(']')
            elif c == '{': rstack.append('}')
            elif c == ')' or c == ']' or c == '}':
                if len(rstack) == 0: raise ValueError
                if rstack[-1] != c: raise ValueError
                else: rstack.pop()
            elif c == '"': double_quote = True
            elif c == "'": single_quote = True
            elif c == '#':
                argline = argline[:i-1]
                break # ignore comment till end of line
            elif c == ',':
                if len(rstack) == 0: argline[i-1] = '\n'

    if len(rstack) > 0: raise ValueError

    return argline.split('\n')

def split(line):
    m = fullmatch(r'\s*([.\w]+)\s+(.*)\s*', line)
    if not m: raise ValueError
    opcode = m.group(1)
    args = splitargs(m.group(2))
    return opcode, args

def doline(line):
    # ignore empty line
    if fullmatch(r'\s*', line):
        return

    # translate label
    m = fullmatch(r'\s*(@?\w+)\s*:\s*', line)
    if m:
        line = '.label ' + m.group(1)

    # split statement
    opcode, args = split(line)

    # translate type


def translate(file, out):
    with open(file) as f:
        for line in f:
            doline(line)

if __name__ == '__main__':
    from sys import stdout, argv
    if len(argv) != 2:
        print("Usage: {} xxx.as".format(argv[0]))
    else:
        translate(argv[1], stdout)
