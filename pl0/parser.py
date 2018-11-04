'''
#########################################################################
# File : parser.py
# Author: mbinary
# Mail: zhuheqin1@gmail.com
# Blog: https://mbinary.coding.me
# Github: https://github.com/mbinary
# Created Time: 2018-09-17  22:19
# Description: 
#########################################################################
'''

from math import e,pi,log
from token_scanner import gen_token,Token
from operator import eq,ge,gt,ne,le,lt, not_,and_,or_,lshift,rshift, add,sub,mod,mul,pow,abs,neg
#div , intdiv, fac, odd

'''
NUM, BITAND,BITOR,BITNOT,RSHIFT,LSHIFT,
EQ,NEQ,GT,LT,GE,LE,
SUB,MOD, ADD, MUL,INTDIV,DIV, POW,FAC,
COMMA,SEMICOLON,PERIOD, WS,LEFT,RIGHT,
NAME,ASSIGN
'''

# reserved  keywords   small case
# IF,ELSE,THEN,BREAK,CONTINUE,WHILE,BEGIN,END,DO,CALL,PROC,CONST,VAR, ODD

THEN = Token('NAME','then')
ELSE = Token('NAME','else')
DO = Token('NAME','do')
END = Token('NAME','end')

ASSIGN = Token('ASSIGN',':=')
EQ = Token('EQ','=')
RIGHT = Token('RIGHT',')')
COMMA=Token('COMMA',',')
SEMICOLON = Token('SEMICOLON',';')
PERIOD = Token('PERIOD','.')

EOF = Token('EOF','$')

class symbol:
    def __init__(self,name,value,varType='VAR'):
        self.name = name
        self.type = varType
        self.value = value
    def __str__(self):
        return self.__repr__()
    def __repr__(self):
        return "symbol('{}',{},'{}')".format(self.name,self.value,self.type)
class parser(object):
    def __init__(self,tokens=None,syms=None,codes=None,level=0):
        self.tokens = [] if tokens is None else tokens
        self.codes = [] if codes is None else codes
        self.pointer = len(self.tokens)
        self.ip = len(self.codes)
        self.level = level
        self.reserved=set()
        # self.closure = Closure({sym.name:sym for sym in syms})
        self.setLock = False # if True, can't set symbol' value
        self.initSymbol(syms)
    def initSymbol(self,syms=None):
        if syms is None: syms=[symbol('ans',None,'VAR'),symbol('E',e,'CONST'),symbol('PI',pi,'CONST')]
        self.symbols =[]
        self.nameId = {}
        for i in syms:
            self.setSymbol(i.name,i.value,i.type,isAddSymbol=True)
    def setSymbol(self,var,val=None,varType='VAR',isAddSymbol=False):
        if self.setLock:return
        level = self.level
        while level>=0:
            if (level,var) in self.nameId:
                index = self.nameId[(level,var)]
                if self.symbols[index].type=='CONST':
                    raise Exception('[Error]: Const "{}" can\'t be reassigned'.format(var))
                self.symbols[index].value =val
                break
            level -=1
        else:
            if isAddSymbol:
                if (self.level,var) in self.nameId:
                    raise Exception('[Error]: {} "{}" has been defined'.format(varType,var))
                self.nameId[(self.level,var)] = len(self.symbols)
                self.symbols.append(symbol(var,val,varType))
            else:
                raise Exception('[Error]: "{}" is assigned before defined'.format(var))
    def getSymbol(self,var):
        level = self.level
        while level >=0:
            if (level,var) in self.nameId:
                return self.symbols[self.nameId[(level,var)]]
            level-=1
        raise Exception('[Error]: "{}" is not defined'.format(var))
    def error(self,s):
        raise Exception('[Error]: Expect "{}", got "{}"'.format(s,self.curSym().value))
    def match(self,sym=None):
        if sym is None \
           or (sym.type=='NUM' and self.isType('NUM')) \
           or sym==self.tokens[self.pointer]:
            self.pointer+=1
            return self.tokens[self.pointer-1]
        self.error(sym.value)
    def parse(self,tokens=None,pointer=0,inheritSymbol=False):
        if tokens is not None: self.tokens = tokens
        if not inheritSymbol: self.initSymbol()
        if self.tokens is None:
            return
        self.pointer= pointer
        try:
            ret,_ = self.statement()
            if self.pointer == len(self.tokens):
                self.setSymbol('ans', ret)
                return ret
            else: print('[Error]: invalid statement')
        except Exception as e:
            print(e)
    def lookahead(self,symbols):
        while self.tokens[self.pointer].type not in symbols:
            self.pointer+=1
            if self.pointer == len(self.tokens):return None
        return self.pointer
    def curSym(self):
        return self.tokens[self.pointer]
    def isType(self,s):
        sym = self.tokens[self.pointer]
        if s in self.reserved: return sym.value==s.lower()
        if s =='NAME' and sym.value.upper() in self.reserved: return False
        return sym.type ==s
    def isAnyType(self,lst):
        return any([self.isType(i) for i in lst])
    def wantType(self,s):
        if not self.isType(s): self.error(s)
    def statement(self):
        pass

