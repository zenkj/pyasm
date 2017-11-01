TAPE_LENGTH = 30000

def translate(program):
    ip = 0

    rstack = []
    nextpc = 0

    $$$
    # test comment
    .define aPtr, rbx # test comment on this line
    .define aState, r12
    .define aTapeBegin, r13
    .define aTapeEnd, r14
    .define rArg1, rdi
    .define rArg2, rsi
    .macro precall1, arg1
      mov rArg1, arg1
      mov rArg2, arg2
    .endmacro
    .define postcall, .nop
    .macro prologue
      push aPtr
      push aState
      push aTapeBegin
      push aTapeEnd
      push rax
      mov aState, rArg1
    .endmacro
    .macro epilogue
      pop rax
      pop aTapeEnd
      pop aTapeBegin
      pop aState
      pop aPtr
      ret
    .endmacro

    .type state:nopack
      .ptr tape
      .ptr get_char
      .ptr put_char
    .endtype
    $$$

    $ .byte 'a"si\'b{}\'c\t', "ab{d\" ' ef\n", {TAPE_LENGTH/2}

    $ .code
    $bf_main:
    $ prologue
    $ mov aPtr, aState:state.tape
    $ lea aTapeBegin, [aPtr-1]
    $ lea aTapeEnd, [aPtr + {TAPE_LENGTH-1}]

    while True:
        i = program[ip]
        ip += 1
        if i == '<':
            n = 1
            while program[ip] == '<':
                ip += 1
                n += 1
            $ sub aPtr, {n%TAPE_LENGTH}
            $ cmp aPtr, aTapeBegin
            $ ja >1
            $ add aPtr, {TAPE_LENGTH}
            $1:
        elif i == '>':
            n = 1
            while program[ip] == '>':
                ip += 1
                n += 1
            $ add aPtr, {n%TAPE_LENGTH}
            $ cmp aPtr, aTapeEnd
            $ jbe >1
            $ sub aPtr, {TAPE_LENGTH}
            $1:
        elif i == '+':
            n = 1
            while program[ip] == '+':
                ip += 1
                n += 1
            $ add byte [aPtr], {n}
        elif i == '-':
            n = 1
            while program[ip] == '-':
                ip += 1
                n += 1
            $ sub byte [aPtr], {n}
        elif i == ',':
            $ call aword aState:state.get_char
            $ postcall 1
            $ mov byte [aPtr], al
        elif i == '.':
            $ movzx r0, byte [aPtr]
            $ precall1 r0
            $ call aword aState:state.put_char
            $ postcall 2
        elif i == '[':
            if program[ip] == '-' and program[ip+1] == ']':
                ip += 2
                $ xor eax, eax
                $ mov byte [aPtr], al
            else:
                $ cmp byte [aPtr], 0
                $ jz @{nextpc + 1}
                $@{nextpc}:
                rstack.append(nextpc)
                nextpc += 2
        elif i == ']':
            if len(rstack) == 0:
                raise ValueError("no corresponding '['")
            $ cmp byte [aPtr], 0
            $ jnz @{rstack[-1]}
            $@{rstack[-1]+1}:
            rstack.pop()
        elif i == '\0':
            if len(rstack) > 0:
                raise ValueError("no corresponding ']'")
            $ epilogue
            return 

if __name__ == '__main__':
    from sys import argv
    if len(argv) != 2:
        print('Usage: python brainfuck.pas bffile')
    else:
        with open(argv[1]) as bf:
            program = bf.read()

        program = program + '\0'

        translate(program)
