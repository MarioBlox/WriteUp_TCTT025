import random
from libnum import s2n
def print_triangle(n: int):
    for i in range(1, n + 1):
        print("*" * i)

def print_square(n: int):
    for _ in range(n):
        print("*" * n)

def print_circle(r: int):
    for y in range(-r, r + 1):
        line = ""
        for x in range(-r, r + 1):
            if x * x + y * y <= r * r:
                line += "*"
            else:
                line += " "
        print(line)

flag=b'hidden_msg'

N=s2n(flag)


oct_N=oct(N)
l=list(str(oct_N)[2:])
for i in range(len(l)):
    n=int(l[i])
    
    if n==0:
        print('#0#')
        
    else: 
        c=random.randrange(1, 4)
        if c == 1:
            print_triangle(n)
        elif c == 2:
            print_square(n)
        else:
            print_circle(n)
