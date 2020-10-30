class Stack:
    def __init__(self):
        self.items = []

    def isEmpty(self):
        return self.items == []

    def push(self, item):
        self.items.append(item)
        
    def pop(self):
        return self.items.pop()

    def top(self):
        return self.items[len(self.items)-1]

    def getSize(self):
        return len(self.items)

    def add(self, entities):
    	pass

    def entities(self):
    	return self.items

    def removeAll(self):
    	self.items = []