from threading import Thread, Event
from time import sleep


counter = 1


def task1(args):
    print('Starting task 1' + args)

def main():

    global counter
    x = Thread(target=task1, args=('test',))
    print('Initiating main thread')    

    while True:

        print(f'Counter value {counter}')

        if counter % 5 == 0 :
            print('Starting a thread')            
            x.run()
            
        if not x.is_alive():
            x = Thread(target=task1, args=('test',))
            print(f'The thread is not alive')

        counter += 1
        sleep(1)


if __name__ == '__main__':    
    traffic_light = {
        'red': { 'pin': 0, 'status': 0 },
        'yellow': { 'pin': 0, 'status': 0 },
        'green': { 'pin': 0, 'status': 0 }
    }

    print(traffic_light['red']['pin'])
    # main()

