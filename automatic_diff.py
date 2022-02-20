from __future__ import annotations
from typing import Callable,Tuple,List,cast,Union
import copy
import math

from typing_extensions import Protocol

class FloatFunction(Protocol):
    def __call__(self, *vals: float) -> float: ...
    
def getsign(negative: bool) -> float:
    return -1. if negative else 1.

class Variable:
    def __init__(self,identif: str,negative: bool = False):
        self.identif  = identif
        self.negative = negative
        
    def __neg__(self) -> Variable:
        newobj = copy.copy(self)
        newobj.negative = not self.negative
        return newobj
    
    def __call__(self,**kwargs: float) -> Variable | float:
        for k,v in kwargs.items():
            if k == self.identif:
                return getsign(self.negative)*v
        return self
    
    def __repr__(self) -> str:
        return ("-" if self.negative else "")+self.identif


class Expr:
    def __init__(self,name: str,func: FloatFunction,arguments: List[Expr | Variable | float]):
        self.name      = name
        self.func      = func
        self.arguments = arguments
        self.negative  = False
        
    def __neg__(self) -> Expr:
        newobj = copy.copy(self)
        newobj.negative = not self.negative
        return newobj
    
    def __repr__(self) -> str:
        ret = "-" if self.negative else ""
        ret+= self.name
        ret+="({})".format(",".join(map(str,self.arguments)))
        return ret
        
    def __call__(self,**kwargs: float) -> Expr | float:
        all_evaled = True
        newargs: List[Expr | Variable | float] = []
        for arg in self.arguments:
            if type(arg) == float:
                newargs.append(arg)
                continue
            newarg = cast(Union[Expr,Variable],arg).__call__(**kwargs) #make it explicit so its more obvious when reading...
            newargs.append(newarg)
            all_evaled = all_evaled and (type(newarg) == float)
                
        if all_evaled:
            casted_newargs = tuple(cast(List[float],newargs))
            return getsign(self.negative)*self.func(*casted_newargs)
        
        return Expr(self.name,self.func,newargs)


class InfixExpr(Expr):            
    def __repr__(self) -> str:
        ret = "-" if self.negative else ""
        tostr = lambda x: "("+str(x)+")" if isinstance(x,InfixExpr) else str(x)
        joined = self.name.join(map(tostr,self.arguments))
        ret+="{}{}{}".format("(" if self.negative else "",joined,")" if self.negative else "")
        #SPEED: do this in a single loop
        #Second character can only be negative. The two cases are when self.name (the first character) is + or -
        ret = ret.replace("+-","-")
        ret = ret.replace("--","+")
        return ret
    
def Sin(arg: Expr | Variable | float) -> Expr:
    def f(*args: float) -> float:
        return math.sin(args[0])
    return Expr("Sin",f,[arg])

def Plus(*args: Expr | Variable | float) -> InfixExpr:
    def f(*args: float):
        ret = 0.
        for a in args:
            ret += a
        return ret
    return InfixExpr("+",f,list(args))

def Minus(*args: Expr | Variable | float) -> InfixExpr:
    def f(*args: float):
        ret = 0.
        for a in args:
            ret -= a
        return ret
    return InfixExpr("-",f,list(args))

def Multiply(*args: Expr | Variable | float) -> InfixExpr:
    def f(*args: float):
        ret = 1.
        for a in args:
            ret *= a
        return ret
    return InfixExpr("*",f,list(args))

def Divide(*args: Expr | Variable | float) -> InfixExpr:
    def f(*args: float):
        if len(args) == 0:
            raise Exception("Can't divide no arguments")
        ret = args[0]
        for a in args[1:]:
            ret /= a
        return ret
    return InfixExpr("/",f,list(args))

def main() -> None:
    x = Variable("x")
    print(x)
    print((-x))
    print(x(x=1.2))
    print((-x)(x=1.2))
    sin_constant = Sin(-1.2)
    print(sin_constant)
    print(-sin_constant)
    plus_test = Plus(Sin(Variable("x")),-1.)
    print(plus_test(x=math.pi))
    print(plus_test)
    print(Divide(1.,2.,3.))
    print(Divide(1.,2.,3.)())
    plus_test_vars = Plus(Variable("x"),Variable("y"),Variable("z"))
    print(plus_test_vars)
    print(-plus_test_vars)
    print(plus_test_vars(x=0.,y=1.,z=2.))#Type hinting doesn't catch the string with **kwargs: float, for some reason
    

if __name__=="__main__":
    main()
