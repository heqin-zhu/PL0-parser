# C-parser
>A token\_scanner and declaration parser for simplified c using LL(1)
# Rules
* size of int or pointer is 1byte
# Grammar
```scala
translation_unit 
  : declaration 
  | translation_unit declaration 
      ; 
 
declaration 
  : declaration_specifiers init_declarator_list ';' 
      ; 
 
declaration_specifiers 
  : type_specifier 
  ; 
 
init_declarator_list 
  : init_declarator 
  | init_declarator_list ',' init_declarator 
  ; 
 
init_declarator 
  : declarator 
  ; 
 
type_specifier 
  : VOID 
  | INT 
  ; 
 
declarator 
  : pointer direct_declarator 
  | direct_declarator 
  ; 
 
direct_declarator 
  : IDENTIFIER 
  | '(' declarator ')' 
  | direct_declarator '[' CONSTANT_INT ']' 
  | direct_declarator '(' parameter_type_list ')' 
  | direct_declarator '(' ')' 
  ; 
 pointer 
  : '*' 
  | '*' pointer 
  ; 
 
parameter_type_list 
  : parameter_list 
      ; 
 
parameter_list 
  : parameter_declaration 
  | parameter_list ',' parameter_declaration 
  ; 
 
parameter_declaration 
  : declaration_specifiers declarator 
  ; 
```
# Examples
```c
>> int *p,q,j[2];
Varible   p, size: 1, type: pointer(INT)
Varible   q, size: 1, type: INT
Varible   j, size: 2, type: array(2,INT)

>> int *p[2][3];
Varible   p, size: 6, type: array(2,array(3,pointer(INT)))

>> int (*p[4])[2];
Varible   p, size: 4, type: array(4,pointer(array(2,INT)))

>> int (*f(int i,void *j))[2];
Parameter i, size: 1, type: INT
Parameter j, size: 1, type: pointer(VOID)
Function  f, return type: pointer(array(2,INT))

>> int f(void i, void j, int p[2]);
Parameter i, size: 1, type: VOID
Parameter j, size: 1, type: VOID
Parameter p, size: 2, type: array(2,INT)
Function  f, return type: INT

>> int *f(int i)[2];
Error: Array of Function can not be returned from functions

>> int f[2](int k);
Error: Array of Functions is not allowed
```
