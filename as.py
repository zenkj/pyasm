from re import match, fullmatch, sub, findall
from ast import literal_eval as leval
import struct

class Type(object):

    def __init__(self, name, size=0, align=1, packed=False):
        if size < 0:
            raise ValueError('size should be >= 0')
        if align == 0 or ((align & (align-1)) != 0):
            raise ValueError('align should be power of 2')
        self.name = name
        self.size = size 
        self.align = align
        self.packed = packed
        self.members = {}
        self.offsets = {}

    def addMember(self, name, tp):
        offset = self.size
        if not self.packed:
            offset = (offset + (tp.align-1)) & (-tp.align)
        self.members[name] = tp
        self.offsets[name] = offset

        # update size of the structure
        self.size = offset + tp.size()

        # update align of the structure
        if tp.align > self.align:
            self.align = tp.align

    def size(self):
        if self.packed:
            return self.size
        else:
            return (self.size + (self.align-1)) & (-self.align)

    def member(self, name):
        if not self.members[name]:
            raise ValueError
        return members[name]


class TypeManager(object):

    def __init__(self):
        self.alltypes = {}
        self.registerType(Type('.byte', 1))
        self.registerType(Type('.int16', 2, 2))
        self.registerType(Type('.int32', 4, 4))
        self.registerType(Type('.int64', 8, 8))
        self.registerType(Type('.float', 4, 4))
        self.registerType(Type('.double', 8, 8))

    def offsetof(self, fullname):
        namelist = fullname.split('.')
        offset = 0
        tp = self.alltypes[ns[0]]
        if not tp: raise ValueError
        for name in namelist[1:]:
            m = tp.members[name]
            if not m: 
                raise ValueError
            offset += tp.offsets[name]
            tp = m
        return offset

    def typeof(self, tpname):
        tp = self.alltypes[tpname]
        if not tp: raise ValueError
        return tp

    def registerType(self, tp):
        name = tp.name
        if name in self.alltypes:
            raise ValueError('reregister type {}'.format(name))
        self.alltypes[name] = tp



