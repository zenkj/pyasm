from re import fullmatch

NORMAL = 0
SINGLE_QUOTE = 1
DOUBLE_QUOTE = 2
TRIPLE_SINGLE_QUOTE = 3
TRIPLE_DOUBLE_QUOTE = 6
ASSEMBLY = -1
TRIPLE_ASSEMBLY = -3
ASPYTHON = 4 # python in assembly

# NORMAL
#   SINGLE_QUOTE
#   DOUBLE_QUOTE
#   TRIPLE_SINGLE_QUOTE
#   TRIPLE_DOUBLE_QUOTE
#   ASSEMBLY
#     SINGLE_QUOTE
#     DOUBLE_QUOTE
#     ASPYTHON
#       SINGLE_QUOTE
#       DOUBLE_QUOTE
#   TRIPLE_ASSEMBLY
#     SINGLE_QUOTE
#     DOUBLE_QUOTE
#     ASPYTHON
#       SINGLE_QUOTE
#       DOUBLE_QUOTE

def translate(file, out):
    rstack = 0
    buf = []
    ss = [NORMAL] # state stack

    with open(file) as f:
        for line in f:
            m = fullmatch(r'(.*)(\n?)', line)
            line = m.group(1)
            eol = m.group(2)

            i = 0
            length = len(line)
            while i < length:
                c = line[i]
                i += 1
                if ss[-1] == NORMAL:
                    if c == "'":
                        buf.append(c)
                        if i+1 < length and line[i] == "'" and line[i+1] == "'":
                            ss.append(TRIPLE_SINGLE_QUOTE)
                            i += 2
                            buf.append("''")
                        else:
                            ss.append(SINGLE_QUOTE)
                    elif c == '"':
                        buf.append(c)
                        if i+1 < length and line[i] == '"' and line[i+1] == '"':
                            ss.append(TRIPLE_DOUBLE_QUOTE)
                            i += 2
                            buf.append('""')
                        else:
                            ss.append(DOUBLE_QUOTE)
                    elif c == '#':
                        buf.append(line[i-1:])
                        i = length
                    elif c == '$':
                        if i+1 < length and line[i] == '$' and line[i+1] == '$':
                            ss.append(TRIPLE_ASSEMBLY)
                            i += 2
                        else:
                            ss.append(ASSEMBLY)

                        buf.append("print('''")
                    else:
                        buf.append(c)
                elif ss[-1] == SINGLE_QUOTE:
                    buf.append(c)
                    if c == "'":
                        ss.pop()
                    elif c == '\\' and i < length:
                        buf.append(line[i])
                        i += 1
                elif ss[-1] == DOUBLE_QUOTE:
                    buf.append(c)
                    if c == '"':
                        ss.pop()
                    elif c == '\\' and i < length:
                        buf.append(line[i])
                        i += 1
                elif ss[-1] == TRIPLE_SINGLE_QUOTE:
                    buf.append(c)
                    if i+1 < length and c == "'" and line[i] == "'" and line[i+1] == "'":
                        buf.append("''")
                        ss.pop()
                        i += 2
                    elif c == '\\' and i < length:
                        buf.append(line[i])
                        i += 1
                elif ss[-1] == TRIPLE_DOUBLE_QUOTE:
                    buf.append(c)
                    if i+1 < length and c == '"' and line[i] == '"' and line[i+1] == '"':
                        buf.append('""')
                        ss.pop()
                        i += 2
                    elif c == '\\' and i < length:
                        buf.append(line[i])
                        i += 1
                elif ss[-1] == ASSEMBLY or ss[-1] == TRIPLE_ASSEMBLY:
                    if c == '#':
                        # ignore comment in assembly
                        i = length
                    elif c == "'":
                        buf.append(c)
                        ss.append(SINGLE_QUOTE)
                    elif c == '"':
                        buf.append(c)
                        ss.append(DOUBLE_QUOTE)
                    elif c == '{':
                        buf.append("''' + repr(")
                        ss.append(ASPYTHON)
                        rstack = 0
                    elif ss[-1] == TRIPLE_ASSEMBLY and i+1 < length and \
                         c == '$' and line[i] == '$' and line[i+1] == '$':
                        i += 2
                        buf.append("''')")
                        ss.pop()
                    else:
                        buf.append(c)
                elif ss[-1] == ASPYTHON:
                    if c == "'":
                        buf.append(c)
                        ss.append(SINGLE_QUOTE)
                    elif c == '"':
                        buf.append(c)
                        ss.append(DOUBLE_QUOTE)
                    elif c == '}':
                        if rstack == 0:
                            buf.append(") + '''")
                            ss.pop()
                        else:
                            rstack -= 1
                            buf.append(c)
                    elif c == '{':
                        buf.append(c)
                        rstack += 1
                    else:
                        buf.append(c)
                else:
                    raise ValueError

            if ss[-1] == ASSEMBLY:
                # $-assembly ended with physical line
                buf.append("''')")
                ss.pop()

            buf.append(eol)

    if ss[-1] != NORMAL:
        raise ValueError

    for str in buf:
        out.write(str)


if __name__ == '__main__':
    from sys import stdout, argv
    if len(argv) != 2:
        print("Usage: {} xxx.pas".format(argv[0]))
    else:
        translate(argv[1], stdout)
