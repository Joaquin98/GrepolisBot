from queue import PriorityQueue
from datetime import datetime
import time

# PriorityQueue:
# .put() Agrega un nuevo elemento.
# .get() Retorna el menor elemento.
# .empty() Es vacia?

class ActionsQueue:
    def __init__(self):
        self.aQueue = PriorityQueue()
    def add_action(self,date,action,city):
        self.aQueue.put((date,action,city))
    def get_action(self):
        return self.aQueue.get()
    def empty(self):
        return self.aQueue.empty()
