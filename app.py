import multiprocessing
import os
#from GatewayManager import gatcontroller
#from WebAppManager import wappcontroller

def fun1():
    os.system('python GatewayManager\\gatcontroller.py')

def fun2():
    os.system('python WebAppManager\\wappcontroller.py')

if __name__ == '__main__':
    p1 = multiprocessing.Process(name='p1', target=fun1)
    p2 = multiprocessing.Process(name='p2', target=fun2)
    p1.start()
    p2.start()

    #print("pre init")
    #p1 = multiprocessing.Process(name='p1', target=wappcontroller.main)
    #print("middle")
    #p2 = multiprocessing.Process(name='p2', target=gatcontroller.main)
    #print("end")
    #p1.start()
    #print("ok1")
    #p2.start()
    #print("ok2")