class AS:
    """
    features:
        # no .include
        # it can be handled in python

        # .byte
        # handle string/hex/oct/float
        # .byte 0, 0x10, 'ab"c\n', "a\nb'c", 'a'

        # .type
        # working

        # .define
        # TBD
        # no define now
        #defines = {}

        # .macro
        # TBD
        #macros = {}
    """

    def __init__(self):
        # assembly operation map
        self.asmap = {}

        # type definition map
        self.tpmap = {}

        #### the current opmap
        self.opmap = self.asmap

        # result binary
        self.resultbin = bytearray()

        # global labels
        self.glabels = {}

        self.tm = TypeManager()

        self.currtp = None
        self.initTypeMap()
        self.initAsMap()


    def initTypeMap(self):
        def typeop(op, params):
            tp = self.tm.typeof(op)
            for name in params:
                self.currtp.addMember(name, tp)

        self.tpmap['*'] = typeop

        def dotendtype(op, params):
            self.tm.registerType(currtp)
            self.currtp = None
            self.opmap = self.asmap

        self.tpmap['.endtype'] = dotendtype

    def initAsMap(self):
        def dottype(op, params):
            m = fullmatch(r'\s*(\w+):?(\w*)\s*', params[0])
            if not m:
                raise ValueError
            name = m.group(1)
            option = m.group(2)
            if option == 'pack':
                self.currtp = Type(name, 0, 1, True)
            else:
                self.currtp = Type(name)
            self.opmap = self.tpmap

        self.asmap['.type-1'] = dottype

        ########################## template #################################
        # instruction structure:
        # [prefix]:[rex]:opcode:[modrm]/[options]
        self.asmap['adc-2'] = '::14:/a8i8|66::15:/a16i16|::15:/a32i32|:48:15:/a64i32' \
                         ''
    
    
    def dotemplateone(self, tmpl, op, params):

        """
        处理一个指令模板 

        x86_64指令结构:
          prefix     rex     opcode    modrm       sib       displacement  immediate
                  0100 WRXB          mm reg r/m  ss iii bbb
                  7654 3210          76 543 210  76 543 210
        
        模板结构：
        [prefix]:[rex]:opcode:[modrm]/[commands]
        
        模板命令列表:
          a
            register AL/AX/EAX/RAX, a8/a16/a32/a64 respectively
          i
            signed immediate integer, i8/i16/i32/i64
          I
            unsigned immediate integer, I8/I16/I32/I64
          f
            floating point number, f32/f64
          r
            registers encoded in reg of modrm, and R in rex optionally.
            r8/r16/r32/r64
          R
            registers encoded in reg of opcode, and B in rex optionally.
            R8/R16/R32/R64
          M
            registers encoded in r/m of modrm, and B in rex optionally.
            M8/M16/M32/M64
          m
            memory location encoded in r/m of modrm, and sib optionally.

        内存操作数结构：
          sr:[base+index*scale+offset]
          sr
            段寄存器前缀，cs/ds/es/fs
          base
            基址寄存器
          index
            索引寄存器，除rsp外其他15个通用寄存器
          scale
            倍数，1/2/4/8
          offset
            偏移值，8位或32位

        内存操作数处理流程：
          1. 先把reg:state.ptr这种类型的转化为reg+nnn
          2. 然后再取出segment register(opt)和[]中的内容
              re.match(r'\s*((\w+)\s*:)?\s*\[\s*([^\]]+)\s*\]\s*', ' fs : [ rax + rdx * 4 - 5 ] ')
          3. 根据段寄存器设置段前缀
          4. 然后解析[]中的内容
              re.split(r'\s*([+-])\s*', 'a + 4 * b - 5 '.strip())
          5. 然后把scale*index取出来
              re.split(r'\s*\*\s*', '4 * rbx'.strip())
          6. 然后就是把基址/索引/倍数/偏移取出来，各种排列组合:
             寄存器基址/索引*倍数/偏移，三部分每个都可以存在或不存在，
             除去三部分都不存在的情况，共2*2*2-1 = 7种，加上rip相对地址，共8种

             mod!=11 and r/m=100意味着存在SIB，有没有REX都不影响:
               所以基址为rsp和r12时，不管有没有偏移，都只能使用SIB;
             mod=0 and r/m=101意味着RIP相对寻址，有没有REX都不影响:
               所以基址为rbp和r13并且没有偏移时，只能使用偏移0(mod=01, displacement=0)
            
        内存操作数种类(8种排列组合C1-C8)：
          1. 寄存器基址
            e.g.: [rax/rbx/rcx/rdx/rsp/rbp/rsi/rdi/r8-r15]
            (1) rax/rbx/rcx/rdx/rsi/rdi:
               mod    r/m
               00     nnn(not 100 and 101)
            (2) rsp:
               mod    r/m       ss iii bbb
               00     100       nn 100 100
            (3) r12:
             REX.B   mod    r/m    ss iii bbb
               1      00    100    nn 100 100
            (4) rbp:
               mod    r/m   displacement
                01    101   00000000
            (5) r13:
             REX.B   mod    r/m    displacement
               1      01    101    00000000
            (6) r8-r11/r14/r15:
             REX.B   mod    r/m
               1      00    nnn(not 100 and 101)
            
          2. 绝对地址
            [1234]
                mod    r/m      ss iii bbb   displacement
                00     100      nn 100 101   nnnnnnnn nnnnnnnn nnnnnnnn nnnnnnnn
            
          3. 寄存器基址+偏移
            e.g.: [rax/rbx/rcx/rdx/rsp/rbp/rsi/rdi/r8-r15 + 12]
            (1) rax/rbx/rcx/rdx/rbp/rsi/rdi + offset:
              mod     r/m             displacement
              01      nnn(not 100)    nnnnnnnn
              10      nnn(not 100)    nnnnnnnn nnnnnnnn nnnnnnnn nnnnnnnn
            (2) rsp + offset:
               mod    r/m       ss iii bbb    displacement
               01     100       nn 100 100    nnnnnnnn
               10     100       nn 100 100    nnnnnnnn nnnnnnnn nnnnnnnn nnnnnnnn
            (3) r12 + offset: 
             REX.B   mod    r/m    ss iii bbb   displacement
               1      01    100    nn 100 100   nnnnnnnn
               1      10    100    nn 100 100   nnnnnnnn nnnnnnnn nnnnnnnn nnnnnnnn
            (4) r8-r11/r13-r15 + offset:
             REX.B   mod    r/m            displacement
               1      01    nnn(not 100)   nnnnnnnn
               1      10    nnn(not 100)   nnnnnnnn nnnnnnnn nnnnnnnn nnnnnnnn
            
          4. rip相对地址
            e.g.: [rip+12]
            mod   r/m   displacement
             00   101   nnnnnnnn nnnnnnnn nnnnnnnn nnnnnnnn
           
          5. 索引*倍数 (不存在，有索引的时候必须有基址或32位偏移，这种编码为偏移=0)
            e.g.: [rax/rbx/rcx/rdx/rbp/rsi/rdi/r8-r15 * 1/2/4/8] (只有rsp不能作索引, 100意味着没有索引)
            (1) rax/rbx/rcx/rdx/rbp/rsi/rdi * 1/2/4/8:
                mod    r/m      ss iii          bbb    displacement
                00     100      00 nnn(not 100) 101    00000000 00000000 00000000 00000000
                00     100      01 nnn(not 100) 101    00000000 00000000 00000000 00000000
                00     100      10 nnn(not 100) 101    00000000 00000000 00000000 00000000
                00     100      11 nnn(not 100) 101    00000000 00000000 00000000 00000000
            (2) r8-r15 * 1/2/4/8:
                REX.X  mod    r/m      ss iii             bbb    displacement
                  1    00     100      00 nnn(100 ok too) 101    00000000 00000000 00000000 00000000
                  1    00     100      01 nnn(100 ok too) 101    00000000 00000000 00000000 00000000
                  1    00     100      10 nnn(100 ok too) 101    00000000 00000000 00000000 00000000
                  1    00     100      11 nnn(100 ok too) 101    00000000 00000000 00000000 00000000
            
          6. 索引*倍数 + 寄存器基址
            e.g.: [rax/rbx/rcx/rdx/rbp/rsi/rdi/r8-r15 * 1/2/4/8 +
                   rax/rbx/rcx/rdx/rsp/rbp/rdi/rsi/r8-r15]
            (1) rax/rbx/rcx/rdx/rbp/rsi/rdi*1/2/4/8 + rax/rbx/rcx/rdx/rsp/rdi/rsi:
                mod  r/m     ss iii          bbb
                00   100     nn nnn(not 100) nnn(not 101)
            (2) r8-r15*1/2/4/8 + rax/rbx/rcx/rdx/rsp/rdi/rsi:
                REX.X REX.B  mod  r/m     ss iii bbb
                  1     0    00   100     nn nnn nnn(not 101)
            (3) rax/rbx/rcx/rdx/rbp/rsi/rdi*1/2/4/8 + r8-r12/r14/r15:
                REX.X REX.B  mod  r/m     ss iii          bbb
                  0     1    00   100     nn nnn(not 100) nnn(not 101)
            (4) r8-r15*1/2/4/8 + r8-r12/r14/r15:
                REX.X REX.B  mod  r/m     ss iii bbb
                  1     1    00   100     nn nnn nnn(not 101)
            (5) rax/rbx/rcx/rdx/rbp/rsi/rdi*1/2/4/8 + rbp:
                mod  r/m     ss iii          bbb  displacement
                01   100     nn nnn(not 100) 101  00000000
            (6) r8-r15*1/2/4/8 + rbp:
                REX.X REX.B  mod  r/m     ss iii bbb  displacement
                  1     0    01   100     nn nnn 101  00000000
            (7) rax/rbx/rcx/rdx/rbp/rsi/rdi*1/2/4/8 + r13:
                REX.X REX.B mod  r/m     ss iii          bbb  displacement
                  0     1   01   100     nn nnn(not 100) 101  00000000
            (8) r8-r15*1/2/4/8 + r13:
                REX.X REX.B  mod  r/m     ss iii bbb  displacement
                  1     1    01   100     nn nnn 101  00000000
            
          7. 索引*倍数 + 偏移 (只能32位偏移)
            e.g.: [rax/rbx/rcx/rdx/rbp/rsi/rdi/r8-r15 * 1/2/4/8 + 1234] (只有rsp不能作索引, 100意味着没有索引)
            (1) rax/rbx/rcx/rdx/rbp/rsi/rdi * 1/2/4/8 + offset:
                mod    r/m      ss iii          bbb    displacement
                00     100      00 nnn(not 100) 101    nnnnnnnn nnnnnnnn nnnnnnnn nnnnnnnn
                00     100      01 nnn(not 100) 101    nnnnnnnn nnnnnnnn nnnnnnnn nnnnnnnn
                00     100      10 nnn(not 100) 101    nnnnnnnn nnnnnnnn nnnnnnnn nnnnnnnn
                00     100      11 nnn(not 100) 101    nnnnnnnn nnnnnnnn nnnnnnnn nnnnnnnn
            (2) r8-r15 * 1/2/4/8 + offset:
                REX.X  mod    r/m      ss iii             bbb    displacement
                  1    00     100      00 nnn(100 ok too) 101    nnnnnnnn nnnnnnnn nnnnnnnn nnnnnnnn
                  1    00     100      01 nnn(100 ok too) 101    nnnnnnnn nnnnnnnn nnnnnnnn nnnnnnnn
                  1    00     100      10 nnn(100 ok too) 101    nnnnnnnn nnnnnnnn nnnnnnnn nnnnnnnn
                  1    00     100      11 nnn(100 ok too) 101    nnnnnnnn nnnnnnnn nnnnnnnn nnnnnnnn

          8. 寄存器基址+索引*倍数+偏移
            e.g.: [rax/rbx/rcx/rdx/rbp/di/rsi/r8-r15 * 1/2/4/8 +
                   rax/rbx/rcx/rdx/rsp/rbp/rdi/rsi/r8-r15 + 1234]
            (1) rax/rbx/rcx/rdx/rbp/rsi/rdi*1/2/4/8 + rax/rbx/rcx/rdx/rsp/rbp/rdi/rsi + offset:
                mod  r/m     ss iii          bbb   displacement
                01   100     nn nnn(not 100) nnn   nnnnnnnn
                10   100     nn nnn(not 100) nnn   nnnnnnnn nnnnnnnn nnnnnnnn nnnnnnnn
            (2) r8-r15*1/2/4/8 + rax/rbx/rcx/rdx/rsp/rbp/rdi/rsi + offset:
                REX.X REX.B  mod  r/m     ss iii bbb   displacement
                  1     0    01   100     nn nnn nnn   nnnnnnnn
                  1     0    10   100     nn nnn nnn   nnnnnnnn nnnnnnnn nnnnnnnn nnnnnnnn
            (3) rax/rbx/rcx/rdx/rbp/rsi/rdi*1/2/4/8 + r8-r15 + offset:
                REX.X REX.B mod  r/m     ss iii          bbb  displacement
                  0     1   01   100     nn nnn(not 100) nnn  nnnnnnnn
                  0     1   10   100     nn nnn(not 100) nnn  nnnnnnnn nnnnnnnn nnnnnnnn nnnnnnnn
            (4) r8-r15*1/2/4/8 + r8-r15 + offset:
                REX.X REX.B  mod  r/m     ss iii bbb  displacement
                  1     1    01   100     nn nnn nnn  nnnnnnnn
                  1     1    10   100     nn nnn nnn  nnnnnnnn nnnnnnnn nnnnnnnn nnnnnnnn
        """

        m = fullmatch(r'([0-9A-F]*):([0-9A-F]*):([0-9A-F]+):([0-9A-F]*)/([a-zA-Z0-9]*)', tmpl) 
        if not m: raise ValueError('Invalid template')
        sprefix = m.group(1)
        srex    = m.group(2)
        sopcode = m.group(3)
        smodrm  = m.group(4)
        soption = m.group(5)

        prefix = bytearray.fromhex(sprefix)
        rex = bytearray.fromhex(srex)
        opcode = bytearray.fromhex(sopcode)
        modrm = bytearray.fromhex(smodrm)

        sib = bytearray()
        displacement = bytearray()
        immediate = bytearray()

        def REX():
            if len(rex) == 0:
                rex.append(0)
            return rex

        def MODRM():
            if len(modrm) == 0:
                modrm.append(0)
            return modrm

        def SIB():
            if len(sib) == 0:
                sib.append(0)
            return sib


        def ensuren(n):
            if n == 8 or n == 16 or n == 32 or n == 64:
                return
            raise ValueError('invalid template {}'.format(tmpl))
        
        for (o, sn) in findall(r'([a-zA-Z])([0-9]*)', soption):
            n = 0 if len(sn) == 0 else int(sn)

            if o == 'a':
                p = params.pop(0)
                if n > 0 and regAbits[p] != n:
                    raise ValueError('invalid ax value: {} bits'.format(n))
            elif o == 'i' or o == 'I' or o == 'f':
                imm = leval(params.pop(0))
                immediate = pack(o+sn, imm)
            elif o == 'r': # reg in modrm, and R in rex optionally
                ensuren(n)
                p = params.pop(0)
                if GPRbits[p] != n:
                    raise ValueError('invalid register "{}"'.format(p))
                code = GPR[p]
                if code >= 8: # need REX
                    REX()[0] |= ((code&8)>>1)
                MODRM()[0] |= ((code&7)<<3)
            elif o == 'R': # reg in opcode, and B in rex optionally
                ensuren(n)
                p = params.pop(0)
                if GPRbits[p] != n:
                    raise ValueError('invalid register "{}"'.format(p))
                code = GPR[p]
                if code >= 8: # need REX
                    REX()[0] |= ((code&8)>>3)
                opcode[-1] |= (code&7)
            elif o == 'M': # register in r/m in modrm, and B in rex optioanlly
                ensuren(n)
                p = params.pop(0)
                if GPRbits[p] != n:
                    raise ValueError('invalid register "{}"'.format(p))
                code = GPR[p]
                if code >= 8: # need REX
                    REX()[0] |= ((code&8)>>3)
                MODRM()[0] |= (0xC0|(code&7))
            elif o == 'm': # memory in r/m in modrm, and sib optionally
                base = None
                index = None
                scale = None
                offset = None

                negative = False
                # 先把reg:state.ptr这种类型的转化为reg+nnn
                p = params.pop(0)
                p = sub(r'(\w+):([\w.]+)', \
                        lambda m: '{}+{}'.format(m.group(1), self.tm.offsetof(m.group(2))), \
                        p)
                # 然后再取出segment register(opt)和[]中的内容
                #     re.match(r'\s*((\w+)\s*:)?\s*\[\s*([^\]]+)\s*\]\s*', ' fs : [ rax + rdx * 4 - 5 ] ')
                m = fullmatch(r'\s*((\w+)\s*:)?\s*\[\s*([^\]]+)\]\s*', p)
                if not m: raise ValueError('{} is not valid memory addressing operand'.format(p))

                # 根据段寄存器设置段前缀
                if m.group(2):
                    sprefix = SegPrefix[m.group(2)]
                    prefix.append(sprefix)

                # 然后解析[]中的内容
                #     re.split(r'\s*([+-])\s*', 'a + 4 * b - 5 '.strip())
                addr0 = re.split('r\s*([+-])\s*', m.group(3).strip())
                addr = []

                for item in addr0:
                    if item == '+':
                        negative = False
                    elif item == '-':
                        negative = True
                    else:
                        if negative:
                            negative = False
                            item = -int(item)
                        addr.append(item)
                
                # 然后把scale*index取出来，保证index不为rsp
                #     re.split(r'\s*\*\s*', '4 * rbx'.strip())
                for item in addr:
                    item = item.strip()
                    m = re.search(r'\*', item)
                    if m:
                        si = re.split(r'\s*\*\s*', item)
                        if len(si) != 2: raise ValueError('item {} is not valid scaled index'.format(item))
                        if index is not None: raise ValueError('duplicate index {}'.format(item))
                        si0 = si[0].strip()
                        si1 = si[1].strip()
                        index, scale = (si0, si1) if len(si0)>len(si1) else (si1, si0)
                        scale = Scale[scale]
                        if index not in GPRbits or GPRbits[index] != 64:
                            raise ValueError("index register should be 64-bit GPR")
                        if index == 'rsp': raise ValueError("rsp can't be used as index register")
                    elif item in GPRbits and GPRbits[item] == 64:
                        if base is None:
                            base = item
                        elif index is None and scale is None:
                            if item == 'rsp' and base == 'rsp':
                                raise ValueError("rsp can't be used as index regiser")
                            if item == 'rsp':
                                index = base
                                base = item
                            else:
                                index = item
                            scale = 0
                        else:
                            raise ValueError('redundant register {}'.format(item))
                    elif item == 'rip':
                        if base is not None or index is not None:
                            raise ValueError("rip can't be used with index register")
                        base = item
                    elif isinstance(item, int):
                        offset = item
                    else: # 不处理其他情况
                        raise ValueError("invalid item {} for memory address".format(item))

                if base is None and index is not None and scale == 0:
                    base = index
                    index = None

                # 然后就是把基址/索引/倍数/偏移取出来，各种排列组合:
                if base is not None and index is None:
                    if offset is None: offset = 0
                    if base == 'rip':
                        # 4. rip相对寻址
                        # mod   r/m   displacement
                        #  00   101   nnnnnnnn nnnnnnnn nnnnnnnn nnnnnnnn
                        MODRM()[0] = (MODRM()[0] & 0x38) | 0x5
                        displacement = pack('i32', offset)
                    else:
                        # 1. 寄存器基址
                        # 3. 寄存器基址+偏移
                        MODRM()[0] = ((MODRM()[0]&0x38)) | (GPR[base]&7)
                        if GPR[base]>=8:
                            REX()[0] = REX()[0] | 1
                        if base == 'rsp' or base == 'r12':
                            SIB()[0] = 0x24

                        if (offset == 0 and (base == 'rbp' or base == 'r13')) or offset != 0:
                            if offset <= 127 and offset >= -128:
                                MODRM()[0] = (MODRM()[0] & 0x3F) | 0x40
                                displacement = pack('i8', offset)
                            else:
                                MODRM()[0] = (MODRM()[0] & 0x3F) | 0x80
                                displacement = pack('i32', offset)
                elif base is None and index is None and offset is not None:
                    # 2. 绝对地址
                    MODRM()[0] = (MODRM()[0] & 0x38) | 0x4
                    SIB()[0] = 0x25
                    displacement = pack('i32', offset)
                elif base is None and index is not None:
                    # 5. 索引*倍数
                    # 7. 索引*倍数+偏移
                    if offset is None: offset = 0
                    MODRM()[0] = ((MODRM()[0]&0x38)|4)
                    if GPR[index] >= 8:
                        REX()[0] = REX()[0] | 2 
                    SIB()[0] = 5 | (scale<<6) | ((GPR[index]&7)<<3)
                    displacement = pack('i32', offset)
                elif base is not None and index is not None:
                    # 6. 索引*倍数 + 基址
                    # 8. 索引*倍数 + 基址 + 偏移
                    if offset is None: offset = 0
                    MODRM()[0] = (MODRM()[0] & 0x38) | 4
                    SIB()[0] = (GPR[base]&7) | ((GPR[index]&7)<<3) | (scale << 6)
                    if GPR[base] >= 8:
                        REX()[0] |= 1
                    if GPR[index] >= 8:
                        REX()[0] |= 2
                    if (offset == 0 and (base == 'rbp' or base == 'r13')) or offset != 0:
                        if offset <= 127 and offset >= -128:
                            MODRM()[0] = (MODRM()[0] & 0x3F) | 0x40
                            displacement = pack('i8', offset)
                        else:
                            MODRM()[0] = (MODRM()[0] & 0x3F) | 0x80
                            displacement = pack('i32', offset)



        # instruction = prefix(opt) + rex(opt) + opcode(1-3bytes) +
        #               modrm(opt) + sib(opt) + displacement(opt) + immediate(opt)
        self.resultbin.extend(prefix)
        self.resultbin.extend(rex)
        self.resultbin.extend(opcode)
        self.resultbin.extend(modrm)
        self.resultbin.extend(sib)
        self.resultbin.extend(displacement)
        self.resultbin.extend(immediate)


    def dotemplate(self, tmpl, op, params):
        tmpls = tmpl.split('|')
        for t in tmpls:
            try:
                self.dotemplateone(t, op, params[:])
                return
            except:
                pass

    def splitargs(self, argline):
        argline = fullmatch(r'(.*),?', argline).group(1)
        i = 0
        length = len(argline)

        if length == 0: return []

        argline = list(argline)

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

        args = ''.join(argline).split('\n')
        return [arg.strip() for arg in args]

    def doline(self, line):
        # ignore empty line
        if fullmatch(r'\s*', line):
            return

        # translate label
        m = fullmatch(r'\s*(@?\w+)\s*:\s*', line)
        if m: line = '.label ' + m.group(1)

        # split statement
        m = fullmatch(r'\s*([-.\w]+)\s+(.*)\s*', line)
        if not m: raise ValueError
        opcode = m.group(1)
        args = self.splitargs(m.group(2))

        key = '{}-{}'.format(opcode, len(args))
        if key not in self.opmap:
            key = opcode
            if key not in self.opmap:
                key = '*'
                if key not in self.opmap:
                    raise ValueError('unknown operation {}'.format(opcode))
        op = self.opmap[key]

        if callable(op):
            op(opcode, args)
        elif isinstance(op, str):
            self.dotemplate(op, opcode, args)
        else:
            raise ValueError

