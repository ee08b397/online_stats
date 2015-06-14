from collections import deque

class Node(object):
    def __init__(self, name):
        self.name = name
        self.children = [] 

    def add_child(self, child):
        self.children.append(child)

    def __repr__(self):
        return '<{0}>'.format(self.name)

"""
Fully connected, directed tree.
0___
|   |
1   2___
    |   |
    3   4
        |
        5
"""
graph = []
for name in xrange(6):
    graph.append(Node(name))

graph[0].add_child(graph[1])
graph[0].add_child(graph[2])
graph[2].add_child(graph[3])
graph[2].add_child(graph[4])
graph[4].add_child(graph[5])

def get_descendants(node):
    unexplored = deque([node])
    while unexplored:
        node = unexplored.popleft()
        yield node
        children = node.children
        for child in children:
            unexplored.append(child)


