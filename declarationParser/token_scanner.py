'''
#########################################################################
# File : token_scanner.py
# Author: mbinary
# Mail: zhuheqin1@gmail.com
# Blog: https://mbinary.coding.me
# Github: https://github.com/mbinary
# Created Time: 2018-11-01  12:58
# Description: 
#########################################################################
'''
import re
from collections import namedtuple as nt


NAME = r'(?P<NAME>[a-zA-Z_][a-zA-Z_0-9]*)'
NUM = r'(?P<NUM>\d*\.\d+|\d+)' # note that don't use \d+|\d*\.\d+

POINTER = r'(?P<POINTER>\*)'
COMMA = r'(?P<COMMA>\,)'
SEMICOLON = r'(?P<SEMICOLON>\;)'

VOID=r'(?P<VOID>void)'
INT = r'(?P<INT>int)'
LEFT=r'(?P<LEFT>\()'
RIGHT=r'(?P<RIGHT>\))'
L2 = r'(?P<L2>\[)'
R2 = r'(?P<R2>\])'
WS = r'(?P<WS>\s+)'

'''
bitnot = r'(?p<bitnot>\~)'
bitor = r'(?p<bitor>\|)'
bitand = r'(?p<bitand>\&)'
rshift = r'(?p<rshift>\>\>)'
lshift = r'(?p<lshift>\<\<)'

add = r'(?p<add>\+)'
sub=r'(?p<sub>\-)'
mul = r'(?p<mul>\*)'
intdiv = r'(?p<intdiv>\/\/)'
mod = r'(?p<mod>\%)'
DIV = r'(?P<DIV>\/)'
EQ = r'(?P<EQ>=)'

EXP = r'(?P<EXP>\^)'
FAC=r'(?P<FAC>!)'  #factorial

master_pat = re.compile('|'.join([LEFT,RIGHT,BITAND,BITOR,BITNOT,RSHIFT,LSHIFT, NUM,SUB,MOD, ADD, MUL,INTDIV,DIV, EXP,EQ, WS,FAC,NAME]))
'''

master_pat = re.compile('|'.join([LEFT,RIGHT,L2,R2,POINTER,COMMA,SEMICOLON,INT,VOID,NUM, WS,NAME]))

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

