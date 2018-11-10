'''
#########################################################################
# File : parser.py
# Author: mbinary
# Mail: zhuheqin1@gmail.com
# Blog: https://mbinary.coding.me
# Github: https://github.com/mbinary
# Created Time: 2018-11-04  19:50
# Description: 
#########################################################################
'''
import sys
import argparse
from math import e,pi,log
from functools import reduce
from token_scanner import gen_token,Token
from operator import eq,ge,gt,ne,le,lt, not_,and_,or_,lshift,rshift, add,sub,mod,mul,pow,abs,neg


parser = argparse.ArgumentParser()

parser.add_argument('-i','--instruction',action='store_true')
parser.add_argument('-f','--file',type=str)

args = parser.parse_args()

FILE = args.file
hasIns = args.instruction

# reserved  keywords  
# IF,ELSE,THEN,BREAK,CONTINUE,WHILE,BEGIN,END,DO,CALL,PROC,CONST,VAR, ODD

THEN = Token('NAME','then')
ELSE = Token('NAME','else')
DO = Token('NAME','do')
END = Token('NAME','end')

ASSIGN = Token('ASSIGN',':=')
EQ = Token('EQ','=')
LEFT = Token('LEFT','(')
RIGHT = Token('RIGHT',')')
COMMA=Token('COMMA',',')
SEMICOLON = Token('SEMICOLON',';')
PERIOD = Token('PERIOD','.')
COLON = Token('COLON',':')
EOF = Token('EOF','$')

class symbol:
    '''for func type, it may have args, argNum ... attrs'''
    def __init__(self,name,varType,value=None,level=None,addr = None):
        self.name = name
        self.type = varType
        self.value = value
        self.level = level
        self.addr=addr
    def __str__(self):
        return "{} {}={} at lv {}, addr {}".format(self.type,self.name,self.value,self.level,self.addr)
    def __repr__(self):
        return "symbol('{}','{}',{},{},{})".format(self.name,self.type,self.value,self.level,self.addr)
class stack:
    '''emulate a stack that with pre-allocated space'''
    def __init__(self,lst,size=1000):
        self.lst = lst.copy()
        self.top=2
        self.lst+=[0]*(size-len(lst))

    def push(self,val):
        self.top+=1
        if self.top>=len(self.lst):
            raise Exception('[Error]: data stack overflow')
        self.lst[self.top]=val
    def pop(self):
        self.top -=1
        return self.lst[self.top+1]
    def __setitem__(self,k,val):
        self.lst[k]=val
    def __getitem__(self,k):
        return self.lst[k]
    def __str__(self):
        return str(self.lst)
    def __repr__(self):
        return 'stack({})'.format(self.lst)
