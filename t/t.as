adc al, 8
adc ax, 0x1122
adc eax, 0x112233
adc rax, 0x11223344
adc bh, 24
adc spl, 35
adc r14l, 33
adc bx, 24
adc sp, 35
adc r14w, 33
adc ebx, 24
adc esp, 35
adc r14d, 33
adc rbx, 24
adc rsp, 35
adc r14, 33
adcb fs:[rax+rbx*4+24], 8
adcb [0x888888], 8
adcb [rsp], 8
adcb [rbp+32], 8
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
