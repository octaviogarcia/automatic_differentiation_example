from __future__ import annotations
from dataclasses import dataclass
import copy

@dataclass
class Dual:
    real: float
    eps: float = 0.
    def scale(self,f: float) -> Dual:
        return Dual(self.real*f,self.eps*f)
    def eq(self,other: Dual) -> bool:
        return (self.real == other.eps) and (self.eps == other.eps)
    def abs(self) -> Dual:
        return Dual(abs(self.real),abs(self.eps))
    def __abs__(self) -> Dual:
        return self.abs()
    def __neg__(self) -> Dual:
        return Dual(-self.real,-self.eps)
    def __add__(self,other: Dual) -> Dual:
        return Dual(self.real+other.real,self.eps+other.eps)
    def __sub__(self,other: Dual) -> Dual:
        return self+(-other)
    def __mul__(self,other: Dual) -> Dual:
        return Dual(self.real*other.real,self.real*other.eps+self.eps*other.real)
    def __truediv__(self,other: Dual) -> Dual:
        if other.real != 0.:
            return Dual(
                self.real/other.real,
                (self.eps*other.real-self.real*other.eps)/(other.real*other.real)
            )
        if self.real != 0.:
            raise ArithmeticError("Division not defined for divisor {}".format(other))
        raise ArithmeticError("Infinite solutions of the form {} + yε".format(self.eps/other.eps))
    def __pow__(self,p: int) -> Dual:
        ret = Dual(1.,0) #multiply identity 
        for i in range(p):
            ret *= self
        return ret
    def __repr__(self) -> str:
        return "{} + {}ε".format(self.real,self.eps)

def main() -> None:
    print(Dual(1.,1.)==Dual(1.,1.))
    print(Dual(1.,1.)!=Dual(-1.,1.))
    print(Dual(1.,1.)==abs(Dual(-1.,-1.)))
    print(Dual(1.,1.)==(-Dual(-1.,-1.)))
    print(Dual(2.,3.)*Dual(1.,1.) == Dual(2.,5.))
    print(Dual(2.,3.)*Dual(0.,1.) == Dual(0.,2.))
    print(Dual(2.,3.)*Dual(1.,0.) == Dual(2.,3))
    print(Dual(2.,3.)/Dual(1.,1.) == Dual(2.,1.))
    print(Dual(1.,1.)-Dual(1.,1.) == Dual(0.,0.))
    print(Dual(2.,3.)**4)
    

if __name__=="__main__":
    main()
