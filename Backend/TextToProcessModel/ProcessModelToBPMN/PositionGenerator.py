import networkx as nx


class Position:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __str__(self):
        return f'({self.x}, {self.y})'

    def __repr__(self):
        return f'({self.x}, {self.y})'


def get_position_dict(edges: [(str, str)], end: str, start: str) -> dict:
    position_dict = dict()

    paths = get_paths(edges, end, start)

    nodes = set()
    for edge in edges:
        nodes.add(edge[0])
        nodes.add(edge[1])

    following_dict = dict()
    inc_dict = dict()
    out_dict = dict()
    layer_dict = dict()
    follows_dict = dict()
    space_needed_dict = dict()

    for node in nodes:
        following_dict[node] = set()
        inc_dict[node] = 0
        out_dict[node] = 0
        layer_dict[node] = 0
        follows_dict[node] = set()

    for edge in edges:
        inc_dict[edge[1]] += 1
        out_dict[edge[0]] += 1
        follows_dict[edge[0]].add(edge[1])

    for path in paths:
        for i in range(len(path)):
            for j in range(len(path) - i - 1):
                following_dict[path[i]].add(path[j + 1 + i])

    print(paths)
    print(following_dict)
    print(inc_dict)
    print(out_dict)

    for path in paths:
        deepness_list = []
        deepness = 1
        for i in range(len(path)):
            node = path[i]

            if i == 0:
                deepness -= 1

            if inc_dict[node] > 1:
                deepness -= 1

            deepness_list.append(deepness)
            layer_dict[node] = deepness
            if out_dict[node] > 1:
                deepness += 1

        print(deepness_list)

    layer_dict = dict(sorted(layer_dict.items(), key=lambda item: item[1], reverse=True))

    DG = nx.DiGraph(edges)
    topology = list(nx.topological_sort(DG))
    rev_topology = list(reversed(topology))

    layer_x_nodes = []
    layer = 0
    setup_done = False
    for node in layer_dict.keys():

        if not setup_done:
            layer = layer_dict[node]
            setup_done = True

        if layer_dict[node] == layer:
            layer_x_nodes.append(node)
        else:
            for m in rev_topology:
                if m in layer_x_nodes:
                    candidates = [m]
                    while len(candidates) > 0:
                        n = candidates[0]
                        if layer_dict[n] == layer_dict[m]:
                            if space_needed_dict[n] > space_needed_dict[m]:
                                space_needed_dict[m] = space_needed_dict[n]
                        for next_node in follows_dict[n]:
                            if layer_dict[next_node] >= layer_dict[m]:
                                candidates.append(next_node)
                        candidates.remove(n)
            layer = layer_dict[node]
            layer_x_nodes = [node]

        if out_dict[node] > 1:
            space_needed_dict[node] = out_dict[node] - 1
            for f_node in follows_dict[node]:
                space_needed_dict[node] += space_needed_dict[f_node]
        if out_dict[node] <= 1:
            space_needed_dict[node] = 1

    for m in rev_topology:
        if m in layer_x_nodes:
            candidates = [m]
            while len(candidates) > 0:
                n = candidates[0]
                if layer_dict[n] == layer_dict[m]:
                    if space_needed_dict[n] > space_needed_dict[m]:
                        space_needed_dict[m] = space_needed_dict[n]
                for next_node in follows_dict[n]:
                    if layer_dict[next_node] >= layer_dict[m]:
                        candidates.append(next_node)
                candidates.remove(n)

    print(layer_dict)

    print(follows_dict)

    space_needed_dict = dict(sorted(space_needed_dict.items(), key=lambda item: item[1], reverse=True))

    print('Space needed dict:')
    print(space_needed_dict)

    position_dict[start] = Position(200, space_needed_dict[start] * 100 / 2)
    for node in topology:
        space = out_dict[node] - 1
        spacer = []
        for f_node in follows_dict[node]:
            space += space_needed_dict[f_node]
            spacer.append(space_needed_dict[f_node])
        i = 0
        x = position_dict[node].x
        y = position_dict[node].y
        if out_dict[node] == 1:
            for f_node in follows_dict[node]:
                position_dict[f_node] = Position(x + 150, y)
        elif divmod(len(spacer), 2)[1] == 0:
            for f_node in follows_dict[node]:
                j = int(len(spacer) / 2)
                print(f'Node:{f_node}')
                print(sum(spacer[:j]))
                print((out_dict[node] / 2))
                x_new = x + 150
                y_new = y + 100 * (i - sum(spacer[:j]) - (out_dict[node] / 2))
                position_dict[f_node] = Position(x_new, y_new)
                i += 1 + space_needed_dict[f_node]
        else:
            for f_node in follows_dict[node]:
                j = int(len(spacer) / 2)
                x_new = x + 150
                print(f'Node:{f_node}')
                print(sum(spacer[:j]))
                print(((spacer[int(j + 0.5)] - 1) / 2))
                print(((out_dict[node] - 1) / 2))
                y_new = y + 100 * (
                            i - sum(spacer[:j]) - ((spacer[int(j + 0.5)] - 1) / 2) - ((out_dict[node] - 1) / 2))
                position_dict[f_node] = Position(x_new, y_new)
                i += 1 + space_needed_dict[f_node]

    # while out_dict[f_node] > 1 or in:


    # position_dict[start] = Position(160, 80)
    # candidates = [start]
    # while len(candidates) != 0:
    #     candidate = candidates[0]
    #     x = position_dict[candidate].x
    #     y = position_dict[candidate].y
    #     offset = 0
    #     for node in follows_dict[candidate]:
    #         candidates.append(node)
    #         position_dict[node] = Position(x + 150, y + offset)
    #         offset += 100
    #     candidates.remove(candidate)

    return position_dict


def get_paths(edges: [(str, str)], end: str, start: str):
    return get_paths_util(edges, end, start, [], [], [])


def get_paths_util(edges: [(str, str)], end: str, start: str, visited: [str], path: [str], paths: [[str]]):
    visited.append(start)
    path.append(start)
    if start == end:
        paths.append(path)
    else:
        for edge in edges:
            if edge[0] == start:
                if edge[1] not in visited:
                    paths = get_paths_util(edges, end, edge[1], visited.copy(), path.copy(), paths.copy())
    return paths


# edges = [('0', '1'), ('1', '2'), ('1', '6'), ('2', '3'), ('2', '4'), ('3', '5'), ('4', '5'), ('5', '8'), ('6', '7'),
#          ('8', '9'), ('8', 'a'), ('9', 'b'), ('a', 'b'), ('b', '7'),
#          ('7', 'g'), ('g', 'v'), ('g', 'w'), ('g', 'x'), ('g', 'y'), ('g', 'z'), ('v', '10'), ('w', '10'), ('x', '10'),
#          ('y', '10'), ('z', '10'), ]
# end = '10'
# start = '0'
#
# print(get_position_dict(edges, end, start))