########################### constant ##########################
regAbits = {
    'al':   8,
    'ax':   16,
    'eax':  32,
    'rax':  64, # with REX prefix
    }

Scale = {
    '1': 0,
    '2': 1,
    '4': 2,
    '8': 3
    }

GPRbits = {
    'al':   8,
    'cl':   8,
    'dl':   8,
    'bl':   8,
    'ah':   8,  # no REX prefix
    'ch':   8,  # no REX prefix
    'dh':   8,  # no REX prefix
    'bh':   8,  # no REX prefix
    'spl':  8,  # with REX prefix
    'bpl':  8,  # with REX prefix
    'sil':  8,  # with REX prefix
    'dil':  8,  # with REX prefix
    'r8l':  8,  # with REX prefix
    'r9l':  8,  # with REX prefix
    'r10l': 8,  # with REX prefix
    'r11l': 8,  # with REX prefix
    'r12l': 8,  # with REX prefix
    'r13l': 8,  # with REX prefix
    'r14l': 8,  # with REX prefix
    'r15l': 8,  # with REX prefix
    'ax':   16,
    'cx':   16,
    'dx':   16,
    'bx':   16,
    'sp':   16,
    'bp':   16,
    'si':   16,
    'di':   16,
    'r8w':  16, # with REX prefix
    'r9w':  16, # with REX prefix
    'r10w': 16, # with REX prefix
    'r11w': 16, # with REX prefix
    'r12w': 16, # with REX prefix
    'r13w': 16, # with REX prefix
    'r14w': 16, # with REX prefix
    'r15w': 16, # with REX prefix
    'eax':  32,
    'ecx':  32,
    'edx':  32,
    'ebx':  32,
    'esp':  32,
    'ebp':  32,
    'esi':  32,
    'edi':  32,
    'r8d':  32, # with REX prefix
    'r9d':  32, # with REX prefix
    'r10d': 32, # with REX prefix
    'r11d': 32, # with REX prefix
    'r12d': 32, # with REX prefix
    'r13d': 32, # with REX prefix
    'r14d': 32, # with REX prefix
    'r15d': 32, # with REX prefix
    'rax':  64, # with REX prefix
    'rcx':  64, # with REX prefix
    'rdx':  64, # with REX prefix
    'rbx':  64, # with REX prefix
    'rsp':  64, # with REX prefix
    'rbp':  64, # with REX prefix
    'rsi':  64, # with REX prefix
    'rdi':  64, # with REX prefix
    'r8':   64, # with REX prefix
    'r9':   64, # with REX prefix
    'r10':  64, # with REX prefix
    'r11':  64, # with REX prefix
    'r12':  64, # with REX prefix
    'r13':  64, # with REX prefix
    'r14':  64, # with REX prefix
    'r15':  64, # with REX prefix
    }

