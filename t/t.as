adc al, 8                    # 1408
adc ax, 0x1122               # 66152211
adc eax, 0x112233            # 1533221100
adc rax, 0x11223344          # 481544332211
adc bh, 24                   # 80D718
adc spl, 35                  # 4080D423
adc r14l, 33                 # 4180D621
adc bx, 24                   # 6683D318
adc sp, 35                   # 6683D423
adc r14w, 33                 # 664183D621
adc ebx, 24                  # 83D318
adc esp, 35                  # 83D423
adc r14d, 33                 # 4183D621
adc rbx, 24                  # 4883D318
adc rsp, 35                  # 4883D423
adc r14, 33                  # 4983D621
adcb fs:[rax+rbx*4+24], 8    # 648054981808
adcb [0x888888], 8           # 8014258888880008
adcb [rsp], 8                # 80142408
adcb [rbp+32], 8             # 80552008
adcb [r15+32], 8             # 4180572008
adcb [r15+r12+32], 8         # 438054272008
adcb [r15*8+r12+32], 8       # 438054FC2008
adcw fs:[rax+rbx*4+24], 8    # 64668354981808
adcw [0x888888], 8           # 668314258888880008
adcw [rsp], 8                # 6683142408
adcw [rbp+32], 8             # 6683542008
adcw [r15+32], 8             # 664183572008
adcw [r15+r12+32], 8         # 66438354272008
adcw [r15*8+r12+32], 8       # 66438354FC2008
adcl fs:[rax+rbx*4+24], 8    # 648354981808
adcl [0x888888], 8           # 8314258888880008
adcl [rsp], 8                # 83142408
adcl [rbp+32], 8             # 83552008
adcl [r15+32], 8             # 4183572008
adcd [r15+r12+32], 8         # 438354272008
adcd [r15*8+r12+32], 8       # 438354FC2008
adcq fs:[rax+rbx*4+24], 8    # 64488354981808
adcq [0x888888], 8           # 488314258888880008
adcq [rsp], 8                # 4883142408
adcq [rbp+32], 8             # 4883552008
adcq [r15+32], 8             # 4983572008
adcq [r15+r12+32], 8         # 4B8354272008
adcq [r15*8+r12+32], 8       # 4B8354FC2008
adc al, bh                   # 10F8
adc r14l, ah                 # 4110C6
adc fs:[rax+rbx*4+24], r13l  # 6444106C9818
adc [0x888888], spl          # 4010242588888800
adc [rsp], ch                # 102C24
adc [rbp+32], bh             # 107D20
adc [r15+32], dl             # 41105720
adc [r15+r12+32], al         # 4310443C20
adc [r15*8+r12+32], dl       # 431054FC20
adc ax, bx                   # 6611D8
adc r14w, ax                 # 664111C5
adc fs:[rax+rbx*4+24], r13w  # 646644116C9818
adc [0x888888], sp           # 6611242588888800
adc [rsp], cx                # 66110C24
adc [rbp+32], bx             # 66115D20
adc [r15+32], dx             # 6641115720
adc [r15+r12+32], ax         # 664311442720
adc [r15*8+r12+32], dx       # 66431154FC20
adc eax, ebx                 # 11C8
adc r14d, eax                # 4111C6
adc fs:[rax+rbx*4+24], r13d  # 6444116C9818
adc [0x888888], esp          # 11242588888800
adc [rsp], ecx               # 110C24
adc [rbp+32], ebx            # 115D20
adc [r15+32], edx            # 41115720
adc [r15+r12+32], eax        # 4311442720
adc [r15*8+r12+32], edx      # 431154FC20
adc rax, rbx                 # 4811C8
adc r14, rax                 # 4911C6
adc fs:[rax+rbx*4+24], r13   # 644C116C9818
adc [0x888888], rsp          # 4811242588888800
adc [rsp], rcx               # 48110C24
adc [rbp+32], rbx            # 48115D20
adc [r15+32], rdx            # 49115720
adc [r15+r12+32], rax        # 4B11442720
adc [r15*8+r12+32], rdx      # 4B1154FC20
adc bh, al                   # 10C7
adc ah, r14l                 # 4410F0
adc r13l, fs:[rax+rbx*4+24]  # 6444126C9818
adc spl, [0x888888]          # 4012242588888800
adc ch, [rsp]                # 122C24
adc bh, [rbp+32]             # 127D20
adc dl, [r15+32]             # 41125720
adc al, [r15+r12+32]         # 4312442720
adc dl, [r15*8+r12+32]       # 431254FC20
adc bx, ax                   # 6611C3
adc ax, r14w                 # 664411C6
adc r13w, fs:[rax+rbx*4+24]  # 646644136C9818
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
