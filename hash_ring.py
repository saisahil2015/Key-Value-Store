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
    for hash, node in hr.get_points():
        print(hash, node)
    print('------------------')

    print(hr.get_replicas('asdf'))

    # my_nodes = l[i:i+2]
    # for hash, node in my_nodes:
    #     print(hash, node)
    # print('------------------')
    # print(hr.get_server('a'))


    # hr.add_node('asdf', {'port': 8081, 'vnodes': 4})
    # l = hr.get_points()
    # for hash, node in l:
    #     print(hash, node)