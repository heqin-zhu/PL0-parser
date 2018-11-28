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

END = Token('END','NIL')
LEFT = Token('LEFT','(')
RIGHT = Token('RIGHT',')')
L2 = Token('L2','[')
R2 = Token('R2',']')
COMMA = Token('COMMA',',')
SEMICOLON= Token('SEMICOLON',';')
VOID= Token('VOID','void')
INT = Token('INT','int')
POINTER = Token('POINTER','*')
NUM =Token('NUM','0')
NAME = Token('NAME','id')


class parser(object):
    def __init__(self):
        self.lookahead = None
        self.tokens =None
        self.varibles={'ans':None,'e':e,'pi':pi}
    def match(self,sym=None):
        if sym is None or self.lookahead.type==sym.type:
            try:
                self.lookahead = self.peek
                self.peek = next(self.tokens)
            except StopIteration: self.peek = END
        else:raise Exception('[parse error] Expect {}, got {}'.format(sym,self.lookahead))
    def parse(self,tokens):
        self.tokens=tokens
        self.lookahead = next(self.tokens)
        self.peek = END
        try: self.peek = next(self.tokens)
        except:pass
        try:
            ret = self.statement()
            if self.lookahead == END:
                self.varibles['ans'] = ret
                return ret
            else: print('[parse error] invalid statement')
        except Exception as e:
            print(e)
    def statement(self):
        pass



class declarationParser(parser):
    type_size = {'INT':1,'POINTER':1,'VOID':1}
    def statement(self):
        '''non-terminate-symbol: translation_unit'''
        while self.lookahead!=END:
            self.declaration()
    def declaration(self):
        symType = self.declaration_specifiers()
        self.init_declarator_list(symType)
        self.match(SEMICOLON)
    def declaration_specifiers(self):
        return self.type_specifier()
    def type_specifier(self):
        sym = self.lookahead
        if sym==VOID or sym==INT:
            self.match()
        else:self.match(INT)
        return sym.type
    def init_declarator_list(self,symType):
        while 1:
            self.init_declarator(symType)
            if self.lookahead==COMMA:
                self.match()
            else:break
    def init_declarator(self,symType):
        lst = self.declarator()
        lst.append(('type',symType))
        #print(lst)
        s = self.parseAllType(lst)
        print(s)
    def declarator(self):
        np = 0
        if self.lookahead ==POINTER:
            np = self.pointer()
        lst = self.direct_declarator()
        return lst+[('pointer',np)]
    def direct_declarator(self):
        flags=[]
        if self.lookahead.type=='NAME':
            ident= ('id',self.lookahead.value)
            flags=[ident]
            self.match()
        elif self.lookahead == LEFT:
            self.match()
            flags= self.declarator()
            self.match(RIGHT)
        else:self.match(LEFT)
        last=None
        funcArg = None
        funcRet = []
        while 1:
            if self.lookahead==LEFT:
                if last =='arr':
                    flags[0] = ('error','Array of Functions is not allowed')
                last = 'func'
                self.match()
                if self.lookahead!=RIGHT:
                    funcArg = self.parameter_type_list()
                else: funcArg=[]
                self.match(RIGHT)
            elif self.lookahead==L2:
                self.match()
                s = self.lookahead.value
                self.match(NUM)
                tp = ('array',int(s))
                if funcArg is None:  flags.append(tp)
                else: funcRet.append(tp)
                if last =='func':
                    flags[0] = ('error','Array of Function can not be returned from functions')
                last = 'arr'
                self.match(R2)
            else:break
        if funcArg is not None: 
            flags.append(('func',funcArg))
            flags += funcRet
        return flags
    def pointer(self):
        n = 1
        self.match(POINTER)
        while self.lookahead==POINTER:
            n+=1
            self.match(POINTER)
        return n
    def parameter_type_list(self):
        return self.parameter_list()
    def parameter_list(self):
        ret = []
        while 1:
            lst,symType = self.parameter_declaration()
            lst.append(('type',symType))
            ret.append(lst)
            if self.lookahead==COMMA:
                self.match()
            else:break
        return ret
    def parameter_declaration(self):
        symType = self.declaration_specifiers()
        return self.declarator(),symType
    def parseAllType(self,lst):
        def parseType(segs):
            ret = ''
            for tup in segs[::-1]:
                if tup[0]=='type':
                    ret = tup[1]
                elif tup[0]=='pointer' and tup[1]!=0:
                    ret = 'pointer('*tup[1] + ret + ')'*tup[1]
                elif tup[0] =='array':
                    ret = 'array({n},{s})'.format(n = tup[1],s = ret)
            size = 1
            for seg in segs:
                if seg[0]=='array':size*=seg[1]
                else:
                    if seg[0]=='pointer': size *= self.type_size['POINTER']
                    else:
                        print(seg)
                        size *=self.type_size[seg[1].upper()]
                    break
            return ret,size

        if lst[0][0]=='error':return 'Error: ' + lst[0][1]
        elif lst[1][0] == 'func':
            segs = []
            for argSeg in lst[1][1]:
                argType,size = parseType(argSeg[1:])
                s = 'Parameter {arg}, size: {size}, type: {s}'.format(arg = argSeg[0][1],s = argType,size = size)
                segs.append(s)
            retType,size = parseType(lst[2:])
            s = 'Function  {func}, return type: {s}'.format(func = lst[0][1],s = retType)
            segs.append(s)
            return '\n'.join(segs)
        else:
            varType, size = parseType(lst[1:])
            return 'Varible   {var}, size: {size}, type: {s}'.format(var = lst[0][1],s = varType,size = size)

def testFromStdIO():
    dp = declarationParser()
    while 1:
        s = input('>> ')
        tk = gen_token(s)
        dp.parse(tk)
def testFromFile(f= 'test.txt'):
    dp = declarationParser()
    with open(f,'r') as fp:
        for line in fp:
            line = line.strip(' \n')
            if line.startswith('//') or line=='' :continue
            print('>>',line)
            tk = gen_token(line)
            dp.parse(tk)
            print()

if __name__=='__main__':
    testFromFile()
    testFromStdIO()
