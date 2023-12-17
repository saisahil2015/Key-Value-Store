from collections import defaultdict
from uhashring import HashRing as UHashRing

class HashRing(UHashRing):
    def __init__(self, nodes=[], **kwargs):
        super().__init__(nodes, **kwargs)

    def get_replicas(self, node_name, n):
        nodes = self.get_points() # [(hash, node), ...]
        total_nodes = len(nodes)
        next_n_nodes = set()

        for i, pos in enumerate(nodes):
            _hash, node = pos
            if node == node_name:
                next_i = i
                collected = 0
                while collected < n:
                    next_i = (next_i + 1) % total_nodes
                    if nodes[next_i][1] != node_name:
                        next_n_nodes.add(nodes[next_i][1])
                        collected += 1

        next_n_nodes_dict = []
        for node in next_n_nodes:
            next_n_nodes_dict.append(self._nodes[node])

        return next_n_nodes_dict
                

if __name__ == "__main__":
    kv_store = defaultdict(dict)

    vnode_factor = 5
    replica_factor = 2 # this should be less than number of nodes at initialization

    nodes = {
        "hopeful_joliot": {
            "port": 8080,
            "vnodes": vnode_factor,
        },
        "practical_jennings": {
            "port": 8081,
            "vnodes": vnode_factor,
        },
        "objective_minsky": {
            "port": 8082,
            "vnodes": vnode_factor,
        },
        "agitated_bassi": {
            "port": 8083,
            "vnodes": vnode_factor,
        },
        "boring_morse": {
            "port": 8084,
            "vnodes": vnode_factor,
        },
    }

    ring = HashRing(nodes, hash_fn='ketama', replicas=replica_factor)
    # for node in ring.get_replicas("hopeful_joliot", replica_factor - 1):
    #     print(node)

    for node, obj in ring._nodes.items():
        print(node, obj)

    # for i, point in enumerate(ring.get_points()):
    #     h, node = point
    #     print(f"{i}: {h} {node}")
    # print()

    # key = "key-asd"
    # pos, name = ring.get_node_pos(key), ring.get_node(key)
    # print(pos, name)

    # for node in ring.range(key, replica_factor): # includes primary
    #     print(node)

    # for node in ring.get_replicas(name, replica_factor - 1):
    #     print(node)

    # for node in ring.get_next_n_nodes("hopeful_joliot", 1):
    #     print(node)

    # ring.remove_node("practical_jennings")
    # ring.print_continuum()

    # ring.add_node("practical_jennings", {"port": 8081, "vnodes": vnode_factor})
    # ring.print_continuum()

    # for i in range(10):
    #     key = f"key-{i}"
    #     value = f"value-{i}"

    #     written_primary = False
    #     for node in ring.range(key, replica_factor):
    #         name = node["nodename"]
    #         if not written_primary:
    #             kv_store[name]['primary'] = [(key, value)] if 'primary' not in kv_store[name] else kv_store[name]['primary'] + [(key, value)]
    #             written_primary = True
    #         else:
    #             kv_store[name]['replica'] = [(key, value)] if 'replica' not in kv_store[name] else kv_store[name]['replica'] + [(key, value)]

    # for name, kv in kv_store.items():
    #     print(name)
    #     if "primary" not in kv:
    #         print("\tprimary: None")
    #     else:
    #         print("\tprimary: ", end=" ")
    #         for k, v in kv['primary']:
    #             print(f"{k}", end=" ")
    #         print()

    #     if "replica" not in kv:
    #         print("\treplica: None")
    #     else:
    #         print("\treplica: ", end=" ")
    #         for k, v in kv['replica']:
    #             print(f"{k}", end=" ")
    #         print()
    
    # name_to_remove = "practical_jennings"

    # kvs_tmp = kv_store[name_to_remove]
    # for mode, kvs in kvs_tmp.items():
    #     print(mode)
    #     for k, v in kvs:
    #         print(f"{k}", end=" ")
    #     print()

    # # remove node 
    # ring.remove_node(name_to_remove)
    # del kv_store[name_to_remove]

    # # add node back
    # ring.add_node(name_to_remove, {"port": 8081, "vnodes": vnode_factor})

    # # redistribute keys
    # all_kvs = []
    # for node_info in ring.get_replicas(name_to_remove, replica_factor - 1):
    #     node_name = node_info["nodename"]
    #     all_kvs.append(kv_store[node_name]["replica"] if "replica" in kv_store[node_name] else [])

    # for kvs in all_kvs:
    #     for k, v in kvs:
    #         written_primary = False
    #         for node in ring.range(k, replica_factor):
    #             name = node["nodename"]
    #             if not written_primary:
    #                 kv_store[name]["primary"] = [(k, v)] if "primary" not in kv_store[name] else kv_store[name]["primary"] + [(k, v)]
    #                 written_primary = True
    #             else:
    #                 kv_store[name]["replica"] = [(k, v)] if "replica" not in kv_store[name] else kv_store[name]["replica"] + [(k, v)]

    # for name, kv in kv_store.items():
    #     print(name)
    #     if "primary" not in kv:
    #         print("\tprimary: None")
    #     else:
    #         print("\tprimary: ", end=" ")
    #         for k, v in kv['primary']:
    #             print(f"{k}", end=" ")
    #         print()

    #     if "replica" not in kv:
    #         print("\treplica: None")
    #     else:
    #         print("\treplica: ", end=" ")
    #         for k, v in kv['replica']:
    #             print(f"{k}", end=" ")
    #         print()
    