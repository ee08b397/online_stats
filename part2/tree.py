from collections import defaultdict
from collections import deque


class Edge(object):
    def __init__(self, parent, child, created_at):
        self.parent = parent
        self.child = child
        self.created_at = created_at
        self.generation = 0

class Tree(object):

    def __init__(self):
        self.name = 'MyTree'
        self.parent_to_child = defaultdict(list) 
        self.child_to_parent = {} 

    def would_be_leaf(self, edge):
        if edge.child in self.parent_to_child:
            return False
        return True

    def is_earliest_parent(self, edge):
        if edge.child not in self.child_to_parent:
            return True
        existing_edge = self.child_to_parent[edge.child]
        if existing_edge.created_at < edge.created_at:
            return False
        return True

    def should_add(self, edge):
        is_leaf = self.would_be_leaf(edge)
        is_earliest = self.is_earliest_parent(edge)
        return all([
            self.would_be_leaf(edge), 
            self.is_earliest_parent(edge)])

    def is_root(self, edge):
        return edge.parent not in self.child_to_parent and edge.parent in self.parent_to_child 

    def get_roots(self):
        roots = []
        for parent, children in self.parent_to_child.items():
            for edge in children:
                if self.is_root(edge):
                    roots.append(edge.parent)
        return roots

    def get_depth(self, root):
        depth = 0
        current_generation = deque([root])
        next_generation = True
        while next_generation:
            next_generation = deque()
            while current_generation:
                node = current_generation.popleft()
                child_edges = self.parent_to_child[node]
                for edge in child_edges:
                    next_generation.append(edge.child)
            depth += 1
            current_generation = next_generation
        return depth

    def get_generation(self, edge):
        if edge.parent in self.child_to_parent:
            ancestor = self.child_to_parent[edge.parent]
            return ancestor.generation + 1
        return 0 

    def add(self, edge):
        self.parent_to_child[edge.parent].append(edge)
        self.child_to_parent[edge.child] = edge
        edge.generation = self.get_generation(edge)

    def get_edgelist(self):
        for parent, edge in self.parent_to_child.items():
            yield edge.parent, edge.child
