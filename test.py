from dataclasses import dataclass, field

@dataclass
class A:
    a: int
    b: int = 3


@dataclass
class B:
    b: A = field(default_factory=lambda: A(2))


one = B()
one.b.a = 3
one.b.b = 4

two = B()
print(two.b.a)
print(two.b.b)
