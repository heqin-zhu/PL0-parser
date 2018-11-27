# PL0-compiler
> A compiler for c-like programming language **based on** PL0, which is a dynamic, strong typing language.

See grammar [here](#grammar), [wikipedia-PL0](https://en.wikipedia.org/wiki/PL/0), and download [this pdf(zh)](src/编译原理和技术实践2017.pdf) for more details.

# QuickStart
```shell
usage: parser.py [-h] [-i] [-s] [-t] [-v] [-f FILE]

optional arguments:
  -h, --help            show this help message and exit
  -i, --instruction     output instructions
  -s, --stack           output data stack when executing each instruction
  -t, --token           output tokens when parsing
  -v, --varible         output varibles for every static environment
  -f FILE, --file FILE  compile and run codes. Without this arg, enter
                        interactive REPL
```

Run `python parse.py` and enter a REPL state, you can type and run sentences and expressions interactively

# Examples
Note that when in REPL, every sentence or expresion or block ends with '.'. But in program codes, only the whole program ends with a dot.
##  interactive-expression

run command `python parser.py` to enter repl.

Therer are some expressions and sentence in file expr.txt, now test it.
`python parser.py -f test/expr.txt`

```c
>> File: "test/expr.txt"
1
2     // expression
3     var a=3,b=2,c;.
>>  c:=a+1.
>> begin c; c+1!=1 ; c+1=5 end.
result: 4.0; True; True;
>> for(;b>=0;b:=b-1) print('random num below 100:',random(100)) .
random num below 100: 73
random num below 100: 16
random num below 100: 51
>> begin ++1--1; 1<<2+3%2; 2&1 end.
result: 2.0; 8; 0;
>>   -1+2*3/%2.
result: 2.0;
>>    (1+2.
line 1: ( 1 + 2 .
                ^
[Error]: Expected ")", got "."
>> print('const e:',E,'    fac of fac 4:',4!!).
const e: 2.718281828459045     fac of fac 4: 620448401733239439360000
```

## fibonacci
run
`python parser.py  -f test/fibonacci.txt`

```c
>> File: "test/fibnaci.txt"
1     func fib(n)
2     begin
3         if n=1 || n=2 then return 1;
4         return fib(n-1)+fib(n-2);
5     end ;
6
7     var n;
8     begin
9         n :=1;
10        while n<15 do
11        begin
12            print('The ',n,'th fib item is:',fib(n));
13            n :=n+1;
14        end;
15
16    end
17    .
The  1.0 th fib item is: 1.0
The  2.0 th fib item is: 1.0
The  3.0 th fib item is: 2.0
The  4.0 th fib item is: 3.0
The  5.0 th fib item is: 5.0
The  6.0 th fib item is: 8.0
The  7.0 th fib item is: 13.0
The  8.0 th fib item is: 21.0
The  9.0 th fib item is: 34.0
The  10.0 th fib item is: 55.0
The  11.0 th fib item is: 89.0
The  12.0 th fib item is: 144.0
The  13.0 th fib item is: 233.0
The  14.0 th fib item is: 377.0
```
# Description
## ident type
* constant
* varible
* function
## operator
### relation opr
* \<
* \>
* \<=
* \>=
* = equal 
* !=
* odd  
### bit opr
* \& bitand
* \| bitor
* \~ bitnot
* \<\< left shift
* \>\> right shift
### arithmetic opr
* \+  add/plus
* \-  sub/minus
* \*  multiply
* \/  divide
* \/\% integer div
* %  mod
* \^  power
* \!  factorial
### conditon opr
*  ?:  eg   a\>b ? c:d
## control structure
* if elif else
* for
* while
* break
* continue
* return

## builtin function
* print(a,b,c...)
* random(), random(n)

# Grammar
```scala
program =  body "."
body = {varDeclaration ";" |  constDeclaration ";" |  "func" ident "(" arg_list  ")" body ";"}  sentence

varDeclaration = "var"  varIdent { "," varIdent}
varIdent  = ident ["=" number] | ident  { "[" number "]" } 
constDeclaration = "const" ident "=" number {"," ident "=" number}

sentence = [ ident ":=" { ident ":=" } sentenceValue 
                |  "begin" sentence { ";" sentence}  "end"
                |  "if" sentenceValue "then" sentence {"elif" sentence} ["else" sentence]
                |  "while" sentenceValue "do" sentence
                |  "break"
                |  "continue"
                |  ["return"] sentenceValue
                |  "print" "(" real_arg_list ")" ]

sentenceValue =   condition

arg_list =  ident { "," ident}

real_arg_list = sentenceValue {"," sentenceValue }


condition = condition_or [ "?" sentenceValue ":" sentenceValue ]
condition_or  = condition_and { "||" condition_or }
condition_and = condition_not { condition_not "&&" condition_and}
condition_not = {"!"} condition_unit
condiiton_unit = ["odd"] expression
                        | expression ("<" | ">" | "<=" | ">=" | "=" | "!=") expression

expression =  level1 { ("<<"| ">>" | "&" | "|") level1 }
level1  = level2 { ( "+" | "-" ) level2 }
level2 = level3 { "*" | "/" | "/%" | "%" ) level3 }
level3 = level4 {"^" level4}
level4 = item {"!"}          (*  factorial *)
item =  number  |ident { "(" real_arg_list ")" }| "(" sentenceValue" )" | ("+" | "-" | "~" ) item
```
## syntax 
Writet down syntax, then convert left recursion to right recursion.
Namely we should change the following productions:
expr, level0, level, level3

We notice that
```scala
A -> Aa|b
```
equls to 
```scala
A -> bR
R -> nil | aR
```
so here are the  right-recursion productions 
```scala
expr   -> level1 interval1
interval1 -> nil | {&|'|'|>>|<<|} interval1

level1 -> level2 interval2
interval2 -> nli | {+|-} interval2

level2 -> level3 interval3
interval3 -> nil | {*|/|//|%} interval3

level3 -> level4 | level4 ^ level3

level4 -> item interval4 
interval4 -> nil |! interval4

item   -> NUM|E|PI|ln(expr)|(expr)| + item| - item| ~ item
```

When implementing the parser, we can use a loop structure to implement the right recursion because it's tail-recursive.

For instance, we can simply find that the production for `level4` is 
```scala
level4 -> item | item ! | item!! |item !!! | ...
```
Though we can't write a production with infinite loops, we can write it in code like this: 
```python
match_level4():
    result = match(item)
    while if lookAhead  matches item:
        match(!)
        result = factorial(item)
    return result
```

# Instruction generation
We designed several instructions that can be generated for the target machine. 
To simplify this problem, we will emulate this virtual machine and execute instructions in python.
## register
This machine has three registers:
* `b` is the base register that contains the base pointer to locate a varible in the data stack
* `reg` is the return register that contains the  return value of latest function call 
* `pc` is the pc register that points to the instruction 
## stack
There are two stack in this virtual machine. 
One contains the instructions, visited by register `pc`. It won't change when executing instructions, so we can assume it's readonly
The other is data stack. It dynamiclly changes when running the program.

For each level, the first is the base address of this level. The second place is the static chain to visit the upper level's varibles. The third place contains the return address of the upper level.
And the other places in one level contains local varibles and real time data for calculation.
![](src/data_stack.jpg)

Each time we call a function, the level increases 1. Also, the level decreases 1 when we return from a function.


## instruction
Every instruction consists of three parts. The first is the name of the instruction. Generally, the second is the level diifference of a identifier(if it has). And the third part is the address.

name | levelDiff | address | explanation
:-:|:-:|:-:|:-:
INT|0|n|allocate n space for one level
INT|1|n|  rewind stk.top backward n steps
INT|2|n| print the top n elements of stack
LIT|-|constant value| push a constant value to the top of the data stack
LOD | levelDiff|addr | load a varible value to the top of the data stack. The var can be found use levelDiff and addr
STO|levelDiff|addr| store the stack top value to a varible, top decreases. 
CAL|levelDiff|addr|call a function
JMP |-|addr|jmp to addr, namely set addr to pc
JPC|-|addr| pop stack, if the value is not True, jmp addr
MOV|n1|n2|  stk[top-n2] = stk[top-n1]
OPR |-| RET| return to the upper level, use current level's first three value to change pc, data stack, base register.
OPR | -|POP| pop the data stack, store the value in `reg` register
OPR|-|PUSH| push `reg` to stack top
OPR|-|operator type| variout operation on value

# Design
We can generate instruction when analysing grammar. 
Some keypoints is the control structures' instruction traslation.
## if elif else
![](src/elseif_ins_stack.jpg)
## while/break
![](src/while_ins_stack.jpg)
`continue`, `for`  can be translated in the same way.
## function arguments pass
When analysing the function's defination, we can store the formal arguments as function's local varibles.
As soon as we call this function, we should calculate the real arguments in the level upper the function, and then pass value to the function's formal varibles one by one.

I use an instruction `MOV` to achive this goal. `MOV  addr1, addr2` will store value stk[top-n2] in stk[top-n1].
Let's have a look at how to call a function and pass args value.

Before we call a function, its real args will be calculated in the level upper this function. Note function level is n+1, and we call this function in level n.
In level n, we calculated function's args, all values are stored in the data stack of level n. Now call function and enter it. Data stack reaches level n+1 and grows three spaces for `DL`,`SL`,`RA`. The following space are for function's local varibles. So we can mov level n's real args value to these places according to function's argument num and varible num.

For example, function has n1 args, n2 local varibles(excluding args), then 
```python
for i in [0,1..,n1-1]:
    mov , n2+n1+3+i, n2 + i
```
The moment we returned level n, we should rewind top for n1 spaces, `OPR,n1,'BACK'` can make it.

![](src/argument_pass.jpg)

## function return
Also, mark function level as n+1, and outer(upper) is level n.
To implement `return` sentence, we just need to do two things:
* calculate `return` sentence value **in level n+1**
* pass this value to level n
It seems that it's hard to pass level n+1 's value to level n. Once we returned to level n, level n+1 's data in  data stack will be cleared.

I use a extra register `reg` to achive this. Before we return, 
* calculate return value
* `OPR ,0,'POP'`  will pop the value and store it in reg
* return level n
* `OPR,0,'PUSH'` will push reg value to stack top

Now the return value has be passed from level n+1 to level n

## instruction fillback
Taking `while` block as an example, Note that we don't know the `JPC` instruction's target addr until we finish analysing the whole block.The Solution is that after we analyse while condition, we generate an instruction with no target address, just take a place. We note down this instruction's address. As soon as we finish analysing the whole  `while` block, the instruction pointer, namely `ip`, pointing to the target address of `JPC`. Then we fill back the `JPC` instruction with the target address along to ip.

## symbol table
When analysing and translating, we want to get the symbol which including level, address,(value for constant) according to its name. The following shows how to achive it elegantly

There are three types of symbols:
* constant
* varible
* function name
Every function has an environment that contains this level's symbols, and an outer environment(except main function). Every environment has the three symbols mentioned above.

Defaultly, we are in the main function in the beginning of this program.

In an enviroment, when we meet a symbol, we should seek it in current environment. If not found, go for the outer environment recursively until we found it.

It gurantees that every environment has no same names for different symbols but may have same names in different environment.

So there won't be conflits when different functions have same local varibles or arguments.

I create class `closure` to describe this kind of environment and varible `curClosure` to  mark down current environment. Every time when calling a function, we enter a more inner environment. We do the following things to make sure that environment changes creately.
```python
saved = curClosure
curClosure = function.closure
call function
curClosure = saved
```
# To do
- [ ] array
- [ ] different value pass
- [ ] do while, switch
- [ ] function pass
- [ ] type 
