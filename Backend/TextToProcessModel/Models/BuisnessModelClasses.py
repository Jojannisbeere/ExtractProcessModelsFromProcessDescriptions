from enum import Enum
import networkx as nx
import pylab as plt


class GatewayType(Enum):
    AND = 'and'
    OR = 'or'
    XOR = 'xor'

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


class Activity:

    class_counter = 1

    def __init__(self, activity_name: str = ''):
        self.activity_name = activity_name
        self.id = 'a' + str(Activity.class_counter)
        Activity.class_counter += 1

    def __str__(self):
        return '|<' + self.activity_name + '>|' + ' (' + self.id + ')'

    def __repr__(self):
        return '|<' + self.activity_name + '>|' + ' (' + self.id + ')'


class SwimLane:
    def __init__(self, actors: [str] = [], activities: [Activity] = [], sub_swim_lanes=[]):
        self.actors = actors
        self.activities = activities
        self.sub_swim_lanes = sub_swim_lanes

    def __str__(self):
        return 'SwimLane{' + str(self.actors) + ', ' + str(self.activities) + '}'

    def __repr__(self):
        return 'SwimLane{' + str(self.actors) + ', ' + str(self.activities) + '}'

    def add_actors_to_activity_names(self):
        actors_str = '-'.join(self.actors)
        for a in self.activities:
            a.activity_name = a.activity_name + ' (' + actors_str + ')'


class Gateway:

    class_counter = 1

    def __init__(self, gateway_type: GatewayType):
        self.gateway_type = gateway_type
        self.id = 'g' + str(Gateway.class_counter)
        Gateway.class_counter += 1

    def __str__(self):
        return '[' + str(self.gateway_type) + ']' + ' (' + self.id + ')'

    def __repr__(self):
        return '[' + str(self.gateway_type) + ']' + ' (' + self.id + ')'


class Transition:

    class_counter = 1

    def __init__(self, going_from: Activity or Gateway, going_to: Activity or Gateway):
        self.going_from = going_from
        self.going_to = going_to
        self.description = ''
        self.id = 't' + str(Transition.class_counter)
        Transition.class_counter += 1

    def __str__(self):
        return str(self.going_from) + '->' + str(self.going_to) + ' (' + self.id + ')'

    def __repr__(self):
        return str(self.going_from) + '->' + str(self.going_to) + ' (' + self.id + ')'


class ProcessModel:
    def __init__(self, swim_lanes: [SwimLane], gateways: [Gateway], transitions: [Transition]):
        self.swim_lanes = swim_lanes
        self.gateways = gateways
        self.transitions = transitions
        self.start_activity = Activity('Start process')
        self.end_activity = Activity('End process')

    def __repr__(self):
        return str([str(transition) for transition in self.transitions])

    def draw_as_graph(self):
        G = nx.DiGraph()
        for transition in self.transitions:
            G.add_edge(str(transition.going_from) + '[' + transition.going_from.id + ']',
                       str(transition.going_to) + '[' + transition.going_to.id + ']')
        pos = nx.planar_layout(G)
        plt.figure(1, figsize=(10, 6))
        nx.draw(G, pos, with_labels=True, font_size=8)
        plt.savefig('Outputs/bpm.png')


# This method returns a Gateway and a list with connected Transitions.
def setup_gateway(from_nodes: [Gateway or Activity],
                  to_nodes: [Gateway or Activity],
                  gateway_type: GatewayType,
                  condition_desc: [str] = None
                  ) -> (Gateway, [Transition]):
    transitions = []
    gateway = Gateway(gateway_type)
    for node in from_nodes:
        transitions.append(Transition(node, gateway))
    if condition_desc is not None:
        for index, node in enumerate(to_nodes):
            transition = Transition(gateway, node)
            if index < len(condition_desc):
                transition.description = condition_desc[index]
            transitions.append(transition)
    else:
        for node in to_nodes:
            transitions.append(Transition(gateway, node))

    return gateway, transitions


