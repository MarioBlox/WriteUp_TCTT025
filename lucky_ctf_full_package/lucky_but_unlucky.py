import random
import time
random.seed(time.time())

def run(lucky):
    try:
        x = str(random.getrandbits(32))
        a = input('Enter Your Name: ').replace('lucky' + x, '')
        if a != 'lucky' + x:
            return 'Exit #' + x
        b = input('Enter Number #1: ').translate(str.maketrans('0123456789', '#' * 10))
        c = input('Enter Number #2: ').translate(str.maketrans('0123456789', '#' * 10))
        if not b.isdigit() or not c.isdigit():
            return 'Exit #' + str(random.getrandbits(32))
        d = int(b) + lucky
        e = int(c) + lucky
        if d == e:
            return 'Exit #' + str(random.getrandbits(32))
        f = float(b) - lucky
        g = float(c) - lucky
        if f != g:
            return 'Exit #' + str(random.getrandbits(32))
        h = int(b)
        i = lucky + 1
        if h == i:
            return 'Exit #' + str(random.getrandbits(32))
        j = hash(h)
        k = hash(i)
        if j != k:
            return 'Exit #' + str(random.getrandbits(32))
        #-----------------------
        return 'flag{xxx}'
        #-----------------------
    except:
        return 'Exit #' + str(random.getrandbits(32))

if __name__ == "__main__":
    count = 0
    while True:
        count += 1
        if count > 313:
            break
        lucky = random.getrandbits(32)
        answer = run(lucky % 10000)
        print(answer)
        if 'flag' in answer:
            break
        else:
            print('Lucky #' + str(lucky))
