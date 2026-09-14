####Multiprocessing with Thread pool Executor

from concurrent.futures import ProcessPoolExecutor
import  time

def print_numbers(number):
    time.sleep(2)
    return f"number :{number*number}"

numbers=[1,2,3,4,5]
if __name__=="__main__":
    with ProcessPoolExecutor(max_workers=3) as executor:
        results=executor.map(print_numbers,numbers)

    for result in results:
        print(result)