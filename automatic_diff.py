from __future__ import annotations
from typing import Callable,Tuple,List,cast,Union
import copy
import math
from dual_numbers import Dual

from typing_extensions import Protocol

class Function(Protocol):
    def __call__(self, *vals: Dual) -> Dual: ...
    
def getsign(negative: bool) -> float:
    return -1. if negative else 1.

def floatToDual(arg: float | Dual) -> Dual:
    return Dual(arg) if type(arg) == float else cast(Dual,arg)

def clearFloat(arg: Expr | Variable | Dual | float) -> Expr | Variable | Dual:
    if type(arg) == float:
        return Dual(arg)
    return cast(Union[Expr,Variable,Dual],arg)

def clearFloats(*args: Expr | Variable | Dual | float) -> List[Expr | Variable | Dual]:
    return list(map(clearFloat,args))

class Variable:
    def __init__(self,identif: str,negative: bool = False):
        self.identif  = identif
        self.negative = negative
        
    def __neg__(self) -> Variable:
        newobj = copy.copy(self)
        newobj.negative = not self.negative
        return newobj
    
    def __call__(self,**kwargs: Dual | float) -> Variable | Dual:
        for k,v in kwargs.items():
            if k == self.identif:
                return floatToDual(v).scale(getsign(self.negative))
        return self
    
    def __repr__(self) -> str:
        return ("-" if self.negative else "")+self.identif

class Expr:
    def __init__(self,name: str,func: Function,arguments: List[Expr | Variable | Dual]):
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
    def __call__(self,**kwargs: Dual | float) -> Expr | Dual:
        all_evaled = True
        newargs: List[Expr | Variable | Dual] = []
        for arg in self.arguments:
            aux = clearFloat(arg)
            if type(aux) == Dual:
                newargs.append(aux)
                continue
            newarg = cast(Union[Expr,Variable],aux).__call__(**kwargs) #make it explicit so its more obvious when reading...
            newargs.append(newarg)
            all_evaled = all_evaled and (type(newarg) == Dual)
                
        if all_evaled:
            casted_newargs = tuple(cast(List[Dual],newargs))
            return self.func(*casted_newargs).scale(getsign(self.negative))
        
        return Expr(self.name,self.func,newargs)


class InfixExpr(Expr):            
    def __repr__(self) -> str:
        ret = "-" if self.negative else ""
        tostr = lambda x: "("+str(x)+")" if (isinstance(x,InfixExpr) or isinstance(x,Dual)) else str(x)
        joined = self.name.join(map(tostr,self.arguments))
        ret+="{}{}{}".format("(" if self.negative else "",joined,")" if self.negative else "")
        #SPEED: do this in a single loop
        #Second character can only be negative. The two cases are when self.name (the first character) is + or -
        ret = ret.replace("+-","-")
        ret = ret.replace("--","+")
        return ret
        
def Sin(arg: Expr | Variable | Dual | float) -> Expr:
    def f(*args: Dual) -> Dual:
        x = Dual(args[0].real % (math.pi*2),args[0].eps % (math.pi*2))
        x_squared = x*x
        result    = x
        accum_mul = x
        sign = -1.
        for i in range(3,24,2):
            accum_mul = accum_mul*x_squared
            result   += accum_mul.scale(sign/math.factorial(i))
            sign     *= -1.
        return result
    return Expr("Sin",f,clearFloats(arg))

def Plus(*args: Expr | Variable | Dual | float) -> InfixExpr:
    def f(*args: Dual):
        ret = Dual(0.)
        for a in args:
            ret += a
        return ret
    return InfixExpr("+",f,clearFloats(*args))

def Minus(*args: Expr | Variable | Dual | float) -> InfixExpr:
    def f(*args: Dual):
        ret = Dual(0.)
        for a in args:
            ret -= a
        return ret
    return InfixExpr("-",f,clearFloats(*args))

def Multiply(*args: Expr | Variable | Dual | float) -> InfixExpr:
    def f(*args: Dual):
        ret = Dual(1.)
        for a in args:
            ret *= a
        return ret
    return InfixExpr("*",f,clearFloats(*args))

def Divide(*args: Expr | Variable | Dual | float) -> InfixExpr:
    def f(*args: Dual):
        if len(args) == 0:
            raise Exception("Can't divide no arguments")
        ret = args[0]
        for a in args[1:]:
            ret /= a
        return ret
    return InfixExpr("/",f,clearFloats(*args))

def main() -> None:
    print(Sin(-1.2),"=",Sin(-1.2)())
    print(Divide(1.,2.,3.),"=",Divide(1.,2.,3.)())
    
    plus_test_vars = Plus(Variable("x"),Variable("y"),Variable("z"))
    values = {"x": 0.,"y": 1.,"z": 2.}
    print(plus_test_vars,"(",values,")","=",plus_test_vars(**values))
    
    start   = 0.
    end     = 4*math.pi
    steps   = 100
    formula = Sin(Variable("x"))
    print("Testing",formula,"and its automatic derivative")
    format_width = 7
    rjust  = lambda s: s.rjust(format_width,' ')
    print(*(rjust(s) for s in ["x","sin(x)","y","cos(x)","y'"]),sep='|')
    print(*("-"*format_width for i in range(5)),sep='|')

    for i in range(0,steps+1,1):
        x = (i/steps)*(end-start) + start
        dual_x = Dual(x,1.)
        dual_y = cast(Dual,formula(x=dual_x))
        print(*(rjust("{:.2f}".format(f)) for f in [x,math.sin(x),dual_y.real,math.cos(x),dual_y.eps]),sep='|')
    

if __name__=="__main__":
    main()
