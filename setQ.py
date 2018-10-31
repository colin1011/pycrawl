import queue

class SetQueue(queue.Queue):

    def _init(self, maxsize):
        self.maxsize = maxsize
        self.queue = set()

    def _put(self, item):
        self.queue.add(item)

    def _get(self):
        return self.queue.pop()


q=SetQueue([1,2,3,4,5,6,7,8,9,10])

print(q.queue)