GPR = {
    'al':   0,
    'cl':   1,
    'dl':   2,
    'bl':   3,
    'ah':   4,  # no REX prefix
    'ch':   5,  # no REX prefix
    'dh':   6,  # no REX prefix
    'bh':   7,  # no REX prefix
    'spl':  4|16,  # with REX prefix
    'bpl':  5|16,  # with REX prefix
    'sil':  6|16,  # with REX prefix
    'dil':  7|16,  # with REX prefix
    'r8l':  8,  # with REX prefix
    'r9l':  9,  # with REX prefix
    'r10l': 10, # with REX prefix
    'r11l': 11, # with REX prefix
    'r12l': 12, # with REX prefix
    'r13l': 13, # with REX prefix
    'r14l': 14, # with REX prefix
    'r15l': 15, # with REX prefix
    'ax':   0,
    'cx':   1,
    'dx':   2,
    'bx':   3,
    'sp':   4,
    'bp':   5,
    'si':   6,
    'di':   7,
    'r8w':  8,  # with REX prefix
    'r9w':  9,  # with REX prefix
    'r10w': 10, # with REX prefix
    'r11w': 11, # with REX prefix
    'r12w': 12, # with REX prefix
    'r13w': 13, # with REX prefix
    'r14w': 14, # with REX prefix
    'r15w': 15, # with REX prefix
    'eax':  0,
    'ecx':  1,
    'edx':  2,
    'ebx':  3,
    'esp':  4,
    'ebp':  5,
    'esi':  6,
    'edi':  7,
    'r8d':  8,  # with REX prefix
    'r9d':  9,  # with REX prefix
    'r10d': 10, # with REX prefix
    'r11d': 11, # with REX prefix
    'r12d': 12, # with REX prefix
    'r13d': 13, # with REX prefix
    'r14d': 14, # with REX prefix
    'r15d': 15, # with REX prefix
    'rax':  0,  # with REX prefix
    'rcx':  1,  # with REX prefix
    'rdx':  2,  # with REX prefix
    'rbx':  3,  # with REX prefix
    'rsp':  4,  # with REX prefix
    'rbp':  5,  # with REX prefix
    'rsi':  6,  # with REX prefix
    'rdi':  7,  # with REX prefix
    'r8':   8,  # with REX prefix
    'r9':   9,  # with REX prefix
    'r10':  10, # with REX prefix
    'r11':  11, # with REX prefix
    'r12':  12, # with REX prefix
    'r13':  13, # with REX prefix
    'r14':  14, # with REX prefix
    'r15':  15, # with REX prefix
    }