class parser(object):
    def __init__(self,tokens=None,syms=None,codes=None):
        self.tokens = [] if tokens is None else tokens
        self.codes = [] if codes is None else codes
        self.pointer = 0
        self.level = 0
        self.ip=0
        self.codes=[]
        self.initSymbol(syms)
    def initSymbol(self,syms=None):
        if syms is None: syms=[symbol('E','CONST',e,0),symbol('PI','CONST',pi,0)]
        self.symbols ={}
        for i in syms:
            self.addSymbol(i.name,i.type,i.value)
    def addSymbol(self,var,varType,value=None,addr=None,func=None):
        if self.level not in self.symbols:
            self.symbols[self.level] = []
        lv = self.symbols[self.level]
        for i in lv:
            if i.name==var:
                self.errorInfo()
                raise Exception('[Error]: {} "{}" has been defined'.format(varType.lower(),var))
        sym = symbol(var,varType,value,self.level,addr)
        if func is not None:
            func.args[var] = sym
        else: lv.append(sym)
        return sym
    def getSymbol(self,var,isFunc=False):
        if not isFunc and self.curFunc is not None:
            if var in self.curFunc.args:return self.curFunc.args[var]
        level = self.level
        while level >=0:
            if level in self.symbols:
                lv = self.symbols[level]
                for sym in lv:
                    if sym.name==var:
                        return sym
            level-=1
        self.errorDefine(var)
    def genIns(self,f,l,a):
        self.codes.append((f,l,a))
        self.ip+=1
        return self.ip-1
    def interpret(self):
        def base(stk,curLevel,levelDiff):
            for i in range(levelDiff):
                curLevel = stk[curLevel]
            return curLevel

        b = 0
        stk = stack([0,0,0])
        pc=0
        reg = None
        while 1:
            ins = self.codes[pc]
            pc+=1
            if ins[0]=='INT':
                stk.top+=ins[2]-3
            elif ins[0]=='LIT':
                stk.push(ins[2])
            elif ins[0]=='STO':
                pos = base(stk,b,ins[1])+ins[2]
                stk[pos]= stk.pop()
            elif ins[0]=='LOD':
                val = stk[base(stk,b,ins[1])+ins[2]]
                stk.push(val)
            elif ins[0]=='MOV':
                stk[stk.top-ins[2]] = stk[stk.top-ins[1]]
            elif ins[0]=='JMP':
                pc = ins[2]
            elif ins[0]=='JPC':
                if not stk.pop():
                    pc = ins[2]
            elif ins[0]=='CAL':
                stk.push(base(stk,b,ins[2]))  # static link  
                stk.push(b)       # dynamic link
                b = stk.top-1
                stk.push(pc)      # return addr
                pc = ins[2]
            elif ins[0]=='PRT':
                stk.top = stk.top-ins[2]+1
                for i in range(ins[2]):
                    print(stk[stk.top+i],end=' ')
                print()
                stk.top-=1
            elif ins[0]=='OPR':
                if ins[2]=='BACK':
                    stk.top-=ins[1]
                elif ins[1]==1:
                    stk[stk.top] = self.unaryOPR[ins[2]](stk[stk.top])
                elif ins[1]==2:
                    arg2 = stk.pop()
                    arg1 = stk[stk.top]
                    stk[stk.top] = self.binaryOPR[ins[2]](arg1,arg2)
                if ins[1]==0:
                    if ins[2] =='RET':
                        pc = stk[b+2]
                        if pc!=0: stk.top=b-1
                        b = stk[b+1]
                    elif ins[2]=='POP':
                        reg = stk.pop()
                    elif ins[2]=='PUSH':
                        stk.push(reg)
                    else:self.errorIns(ins,pc-1)
            else:
                self.errorIns(ins,pc-1)
            #print(ins,stk[:stk.top+1])
            if pc==0:break
        return stk[3:stk.top+1]
    def errorInfo(self):
        tk = self.tokens[self.pointer]
        a=b = self.pointer
        lineno = tk.lineNum
        n = len(self.tokens)
        while a>=0 and self.tokens[a].lineNum == lineno:
            a -=1
        while b<n and self.tokens[b].lineNum == lineno:
            b +=1
        s1 = ' '.join([str(t.value) for t in self.tokens[a+1:self.pointer]])
        s2 = ' '.join([str(t.value) for t in self.tokens[self.pointer:b]])
        print('line {}: {} {}'.format(lineno,s1,s2))
        print(' '*(len(s1)+8+len(str(lineno)))+'^'*len(str(tk.value)))
        return tk
    def errorIns(self,ins,pc):
        print('[Error]: Unknown instruction {}: {}  '.format(pc,ins))
    def errorDefine(self,var):
        self.errorInfo()
        raise Exception('[Error]: "{}" is not defined'.format(var))
    def errorArg(self,n1,n2):
        self.errorInfo()
        raise Exception('[Error]: Expect {} args, but {} given'.format(n1,n2))
    def errorExpect(self,s):
        tk = self.errorInfo()
        raise Exception('[Error]: Expect {}, got "{}"'.format(s,tk.value))
    def errorLoop(self,s):
        self.errorInfo()
        raise Exception('[Error]: "{}" outside loop'.format(s))
    def match(self,sym=None):
        #print(self.tokens[self.pointer])
        if sym is None \
           or (sym.type=='NUM' and self.isType('NUM')) \
           or sym==self.tokens[self.pointer]:
            self.pointer+=1
            return self.tokens[self.pointer-1]
        self.errorExpect('"'+sym.value+'"')
    def parse(self,tokens=None):
        self.ip=0
        self.codes=[]
        self.pointer=0
        self.curFunc = None
        if tokens is not None: self.tokens = tokens
        if self.tokens is None:
            return
        try:
            self.program()
            if hasIns:
                for i,ins in enumerate(self.codes):print(str(i).ljust(5),ins)
            if self.pointer != len(self.tokens):
                print('[Error]: invalid syntax')
            result =self.interpret()
            for sym,val in zip(self.varibles,result):
                sym.value=val
            res = result[len(self.varibles):]
            if res!=[]: print('result: ',end='')
            for i in res:
                print(i,end=', ')
            if res!=[]: print()
        #try:pass
        except Exception as e:
            print(e)

    def isType(self,s):
        if self.pointer == len(self.tokens):sym = EOF
        else:    sym = self.tokens[self.pointer]
        if s in self.reserved: return sym.value==s.lower()
        if s =='NAME' and sym.value.upper() in self.reserved: return False
        return sym.type ==s
    def isAnyType(self,lst):
        return any([self.isType(i) for i in lst])
    def wantType(self,s):
        if not self.isType(s): self.errorExpect(s)
    def program(self):
        pass

