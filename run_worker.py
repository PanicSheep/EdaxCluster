import datetime
import multiprocessing
import subprocess
import threading
import time
import edax
from core import Position
from workspread import TaskDispatchClient


def countdown(seconds):
    for i in range(seconds, 0, -1):
        print(f'Starting worker in {i} ...')
        time.sleep(1)


def log(text: str = ''):
    now = datetime.datetime.now()
    print(f'[{now}] {text}')


def work(ip):
    client = TaskDispatchClient(ip)

    while True:
        log(f'Requesting task')
        task = client.request_task()
        if task is None:
            log('Received no task')
            break
        log(f'Received task: {task}')

        index, (pos, depth) = task

        pos = Position.from_string(pos)
        depth = int(depth)

        #engine = edax.Engine('../edax-reversi/bin/lEdax-x64-modern', depth)
        engine = edax.Engine(r'G:\edax-ms-windows\edax-4.4', depth)

        line = engine.solve(pos)[0]

        result = f'{line.depth} {line.confidence} {line.score} {line.time} {line.nodes}'
        client.report_result((index, result))
        log(f'Sent result: {result}')


if __name__ == '__main__':
    #ip = sys.argv[1]
    ip = 'ec2-54-157-188-48.compute-1.amazonaws.com'
    ip = 'localhost'

    countdown(1)

    threads = []
    for _ in range(multiprocessing.cpu_count()):
        threads.append(threading.Thread(target=work, args=(ip,)))

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    #subprocess.run(['shutdown', 'now'])