SegPrefix = {
    'cs':    0x2E,
    'ds':    0x3E,
    'es':    0x26,
    'fs':    0x64,
    'gs':    0x65,
    'ss':    0x36,
    }
Prefix = {
    # group 1
    'lock':  0xF0,
    'repne': 0xF2,
    'repnz': 0xF2,
    'rep':   0xF3,
    'repe':  0xF3,
    'repz':  0xF3,
    'bnd':   0xF2,

    # group 2
    'cs':    0x2E,
    'ds':    0x3E,
    'es':    0x26,
    'fs':    0x64,
    'gs':    0x65,
    'ss':    0x36,
    'nbhint':0x2E, # only for Jcc
    'bhint': 0x3E, # only for Jcc

    # group 3
    'operand-size': 0x66,

    # group 4
    'address-size': 0x67,

    # rex prefix
    'rex': 0x40,
    }


_pack_formats = {
    'i8':  'b',
    'I8':  'B',
    'i16': 'h',
    'I16': 'H',
    'i32': 'i',
    'I32': 'I',
    'i64': 'l',
    'I64': 'L',
    'f32': 'f',
    'f64': 'd',
    }

def pack(f, n):
    return struct.pack(_pack_formats[f], n)


def translate(file, out):
    pas = AS()
    with open(file) as f:
        for line in f:
            pas.doline(line)
    out.write(pas.resultbin.hex())

if __name__ == '__main__':
    from sys import stdout, argv
    if len(argv) != 2:
        print("Usage: {} xxx.as".format(argv[0]))
    else:
        translate(argv[1], stdout)