class PL0(parser):
    def __init__(self,tokens=None,syms=None,codes=None,level=0):
        super().__init__()
        self.reserved={'FUNC','PRINT','RETURN','BEGIN','END','IF','THEN','FOR','ELIF','ELSE','WHILE','DO','BREAK','CONTINUE','VAR','CONST','ODD'}
        self.bodyFirst= self.reserved.copy()
        self.bodyFirst.remove('ODD')
        self.relationOPR= {'EQ':eq,'NEQ':ne,'GT':gt,'LT':lt,'GE':ge,'LE':le} # odd
        self.conditionOPR = {'AND':and_,'OR':or_, 'NOT':not_}
        self.conditionOPR.update(self.relationOPR)
        self.arithmeticOPR = {'ADD':add,'SUB':sub,'MOD':mod,'MUL':mul,'POW':pow,'DIV':lambda x,y:x/y,'INTDIV':lambda x,y:round(x)//round(y) }
        self.bitOPR = {'LSHIFT':lambda x,y:round(x)<<round(y),'RSHIFT':lambda x,y:round(x)>>round(y),'BITAND':lambda x,y:round(x)&round(y), 'BITOR':lambda x,y:round(x)|round(y),'BITNOT':lambda x:~round(x)}
        self.binaryOPR = dict()
        self.binaryOPR.update(self.conditionOPR)
        del self.binaryOPR['NOT']
        self.binaryOPR.update(self.arithmeticOPR)
        self.binaryOPR.update(self.bitOPR)
        del self.binaryOPR['BITNOT']
        self.unaryOPR = {'NEG':neg,'NOT':not_,'BITNOT':lambda x:~round(x),'FAC':lambda x:reduce(mul,range(1,round(x)+1),1),'ODD':lambda x:round(x)%2==1}#abs

    def program(self):
        self.enableJit = False
        self.genIns('JMP',0,None)
        ip,_= self.body()
        self.codes[0]=('JMP',0,ip)
        self.match(PERIOD)
        self.genIns('OPR',0,'RET')
    def body(self,varCount = 0,func=None):
        while 1:
            if self.isType('CONST'):
                self.match()
                while 1:
                    self.wantType('NAME')
                    name = self.match().value
                    self.match(EQ)
                    self.wantType('NUM')
                    num = float(self.match().value)
                    self.addSymbol(name,'CONST',num,func=func)
                    if self.isType('SEMICOLON'):
                        self.match()
                        break
                    self.match(COMMA)
            elif self.isType('VAR'):
                self.match()
                while 1:
                    self.wantType('NAME')
                    name = self.match().value
                    self.addSymbol(name,'VAR',addr = varCount+3,func=func)
                    varCount+=1
                    if self.isType('SEMICOLON'):
                        self.match()
                        break
                    self.match(COMMA)
            elif self.isType('FUNC'):
                self.match()
                self.wantType('NAME')
                name = self.match().value
                args = self.arg_list()
                beginIp  = self.genIns('INT',0,None)
                sym = self.addSymbol(name,'FUNC',None,beginIp)
                self.level +=1
                sym.args={}
                n = len(args)
                sym.argNum = n
                ips=[]
                for i,arg in enumerate(args):
                    argSym = symbol(arg,'VAR',level=self.level,addr=i+3)
                    sym.args[arg] = argSym
                    ips.append(self.genIns('MOV',None,None))
                saved = self.curFunc
                self.curFunc = sym
                _,nvar = self.body(n,sym)
                self.curFunc = saved
                span1 = nvar -n
                span2 = 3+nvar
                for i ,ip in enumerate(ips):
                    self.codes[ip] = ('MOV',span2+i,span1+i)
                self.match(SEMICOLON)
                self.codes[beginIp] = ('INT',0,nvar+3)
                self.level -=1
                self.genIns('OPR',0,'RET')
            else:break
        ret = None
        if self.level ==0:
            self.varibles =[sym for sym in  self.symbols[0] if sym.type=='VAR']
            n= len(self.varibles)
            ret = self.genIns( 'INT',0,n+3) #varCount+3)
            for sym in self.varibles:
                if sym.value is not None:
                    self.genIns('LIT',0,sym.value)
                    self.genIns('STO',0,sym.addr)
        if not  self.isType('PERIOD'):
            for ip in self.sentence()['RETURN']:
                self.codes[ip] = ('JMP',0,self.ip)
        return ret,varCount
    def arg_list(self):
        self.match(LEFT)
        li = []
        if not self.isType('RIGHT'):
            self.wantType('NAME')
            li=[self.match().value]
        while self.isType('COMMA'):
            self.match()
            self.wantType('NAME')
            li.append(self.match().value)
        self.match(RIGHT)
        return li
    def real_arg_list(self):
        self.match(LEFT)
        ct=0
        if not  self.isType('RIGHT'):
            self.sentenceValue()
            ct+=1
        while self.isType('COMMA'):
            self.match()
            self.sentenceValue()
            ct+=1
        self.match(RIGHT)
        return ct
    def sentence_list(self,outerLoop=None):
        ret = self.sentence(outerLoop)
        while self.isType('SEMICOLON'):
            self.match()
            dic=self.sentence(outerLoop)
            for i in ['BREAK','CONTINUE','RETURN']:
                ret[i] = ret[i].union(dic[i])
        return ret
    def sentence(self,outerLoop=None):
        ret ={'BREAK':set(),'CONTINUE':set(),'RETURN':set()}
        if self.isType('BEGIN'):
            self.match()
            ret = self.sentence_list(outerLoop)
            self.match(END)
        elif self.isType('PRINT'):
            self.match()
            n = self.real_arg_list()
            self.genIns('PRT',0,n)
        elif self.isType('BREAK'):
            if outerLoop is None: self.errorLoop('break')
            self.match()
            ret['BREAK'].add(self.genIns('JMP',0,None))
        elif self.isType('CONTINUE'):
            self.match()
            if outerLoop is None: self.errorLoop('continue')
            ret['CONTINUE'].add(self.genIns('JMP',0,None))
        elif self.isType('IF'):
            self.match()
            self.sentenceValue()
            self.match(THEN)
            jpcIp = self.genIns('JPC',0,None)
            ret = self.sentence(outerLoop)
            jmpIps = []
            while self.isType('ELIF'):
                self.match()
                ip = self.genIns('JMP',None,None)
                jmpIps.append(ip)
                self.codes[jpcIp] = ('JPC',0,self.ip)
                self.sentenceValue()
                jpcIp = self.genIns('JPC',0,None)
                self.match(THEN)
                dic=self.sentence(outerLoop)
                for i in ['BREAK','CONTINUE','RETURN']:
                    ret[i] = ret[i].union(dic[i])

            if self.isType('ELSE'):
                self.match()
                ip = self.genIns('JMP',0,None)
                jmpIps.append(ip)
                self.codes[jpcIp] = ('JPC',0,self.ip)
                dic=self.sentence(outerLoop)
                for i in ['BREAK','CONTINUE','RETURN']:
                    ret[i] = ret[i].union(dic[i])
            else:
                self.codes[jpcIp] = ('JPC',0,self.ip)
            for ip in jmpIps:
                self.codes[ip] = ('JMP',0,self.ip)
        elif self.isType('WHILE') or self.isType('FOR'):
            tp = self.match()
            beginIp = jpcIp =None
            if tp.value=='while':
                beginIp = self.ip
                self.sentenceValue()
                jpcIp = self.genIns('JPC',0,None)
                self.match(DO)
            else:
                self.match(LEFT)
                if not self.isType('SEMICOLON'):
                    self.assignment()
                self.match(SEMICOLON)
                beginIp = self.ip
                if not self.isType('SEMICOLON'):
                    self.sentenceValue()
                    jpcIp = self.genIns('JPC',0,None)
                self.match(SEMICOLON)
                if not self.isType('RIGHT'):
                    self.assignment()
                self.match(RIGHT)
            ret  = self.sentence(1)
            self.genIns('JMP',0,beginIp)
            self.codes[jpcIp] = ('JPC',0,self.ip)
            for jmpip in ret['BREAK']:
                self.codes[jmpip] = ('JMP',0,self.ip)
            for jmpip in ret['CONTINUE']:
                self.codes[jmpip] = ('JMP',0,beginIp)
        elif self.isType('RETURN'): # retrun sentence
            self.match()
            self.sentenceValue()
            self.genIns('OPR',0,'POP')
            ret['RETURN'].add(self.genIns('JMP',0,None))
        elif self.isAnyType(['SEMICOLON','END','ELSE']):pass # allow blank sentence: namely   ; ;; 
        elif self.isAssignment() : # this must be the last to be checked in sentences
            self.assignment()
        else:
            self.sentenceValue()
        return ret
    def funcall(self):
        name = self.match().value
        sym = self.getSymbol(name,True)
        saved = self.curFunc
        self.curFunc = sym
        n2= self.real_arg_list()
        self.curFunc = saved
        if sym.argNum!=n2:
            self.errorArg(sym.argNum,n2)
        self.genIns('CAL',abs(self.level-sym.level),sym.addr)
        self.genIns('OPR',n2,'BACK')
        self.genIns('OPR',0,'PUSH')
    def sentenceValue(self):
        self.condition()
    def isAssignment(self):
        return self.isType('NAME') \
           and self.pointer+1<len(self.tokens)\
           and self.tokens[self.pointer+1]==ASSIGN

    def assignment(self):
        varLst = []
        while self.isAssignment():
            varLst .append(self.match().value)
            self.match(ASSIGN)
        self.sentenceValue()
        sym0 = self.getSymbol(varLst[0])
        lastLevel=abs(self.level-sym0.level)
        lastAddr = sym0.addr
        self.genIns('STO',lastLevel,sym0.addr)
        for var in varLst[1:]:
            sym = self.getSymbol(var)
            if sym.type=='CONST':
                raise Exception('[Error]: Const "{}" can\'t be reassigned'.format(sym.name))
            self.genIns('LOD',lastLevel,lastAddr)
            lastLevel = abs(self.level-sym.level)
            lastAddr = sym.addr
            self.genIns('STO',lastLevel,sym.addr)
    def condition(self):
        self.condition_and()
        while self.isType('OR'):
            self.match()
            self.condition_and()
            self.genIns('OPR',2,'OR')
        if self.isType('QUESTION'): # 即条件表达式  condition ? expr1 : expr2
            self.match()
            ip = self.genIns('JPC',0,None)
            self.sentenceValue()
            ip2 = self.genIns('JMP',0,None)
            self.match(COLON)
            self.codes[ip] = ('JPC',0,self.ip)
            self.sentenceValue()
            self.codes[ip2] = ('JMP',0,self.ip)
    def condition_and(self):
        self.condition_not()
        while self.isType('AND'):
            self.match()
            self.condition_not()
            self.genIns('OPR',2,'AND')
    def condition_not(self):
        ct = 0
        while self.isType('NOT'):
            self.match()
            ct+=1
        self.condition_unit()
        if ct%2==1:
            self.genIns('OPR',1,'NOT')
    def condition_unit(self):
        if self.isType('ODD'):
            self.match()
            self.expression()
            self.genIns('OPR',1,'ODD')
            return
        self.expression()  # 允许 表达式作为逻辑值, 即 非0 为真, 0 为假
        if self.isAnyType(self.relationOPR):
            op = self.match().type
            self.expression()
            self.genIns('OPR',2,op)
    def expression(self):
        self.level1()
        while 1:   # interval production,  optimized tail recursion and merged it
            if self.isType('RSHIFT'):
                self.match()
                self.level1()
                self.genIns('OPR',2,'RSHIFT')
            elif self.isType('LSHIFT'):
                self.match()
                self.level1()
                self.genIns('OPR',2,'LSHIFT')
            elif self.isType('BITAND'):
                self.match()
                self.level1()
                self.genIns('OPR',2,'BITAND')
            elif self.isType('BITOR'):
                self.match()
                self.level1()
                self.genIns('OPR',2,'BITOR')
            else:
                return
    def item(self):
        if self.isType('NUM'):
            val = float(self.match().value)
            self.genIns('LIT',0,val)
        elif self.isType('STR'):
            val = self.match().value
            self.genIns('LIT',0.,val)
        elif self.isType('LEFT'):
            self.match()
            self.sentenceValue()
            self.match(RIGHT)
        elif self.isType('SUB'):
            self.match()
            self.item()
            self.genIns('OPR',1,'NEG')
        elif self.isType('ADD'):
            self.match()
            self.item()
        elif self.isType('BITNOT'):
            self.match()
            self.item()
            self.genIns('OPR',1,'BITNOT')
        elif self.isType('NAME'):
            if self.tokens[self.pointer+1] == LEFT:
                self.funcall()
            else:
                name = self.match().value
                sym = self.getSymbol(name)
                if sym.type=='CONST':
                    self.genIns('LIT',0,sym.value)
                else:
                    self.genIns('LOD',abs(self.level-sym.level),sym.addr)
        else:
            self.errorExpect('a varible or const or num')
    def level1(self):
        self.level2()
        while 1:
            if self.isType('ADD'):
                self.match()
                self.level2()
                self.genIns('OPR',2,'ADD')
            elif self.isType('SUB'):
                self.match()
                self.level2()
                self.genIns('OPR',2,'SUB')
            else: return
    def level2(self):
        self.level3()
        while 1:
            if self.isType('MUL'):
                self.match()
                self.level3()
                self.genIns('OPR',2,'MUL')
            elif self.isType('DIV'):
                self.match()
                self.level3()
                self.genIns('OPR',2,'DIV')
            elif self.isType('INTDIV'):
                self.match()
                self.level3()
                self.genIns('OPR',2,'INTDIV')
            elif self.isType('MOD'):
                self.match()
                self.level3()
                self.genIns('OPR',2,'MOD')
            else:return
    def level3(self):
        self.level4()
        if self.isType('POW'):
            self.match()
            self.level3()
            self.genIns('OPR',2,'POW')
        return
    def level4(self):
        self.item()
        while self.isType('FAC'):#factorial
            self.match()
            self.genIns('OPR',1,'FAC')

def getCode(inStream):
    lines = []
    eof = False
    while 1:
        line = inStream.readline()
        if line=='':
            eof = True
            break
        lines.append(line)
        p = line.find('//')
        if p==-1 and line.rstrip('\n\t\r ').endswith('.'):break
    if eof and len(lines)==0: raise EOFError
    return lines,inStream

def testFromStdIO():
    cal = PL0()
    while 1:
        sys.stdout.write('>> ')
        sys.stdout.flush()
        lines,sys.stdin = getCode(sys.stdin)
        s = ''.join(lines)
        tk =[i for i in  gen_token(s)]
        if tk==[]:continue
        res = cal.parse(tk)
        if res is not None: print(res)
def testFromFile(f):
    cal = PL0()
    with open(f,'r') as fp:
        try:
            while 1:
                lines,fp = getCode(fp)
                if len(lines)==1: print('>>',lines[0].strip('\n'))
                else:
                    print('>> File: "{}"'.format(f))
                    for i,l in enumerate(lines):
                        print(str(i+1).ljust(5),l,end='')
                tk =[i for i in  gen_token(''.join(lines))]
                if tk ==[]:continue
                res = cal.parse(tk)
                if res is not None: print(res)
        except EOFError:
            pass
if __name__=='__main__':
    if FILE:
        testFromFile(FILE)
    else:
        testFromStdIO()
