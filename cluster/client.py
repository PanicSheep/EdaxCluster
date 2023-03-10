import datetime
from typing import Iterable
from .protocols import *

def log(text: str) -> None:
    now = datetime.datetime.now()
    print(f'[{now}] {text}')

class TaskDispatchClient:

    def __init__(self, ip) -> None:
        transporter = Connector().connect(ip, port = 12350)
        self.tdp = TaskDispatchProtocol(PascalMethod(), StatefulSession(transporter))

    def request_task(self) -> str:
        try:
            self.tdp.request()
            msg = self.tdp.receive(blocking = True)
        except:
            return None
        
        if msg.type == Message.Type.respond:
            return msg.content
        elif msg.type == Message.Type.deny:
            return None

    def report_result(self, result: str) -> None:
        self.tdp.report(result)

    def report_fail(self) -> None:
        self.tdp.report_fail()

    def dispatch(self, tasks, on_report = lambda *args: None) -> list:
        if not isinstance(tasks, Iterable):
            tasks = [tasks]

        tasks = [(i, t) for i, t in enumerate(tasks)]
        results = [None] * len(tasks)

        self.tdp.dispatch(tasks)

        while any(r is None for r in results):
            msg = self.tdp.receive(blocking = True)

            if msg.type == Message.Type.report:
                i, r = msg.content
                on_report(i, r)
                results[i] = r
            else:
                raise RuntimeError('Unexpected message type')

        return results
