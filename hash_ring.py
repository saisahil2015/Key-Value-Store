from uhashring import HashRing

class MyHashRing(HashRing):
    def __init__(self, nodes, replicas_count=1):
        super().__init__(nodes)
        self.replicas_count = replicas_count

    def get_node_by_node_name(self, node_name):
        '''
            get the node by its name
        '''
        l = self.get_points()
        for _hash, node in l:
            if node == node_name:
                return node
        return None

    def get_node_by_index(self, index):
        '''
            get the node by its index
        '''
        l = self.get_points()
        return l[index][1]

    def get_next_n_nodes(self, node_name, n):
        '''
            get the next n nodes of a node
        '''
        l = self.get_points()
        total_nodes = len(l)
        for i, pos in enumerate(l):
            _hash, node = pos

            if node == node_name:
                next_n_nodes = []
                while len(next_n_nodes) < n:
                    i = (i + 1) % total_nodes
                    if l[i][1] != node_name and l[i][1] not in next_n_nodes:
                        next_n_nodes.append(l[i][1])
                return next_n_nodes

        return None

    def get_replicas(self, node_name):
        '''
            get the replicas of a node
        '''
        replicas = []
        l = self.get_points()
        total_nodes = len(l)
        for i, pos in enumerate(l):
            _hash, node = pos

            if node == node_name:
                replicas.append(node)
                while len(replicas) - 1 < self.replicas_count:
                    i = (i + 1) % total_nodes
                    if l[i][1] not in replicas:
                        replicas.append(l[i][1])
                break
        return replicas

    def get_all_virtual_nodes(self, node_name):
        '''
            get all virtual nodes
        '''
        virtual_nodes = []
        l = self.get_points()
        total_nodes = len(l)
        for i, pos in enumerate(l):
            _hash, node = pos

            if node == node_name:
                virtual_nodes.append(i)
        return None

    def get_next_node(self, node_name):
        '''
            get the next node of a node
        '''
        l = self.get_points()
        total_nodes = len(l)
        for i, pos in enumerate(l):
            _hash, node = pos

            if node == node_name:
                return l[(i + 1) % total_nodes][1]
        return None

    def print_all_nodes(self):
        '''
            print all nodes
        '''
        l = self.get_points()
        for _hash, node in l:
            print(_hash, node)
        print("=====================================")

if __name__ == "__main__":
    r = 2

    nodes = {
        'qwer': {
            'port': 8080,
            'vnodes': r,
        },
        'asdf': {
            'port': 8081,
            'vnodes': r,
        },
        'zxcv': {
            'port': 8082,
            'vnodes': r,
        }
    }

    hr = MyHashRing(nodes)
    hr.print_all_nodes()

    # add new node into the hash ring
    hr.add_node('uiop', {
        'port': 8083,
        'vnodes': r,
    })
    hr.print_all_nodes()

    # find all the next nodes of virtual nodes of the new node
    nodename = hr.get_node('a')
    print(nodename)
    next_nodes = hr.get_next_n_nodes(nodename, r)
    print(next_nodes)