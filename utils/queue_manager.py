from collections import deque

class QueueManager:
    def __init__(self):
        self.queue = deque()
        self.current = None

    def add(self, item):
        """Add an item to the queue"""
        self.queue.append(item)

    def get_next(self):
        """Get the next item from the queue"""
        if not self.is_empty():
            self.current = self.queue.popleft()
            return self.current
        return None

    def clear(self):
        """Clear the queue"""
        self.queue.clear()
        self.current = None

    def is_empty(self):
        """Check if the queue is empty"""
        return len(self.queue) == 0

    def get_queue(self):
        """Get the current queue as a list"""
        return list(self.queue)
