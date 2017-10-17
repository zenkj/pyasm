

NORMAL = 0
SINGLE_QUOTE = 1
DOUBLE_QUOTE = 2
TRIPLE_SINGLE_QUOTE = 3
TRIPLE_DOUBLE_QUOTE = 6
ASSEMBLY = -1
PYTHON_IN_ASSEMBLY = -2
TRIPLE_ASSEMBLY = -3
PYTHON_IN_TRIPLE_ASSEMBLY = -4

def translate(file, out):
    state = NORMAL
    rstack = 0
    buf = []

    with open(file) as f:
        for line in f:
            i = 0
            length = len(line)
            while i < length:
                c = line[i]
                i += 1
                if c == '\n':
                    break;
                if state == NORMAL:
                    if c == "'":
                        buf.append(c)
                        if i+1 < length and line[i] == "'" and line[i+1] == "'":
                            state = TRIPLE_SINGLE_QUOTE
                            i += 2
                            buf.append("''")
                        else:
                            state = SINGLE_QUOTE
                    elif c == '"':
                        buf.append(c)
                        if i+1 < length and line[i] == '"' and line[i+1] == '"':
                            state = TRIPLE_DOUBLE_QUOTE
                            i += 2
                            buf.append('""')
                        else:
                            state = DOUBLE_QUOTE
                    elif c == '#':
                        if line[-1] == '\n':
                            buf.append(line[i-1:-1])
                        else:
                            buf.append(line[i-1:])
                        i = length
                    elif c == '$':
                        if i+1 < length and line[i] == '$' and line[i+1] == '$':
                            state = TRIPLE_ASSEMBLY
                            i += 2
                        else:
                            state = ASSEMBLY
                        buf.append("print('''")
                    else:
                        buf.append(c)
                elif state == SINGLE_QUOTE:
                    buf.append(c)
                    if c == "'":
                        state = NORMAL
                    elif c == '\\' and i < length:
                        buf.append(line[i])
                        i += 1
                elif state == DOUBLE_QUOTE:
                    buf.append(c)
                    if c == '"':
                        state = NORMAL
                    elif c == '\\' and i < length:
                        buf.append(line[i])
                        i += 1
                elif state == TRIPLE_SINGLE_QUOTE:
                    buf.append(c)
                    if i+1 < length and c == "'" and line[i] == "'" and line[i+1] == "'":
                        buf.append("''")
                        state = NORMAL
                        i += 2
                    elif c == '\\' and i < length:
                        buf.append(line[i])
                        i += 1
                elif state == TRIPLE_DOUBLE_QUOTE:
                    buf.append(c)
                    if i+1 < length and c == '"' and line[i] == '"' and line[i+1] == '"':
                        buf.append('""')
                        state = NORMAL
                        i += 2
                    elif c == '\\' and i < length:
                        buf.append(line[i])
                        i += 1
                elif state == ASSEMBLY:
                    if c == '{':
                        state = PYTHON_IN_ASSEMBLY
                        buf.append("''' + str(")
                    else:
                        buf.append(c)
                elif state == TRIPLE_ASSEMBLY:
                    if c == '{':
                        state = PYTHON_IN_TRIPLE_ASSEMBLY
                        buf.append("''' + str(")
                    elif i+1 < length and c == '$' and line[i] == '$' and line[i+1] == '$':
                        state = NORMAL
                        buf.append("''')")
                        i += 2
                    else:
                        buf.append(c)
                elif state == PYTHON_IN_ASSEMBLY:
                    if c == '}':
                        if rstack == 0:
                            state = ASSEMBLY
                            buf.append(") + '''")
                        else:
                            rstack -= 1
                            buf.append(c)
                    elif c == '{':
                        buf.append(c)
                        rstack += 1
                    else:
                        buf.append(c)
                elif state == PYTHON_IN_TRIPLE_ASSEMBLY:
                    if c == '}':
                        if rstack == 0:
                            state = TRIPLE_ASSEMBLY
                            buf.append(") + '''")
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

            if state == ASSEMBLY:
                # $-assembly ended with physical line
                buf.append("''')")
                state = NORMAL

            buf.append('\n')

    if state != NORMAL:
        raise ValueError

    for str in buf:
        out.write(str)


if __name__ == '__main__':
    from sys import stdout, argv
    if len(argv) != 2:
        print("Usage: {} xxx.pas".format(argv[0]))
    else:
        translate(argv[1], stdout)