# This function gets a processModel and iterates over all transitions.
# All nodes without an incoming node become a start node.
# All nodes without an outgoing node become an end node.
def add_start_end(process_model: ProcessModel, starts = [], ends = []) -> ProcessModel:
    not_start_ids = []
    not_end_ids = []
    all_ids = []
    all_nodes = []

    for transition in process_model.transitions:
        not_start_ids.append(transition.going_to.id)
        not_end_ids.append(transition.going_from.id)
        all_ids.append(transition.going_to.id)
        all_ids.append(transition.going_from.id)
        all_nodes.append(transition.going_to)
        all_nodes.append(transition.going_from)

    swim_lanes = process_model.swim_lanes.copy()
    while len(swim_lanes) > 0:
        swim_lanes = swim_lanes + swim_lanes[0].sub_swim_lanes
        for activity in swim_lanes[0].activities:
            all_ids.append(activity.id)
            all_nodes.append(activity)
        swim_lanes.remove(swim_lanes[0])

    start_ids = set(all_ids) - set(not_start_ids)
    end_ids = set(all_ids) - set(not_end_ids)

    start_node = process_model.start_activity
    end_node = process_model.end_activity

    process_model.swim_lanes.append(SwimLane(['Process management'], [start_node, end_node], []))

    start_nodes = [] + starts
    end_nodes = [] + ends

    for node in all_nodes:
        if node.id in start_ids and node not in start_nodes:
            start_nodes.append(node)
        if node.id in end_ids and node not in end_nodes:
            end_nodes.append(node)

    for node in start_nodes:
        process_model.transitions.append(Transition(start_node, node))

    for node in end_nodes:
        process_model.transitions.append(Transition(node, end_node))

    process_model.start_activity = start_node
    process_model.end_activity = end_node

    return process_model


# Creates exemplary process model(Figure 1 from iterative approach)
def get_process_model_example() -> ProcessModel:

    swim_lanes = [SwimLane(['Handling department', 'Notification department'], [], [
        SwimLane(['Notification department'], [
            Activity('Check documentation'),
            Activity('Register claim')
        ], []),
        SwimLane(['Handling department'], [
            Activity('Check Insurance'),
            Activity('Perform assessment'),
            Activity('Reject claim'),
            Activity('Arrange repair'),
            Activity('Schedule payment'),
            Activity('Notify customer')
        ], [])
    ])]

    transitions = [
        Transition(swim_lanes[0].sub_swim_lanes[0].activities[0], swim_lanes[0].sub_swim_lanes[0].activities[1]),
        Transition(swim_lanes[0].sub_swim_lanes[0].activities[1], swim_lanes[0].sub_swim_lanes[1].activities[0]),
        Transition(swim_lanes[0].sub_swim_lanes[1].activities[0], swim_lanes[0].sub_swim_lanes[1].activities[1]),
        Transition(swim_lanes[0].sub_swim_lanes[1].activities[3], swim_lanes[0].sub_swim_lanes[1].activities[4])
    ]

    gateway1, transitions1 = setup_gateway([
        swim_lanes[0].sub_swim_lanes[1].activities[1]
    ], [
        swim_lanes[0].sub_swim_lanes[1].activities[2],
        swim_lanes[0].sub_swim_lanes[1].activities[3]
    ], GatewayType.XOR)
    gateway2, transitions2 = setup_gateway([
        swim_lanes[0].sub_swim_lanes[1].activities[2],
        swim_lanes[0].sub_swim_lanes[1].activities[4]
    ], [
        swim_lanes[0].sub_swim_lanes[1].activities[5]
    ], GatewayType.XOR)

    return ProcessModel(swim_lanes, [gateway1, gateway2], transitions + transitions1 + transitions2)


class Prestructure:
    def __init__(self, ingoing, outgoing):
        self.ingoing = ingoing
        self.outgoing = outgoing