class PL0(parser):
    def __init__(self,tokens=None,syms=None,codes=None,level=0):
        super().__init__()
        self.reserved={'CALL','PROCEDURE','BEGIN','END','IF','THEN','ELSE','WHILE','DO','BREAK','CONTINUE','VAR','CONST','ODD'}
        self.bodyFirst={'CALL','PROCEDURE','BEGIN','END','IF','THEN','ELSE','WHILE','DO','BREAK','CONTINUE','VAR','CONST'}
        self.relationOPR= {'EQ':eq,'NEQ':ne,'GT':gt,'LT':lt,'GE':ge,'LE':le} # odd
        self.conditionOPR = {'EQ':eq,'NEQ':ne,'GT':gt,'LT':lt,'GE':ge,'LE':le,'AND':and_,'OR':or_, 'NOT':not_}
        self.arithmeticOPR = {'ADD':add,'SUB':sub,'MOD':mod,'MUL':mul,'POW':pow}
        self.bitOPR = {'LSHIFT':lshift,'RSHIFT':rshift}
        self.binaryOPR ={'EQ':eq,'NEQ':ne,'GT':gt,'LT':lt,'GE':ge,'LE':le,'AND':and_,'OR':or_ \
                        ,'ADD':add,'SUB':sub,'MOD':mod,'MUL':mul,'POW':pow,'LSHIFT':lshift,'RSHIFT':rshift}
        self.unaryOPR = {'NEG':neg,'ABS':abs,'NOT':not_}#'BITNOT'
    def statement(self):
        ret = None
        if self.isAnyType(self.bodyFirst):
            ret = self.body()
        else:
            ret = self.general_expression()
        self.match(PERIOD)
        return ret,self.pointer
    def body(self):
        while 1:
            if self.isType('CONST'):
                self.match()
                while 1:
                    self.wantType('NAME')
                    name = self.match().value
                    self.match(EQ)
                    self.wantType('NUM')
                    num = float(self.match().value)
                    #self.closure.add(name,'CONST',num)
                    self.setSymbol(name,num,'CONST',isAddSymbol=True)
                    if self.isType('SEMICOLON'):
                        self.match()
                        break
                    self.match(COMMA)
            if self.isType('VAR'):
                self.match()
                while 1:
                    self.wantType('NAME')
                    name = self.match().value
                    #self.closure.add(name,'VAR')
                    self.setSymbol(name,varType='VAR',isAddSymbol=True)
                    if self.isType('SEMICOLON'):
                        self.match()
                        break
                    self.match(COMMA)
            if self.isType('PROCEDURE'):
                self.match()
                self.wantType('NAME')
                name = self.match().value
                self.match(SEMICOLON)
                beg = self.ip
                end = self.body()
                #if self.isType('RETURN'):
                self.match(SEMICOLON)
            else:break
        return self.sentence()
    def general_expression(self):
        if self.isType('ODD'):
            return self.condition()
        if self.isType('NAME') \
           and self.pointer+1<len(self.tokens)\
           and self.tokens[self.pointer+1]==ASSIGN:
                self.assignment(isAddSymbol=True)
        else:
            pt = self.pointer
            i = self.lookahead(self.conditionOPR) 
            self.pointer = pt
            if i is not None:
                return self.condition()
            return self.expression()
    def sentence_list(self):
        self.sentence()
        while self.isType('SEMICOLON'):
            self.match()
            self.sentence()
    def sentence(self):
        if self.isType('CALL'):
            self.match()
            self.wantType('NAME')
            name = self.match().value
            # to do
        elif self.isType('BEGIN'):
            self.match()
            self.sentence_list()
            self.match(END)
        elif self.isType('IF'):
            self.match()
            bl = self.condition()
            self.match(THEN)
            '''
            self.setLock = True
            beg = self.pointer
            self.sentence()
            end2 = self.pointer
            if bl: self.parse(inheritSymbol=True)
            if self.isType('ELSE'):
                self.match()
                self.sentence()
                end3 = self.pointer
            '''
            self.sentence()
        elif self.isType('WHILE'):
            self.match()
            self.condition()
            self.match(DO)
            self.sentence()
            ### todo
        elif self.isType('NAME'): # this must be the last to be checked in sentences
            self.assignment()
        # allow blank sentence: namely   ; ;; 
        # else:self.error('sentence symbol: begin/if/call/while')

    def assignment(self,isAddSymbol=False):
        self.wantType('NAME')
        var = self.match().value
        self.match(ASSIGN)
        val = None
        if self.isType('NAME') \
           and self.pointer+1<len(self.tokens)\
           and self.tokens[self.pointer+1]==ASSIGN:
            val = self.assignment(isAddSymbol)
        else: val = self.expression()
        self.setSymbol(var,val,isAddSymbol=isAddSymbol)
        return val
    def condition(self):
        bl = self.condition_and()
        while not bl and self.isType('OR'):
            self.match()
            bl = self.condition_and()
        return bl
    def condition_and(self):
        bl = self.condition_not()
        while bl and self.isType('AND'):
            self.match()
            bl = self.condition_not()
        return bl
    def condition_not(self):
        ct = 0
        while self.isType('NOT'):
            self.match()
            ct+=1
        bl = self.condition_unit()
        return bl if ct%2==0 else not bl

    def condition_unit(self):
        if self.isType('ODD'):
            self.match()
            n = self.expression()
            return round(n)%2==1
        a = self.expression()
        if not self.isAnyType(self.relationOPR):
            self.error('relation operator')
        op = self.match().type
        return self.relationOPR[op](a,self.expression())
    def expression(self):
        a = self.level1()
        while 1:   # interval production,  optimized tail recursion and merged it
            if self.isType('RSHIFT'):
                self.match()
                b = self.level1()
                a = round(a)>>round(b)
            elif self.isType('LSHIFT'):
                self.match()
                b = self.level1()
                a = round(a)<<round(b)
            elif self.isType('BITAND'):
                self.match()
                b = self.level1()
                a = round(a)&round(b)
            elif self.isType('BITOR'):
                self.match()
                b = self.level1()
                a = round(a)|round(b)
            else:  return a
    def item(self):
        if self.isType('NUM'):
            return float(self.match().value)
        elif self.isType('LEFT'):
            self.match()
            ret = self.expression()
            self.match(RIGHT)
            return ret
        elif self.isType('SUB'):
            self.match()
            return -self.item()
        elif self.isType('ADD'):
            self.match()
            return self.item()
        elif self.isType('BITNOT'):
            self.match()
            a = self.item()
            return ~round(a)
        elif self.isType('NAME'):
            name = self.match().value
            return self.getSymbol(name).value
        else:self.error('factor item')
    def level1(self):
        a = self.level2()
        while 1:
            if self.isType('ADD'):
                self.match()
                a+= self.level2()
            elif self.isType('SUB'):
                self.match()
                a-= self.level2()
            else: return a
    def level2(self):
        a = self.level3()
        while 1:
            if self.isType('MUL'):
                self.match()
                a*= self.level3()
            elif self.isType('DIV'):
                self.match()
                a/= self.level3()
            elif self.isType('INTDIV'):
                self.match()
                a//= self.level3()
            elif self.isType('MOD'):
                self.match()
                a%= self.level3()
            else:return a
    def level3(self):
        a = self.level4()
        if self.isType('POW'):
            self.match()
            b = self.level3()
            return a**b
        else: return a
    def level4(self):
        def factorial(n):
            ret=1
            for i in range(2,n+1): ret*=i
            return ret

        a = self.item()
        while self.isType('FAC'):#factorial
            self.match()
            a = factorial(round(a))
        return a

def getCode(inStream):
    lines = []
    eof = False
    while 1:
        line = inStream.readline()
        if line=='':
            eof = True
            break
        line = line.strip(' \n\t\r')
        if line.startswith('//'):continue
        lines.append(line)
        if line.endswith('.'):break
    code = ' '.join(lines)
    if eof :
        if code=='': raise EOFError
        if not code.endswith('.'):
            raise Exception('[Error]: Program not terminated')
    return code,inStream

import sys
def testFromStdIO():
    cal = PL0()
    while 1:
        sys.stdout.write('>> ')
        sys.stdout.flush()
        s,sys.stdin = getCode(sys.stdin)
        if s.lstrip().startswith('//'): continue
        tk =[i for i in  gen_token(s)]
        res = cal.parse(tk,inheritSymbol=True)
        if res is not None: print(res)
def testFromFile(f='test.txt'):
    cal = PL0()
    with open(f,'r') as fp:
        try:
            while 1:
                s,fp = getCode(fp)
                print('>>',s)
                tk =[i for i in  gen_token(s)]
                res = cal.parse(tk,inheritSymbol=True)
                if res is not None: print(res)
        except EOFError:
            pass
if __name__=='__main__':
    testFromFile()
    testFromStdIO()
