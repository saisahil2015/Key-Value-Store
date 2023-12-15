from uhashring import HashRing as UHashRing

class HashRing(UHashRing):
    def __init__(self, nodes=[], **kwargs):
        super().__init__(nodes, **kwargs)

    def get_next_n_nodes(self, node_name, n):
        l = self.get_points()
        total_nodes = len(l)
        for i, pos in enumerate(l):
            _hash, node = pos
            if node == node_name:
                next_n_nodes = set()
                next_i = i
                while len(next_n_nodes) < n:
                    next_i = (next_i + 1) % total_nodes                    
                    if l[next_i][1] != node_name:
                        next_n_nodes.add(l[next_i][1])

        next_n_nodes_dict = []
        for node in next_n_nodes:
            next_n_nodes_dict.append(self._nodes[node])
        return next_n_nodes_dict