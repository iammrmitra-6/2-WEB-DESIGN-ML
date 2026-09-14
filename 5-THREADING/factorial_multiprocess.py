import multiprocessing,math,sys,time

##Increase the maximum number of digits for integer conversion

sys.set_int_max_str_digits(10000)

#### function to compute factorial of a given number 

def computer_factorial(number):
    print(f"computing factorial pf {number}")
    result=math.factorial(number)
    print(f"Factorial of {number} is {result}")
    return result

if __name__=="__main__":
    numbers=[5,6,7,8]
    
    start_time=time.time()

    with multiprocessing.Pool() as pool:
        results=pool.map(computer_factorial,numbers)
    
    end_time=time.time()

    print(f"result:{results}")
    print(f"Time taken: {end_time-start_time} seconds")
