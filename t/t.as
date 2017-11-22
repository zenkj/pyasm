adc al, 8
# 1408
adc ax, 0x1122
# 66152211
adc eax, 0x112233
# 1533221100
adc rax, 0x11223344
# 481544332211
adc bh, 24
# 80D718
adc spl, 35
# 4080D423
adc r14l, 33
# 4180D621
adc bx, 24
# 6683D318
adc sp, 35
# 6683D423
adc r14w, 33
# 664183D621
adc ebx, 24
# 83D318
adc esp, 35
# 83D423
adc r14d, 33
# 4183D621
adc rbx, 24
# 4883D318
adc rsp, 35
# 4883D423
adc r14, 33
# 4983D621
adcb fs:[rax+rbx*4+24], 8
# 648054981808
adcb [0x888888], 8
# 8014258888880008
adcb [rsp], 8
# 80142408
adcb [rbp+32], 8
# 80552008
adcb [r15+32], 8
adcb [r15+r12+32], 8
adcb [r15*8+r12+32], 8
adcw fs:[rax+rbx*4+24], 8
adcw [0x888888], 8
adcw [rsp], 8
adcw [rbp+32], 8
adcw [r15+32], 8
adcw [r15+r12+32], 8
adcw [r15*8+r12+32], 8
adcl fs:[rax+rbx*4+24], 8
adcl [0x888888], 8
adcl [rsp], 8
adcl [rbp+32], 8
adcl [r15+32], 8
adcd [r15+r12+32], 8
adcd [r15*8+r12+32], 8
adcq fs:[rax+rbx*4+24], 8
adcq [0x888888], 8
adcq [rsp], 8
adcq [rbp+32], 8
adcq [r15+32], 8
adcq [r15+r12+32], 8
adcq [r15*8+r12+32], 8
adc al, bh
adc r14l, ah
adc fs:[rax+rbx*4+24], r13l
adc [0x888888], spl
adc [rsp], ch
adc [rbp+32], bh
adc [r15+32], dl
adc [r15+r12+32], al
adc [r15*8+r12+32], dl
adc ax, bx
adc r14w, ax
adc fs:[rax+rbx*4+24], r13w
adc [0x888888], sp
adc [rsp], cx
adc [rbp+32], bx
adc [r15+32], dx
adc [r15+r12+32], ax
adc [r15*8+r12+32], dx
adc eax, ebx
adc r14d, eax
adc fs:[rax+rbx*4+24], r13d
adc [0x888888], esp
adc [rsp], ecx
adc [rbp+32], ebx
adc [r15+32], edx
adc [r15+r12+32], eax
adc [r15*8+r12+32], edx
adc rax, rbx
adc r14, rax
adc fs:[rax+rbx*4+24], r13
adc [0x888888], rsp
adc [rsp], rcx
adc [rbp+32], rbx
adc [r15+32], rdx
adc [r15+r12+32], rax
adc [r15*8+r12+32], rdx
adc bh, al
adc ah, r14l
adc r13l, fs:[rax+rbx*4+24]
adc spl, [0x888888]
adc ch, [rsp]
adc bh, [rbp+32]
adc dl, [r15+32]
adc al, [r15+r12+32]
adc dl, [r15*8+r12+32]
adc bx, ax
adc ax, r14w
adc r13w, fs:[rax+rbx*4+24]
adc sp, [0x888888]
adc cx, [rsp]
adc bx, [rbp+32]
adc dx, [r15+32]
adc ax, [r15+r12+32]
adc dx, [r15*8+r12+32]
adc ebx, eax
adc eax, r14d
adc r13d, fs:[rax+rbx*4+24]
adc esp, [0x888888]
adc ecx, [rsp]
adc ebx, [rbp+32]
adc edx, [r15+32]
adc eax, [r15+r12+32]
adc edx, [r15*8+r12+32]
adc rbx, rax
adc rax, r14
adc r13, fs:[rax+rbx*4+24]
adc rsp, [0x888888]
adc rcx, [rsp]
adc rbx, [rbp+32]
adc rdx, [r15+32]
adc rax, [r15+r12+32]
adc rdx, [r15*8+r12+32]
