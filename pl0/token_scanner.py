'''
#########################################################################
# File : token_scanner.py
# Author: mbinary
# Mail: zhuheqin1@gmail.com
# Blog: https://mbinary.coding.me
# Github: https://github.com/mbinary
# Created Time: 2018-09-17  22:20
# Description: 
#########################################################################
'''

import re
from collections import namedtuple as nt


NAME = r'(?P<NAME>[a-zA-Z_][a-zA-Z_0-9]*)'
NUM = r'(?P<NUM>\d*\.\d+|\d+)' # note that don't use \d+|\d*\.\d+

ASSIGN = r'(?P<ASSIGN>\:\=)'

# ODD = r'(?P<ODD>odd )'
EQ = r'(?P<EQ>=)'
NEQ = r'(?P<NEQ>\<\>)'
GT = r'(?P<GT>\>)'
LT = r'(?P<LT>\<)'
GE = r'(?P<GE>\>\=)'
LE = r'(?P<LE>\<\=)'

BITNOT = r'(?P<BITNOT>\~)'
BITOR = r'(?P<BITOR>\|)'
BITAND = r'(?P<BITAND>\&)'
RSHIFT = r'(?P<RSHIFT>\>\>)'
LSHIFT = r'(?P<LSHIFT>\<\<)'

AND = r'(?P<AND>\&\&)'
NOT = r'(?P<NOT>\!)'
OR = r'(?P<OR>\|\|)'

ADD = r'(?P<ADD>\+)'
SUB=r'(?P<SUB>\-)'

MUL = r'(?P<MUL>\*)'
INTDIV = r'(?P<INTDIV>\/\/)'
MOD = r'(?P<MOD>\%)'
DIV = r'(?P<DIV>\/)'

POW = r'(?P<POW>\^)'
FAC=r'(?P<FAC>\!)'  #factorial

COMMA = r'(?P<COMMA>\,)'
SEMICOLON = r'(?P<SEMICOLON>\;)'
PERIOD = r'(?P<PERIOD>\.)'
LEFT=r'(?P<LEFT>\()'
RIGHT=r'(?P<RIGHT>\))'
WS = r'(?P<WS>\s+)'

li = [NUM, AND,OR,BITAND,BITOR,BITNOT,RSHIFT,LSHIFT,
      EQ,NEQ,GT,LT,GE,LE,\
      SUB,MOD, ADD, MUL,INTDIV,DIV, POW,FAC,NOT,\
      COMMA,SEMICOLON,PERIOD, WS,LEFT,RIGHT,\
      ASSIGN,NAME]
master_pat = re.compile('|'.join(li))

Token = nt('Token',['type','value'])
def gen_token(text):
    scanner = master_pat.scanner(text)
    for m in iter(scanner.match,None):
        tok = Token(m.lastgroup,m.group())
        if tok.type!='WS':
            yield tok
if __name__ =='__main__':
    while 1:
        expr = input('>> ')
        for i in gen_token(expr):
            print(i)
