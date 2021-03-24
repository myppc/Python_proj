
n = 0.3
c = 2

def func(x):
    return x**c 

def der_func(x):
    return c * x**(c - 1)

def na_value(x):
    return x - n*der_func(x)

def main():
    x = 100
    v_min =  func(x)
    for i in range(10):
        cur_v = func(x)
        x = na_value(x)
        if cur_v < v_min:
            v_min = cur_v
        print("----> " ,i ," cur  = ",cur_v," x = ",x," v_min = " ,v_min )


main()