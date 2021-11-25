import xml.etree.cElementTree as eTree
import Models.BuisnessModelClasses as bmc
from Models.BuisnessModelClasses import GatewayType


def to_edges(transitions):
    edges = []
    for transition in transitions:
        edges.append((transition.going_from.id, transition.going_to.id, transition.description))
    return edges


def buildXML(model: bmc.ProcessModel):

    transitions = model.transitions

    # participants = []

    tasks: [bmc.Activity] = []
    for swimlane in model.swim_lanes:
        swimlane.add_actors_to_activity_names()
        tasks = tasks + swimlane.activities
        # participants.append(swimlane.actors)
        for sl in swimlane.sub_swim_lanes:
            sl.add_actors_to_activity_names()
            tasks = tasks + sl.activities
    gateways = model.gateways

    start = model.start_activity
    end = model.end_activity

    edges = to_edges(transitions)

    # pos_dict = pg.get_position_dict(edges, end.id, start.id)
    # print(pos_dict)

    root = eTree.Element('bpmn:definitions')
    root.set("xmlns", "http://www.omg.org/spec/BPMN/20100524/MODEL")
    root.set("xmlns:bpmndi", "http://www.omg.org/spec/BPMN/20100524/DI")
    root.set("xmlns:omgdc", "http://www.omg.org/spec/DD/20100524/DC")
    root.set("xmlns:di", "http://www.omg.org/spec/DD/20100524/DI")

    # Have to be implemented later when the own layout algorithm is built.
    # collaboration_root = eTree.Element('bpmn:collaboration', id="Collaboration")
    # root.append(collaboration_root)
    #
    # eTree.Element('bpmn:participant', id='test', name='Test', processRef='Process_1')


    process_root = eTree.Element('bpmn:process', id="Process_1")
    root.append(process_root)

    # Building a transition dict which stores for ever task its ingoing and outgoing transitions
    trans_dict = dict()
    for task in tasks:
        trans_dict[task.id] = ([], [])

    for gateway in gateways:
        trans_dict[gateway.id] = ([], [])

    for transition in transitions:
        print(transition)
        trans_dict[transition.going_from.id][1].append(transition.id)
        trans_dict[transition.going_to.id][0].append(transition.id)

    # Creating the xml elements for tasks
    for task in tasks:
        if task == start:
            taskXML = eTree.Element('bpmn:startEvent', id=task.id, name=task.activity_name)
        elif task == end:
            taskXML = eTree.Element('bpmn:endEvent', id=task.id, name=task.activity_name)
        else:
            taskXML = eTree.Element('bpmn:task', id=task.id, name=task.activity_name)

        for inc in trans_dict[task.id][0]:
            incXML = eTree.Element('bpmn:incoming')
            incXML.text = inc
            taskXML.append(incXML)
        for out in trans_dict[task.id][1]:
            outXML = eTree.Element('bpmn:outgoing')
            outXML.text = out
            taskXML.append(outXML)
        process_root.append(taskXML)

    # Creating the xml elements for gateways
    for gateway in gateways:
        if gateway.gateway_type == GatewayType.XOR:
            gatewayXML = eTree.Element('bpmn:exclusiveGateway', id=gateway.id)
            for inc in trans_dict[gateway.id][0]:
                incXML = eTree.Element('bpmn:incoming')
                incXML.text = inc
                taskXML.append(incXML)
            for out in trans_dict[gateway.id][1]:
                outXML = eTree.Element('bpmn:outgoing')
                outXML.text = out
                taskXML.append(outXML)
            process_root.append(gatewayXML)
        elif gateway.gateway_type == GatewayType.AND:
            gatewayXML = eTree.Element('bpmn:parallelGateway', id=gateway.id)
            for inc in trans_dict[gateway.id][0]:
                incXML = eTree.Element('bpmn:incoming')
                incXML.text = inc
                gatewayXML.append(incXML)
            for out in trans_dict[gateway.id][1]:
                outXML = eTree.Element('bpmn:outgoing')
                outXML.text = out
                gatewayXML.append(outXML)
            process_root.append(gatewayXML)


    # Creating the xml elements for transitions
    for transition in transitions:
        transitionXML = eTree.Element('bpmn:sequenceFlow', id=transition.id, sourceRef=transition.going_from.id,
                                      targetRef=transition.going_to.id)
        if transition.description != '':
            transitionXML.set('name', transition.description)
        process_root.append(transitionXML)

    # eTree.register_namespace('bpmndi', '1')
    #
    # vis_root = eTree.Element('bpmndi:BPMNDiagram', id='BpmnDiagram_1')
    # root.append(vis_root)
    #
    # lane_root = eTree.Element('bpmndi:BPMNPlane', id='BpmnPlane_1', bpmnElement='Process_1')
    # vis_root.append(lane_root)
    #
    # for transition in transitions:
    #     from_task = transition.going_from.id
    #     to_task = transition.going_to.id
    #
    #     if from_task[0] == 'a':
    #         x1_pos = str(pos_dict[from_task].x + 100)
    #         y1_pos = str(pos_dict[from_task].y + 40)
    #
    #     if from_task[0] == 'g':
    #         x1_pos = str(pos_dict[from_task].x + 75)
    #         y1_pos = str(pos_dict[from_task].y + 40)
    #
    #     if to_task[0] == 'a':
    #         x2_pos = str(pos_dict[to_task].x)
    #         y2_pos = str(pos_dict[to_task].y + 40)
    #
    #     if to_task[0] == 'g':
    #         x2_pos = str(pos_dict[to_task].x + 25)
    #         y2_pos = str(pos_dict[to_task].y + 40)
    #
    #     transitionXML_di = eTree.Element('bpmndi:BPMNEdge', id=(transition.id + '_di'), bpmnElement=transition.id)
    #
    #     if pos_dict[from_task].y > pos_dict[to_task].y:
    #
    #         x2_pos = str(pos_dict[to_task].x + 50)
    #         y2_pos = str(pos_dict[to_task].y + 55)
    #
    #         x3_pos = str(int(pos_dict[to_task].x) + 50)
    #         y3_pos = str(int(pos_dict[from_task].y) + 40)
    #         pos1XML = eTree.Element('di:waypoint', x=x1_pos, y=y1_pos)
    #         pos2XML = eTree.Element('di:waypoint', x=x2_pos, y=y2_pos)
    #         pos3XML = eTree.Element('di:waypoint', x=x3_pos, y=y3_pos)
    #         transitionXML_di.append(pos1XML)
    #         transitionXML_di.append(pos3XML)
    #         transitionXML_di.append(pos2XML)
    #     elif pos_dict[from_task].y < pos_dict[to_task].y:
    #
    #         x1_pos = str(pos_dict[from_task].x + 50)
    #         y1_pos = str(pos_dict[from_task].y + 55)
    #
    #         x3_pos = str(int(pos_dict[from_task].x) + 50)
    #         y3_pos = str(int(pos_dict[to_task].y) + 40)
    #         pos1XML = eTree.Element('di:waypoint', x=x1_pos, y=y1_pos)
    #         pos2XML = eTree.Element('di:waypoint', x=x2_pos, y=y2_pos)
    #         pos3XML = eTree.Element('di:waypoint', x=x3_pos, y=y3_pos)
    #         transitionXML_di.append(pos1XML)
    #         transitionXML_di.append(pos3XML)
    #         transitionXML_di.append(pos2XML)
    #     else:
    #         pos1XML = eTree.Element('di:waypoint', x=x1_pos, y=y1_pos)
    #         pos2XML = eTree.Element('di:waypoint', x=x2_pos, y=y2_pos)
    #
    #         transitionXML_di.append(pos1XML)
    #         transitionXML_di.append(pos2XML)
    #
    #     lane_root.append(transitionXML_di)
    #
    # for task in tasks:
    #     x_pos = str(pos_dict[task.id].x)
    #     y_pos = str(pos_dict[task.id].y)
    #     taskXML_di = eTree.Element('bpmndi:BPMNShape', id=(task.id + '_di'), bpmnElement=task.id)
    #     posXML = eTree.Element('omgdc:Bounds', x=x_pos, y=y_pos, width='100', height='80')
    #     taskXML_di.append(posXML)
    #     lane_root.append(taskXML_di)
    #
    # for gateway in gateways:
    #     x_pos = str(pos_dict[gateway.id].x + 25)
    #     y_pos = str(pos_dict[gateway.id].y + 15)
    #     gatewayXML_di = eTree.Element('bpmndi:BPMNShape', id=(gateway.id + '_di'), bpmnElement=gateway.id)
    #     posXML = eTree.Element('omgdc:Bounds', x=x_pos, y=y_pos, width='50', height='50')
    #     gatewayXML_di.append(posXML)
    #     lane_root.append(gatewayXML_di)

    eTree.ElementTree(root).write("../Outputs/process.xml")
    s = str(eTree.tostring(root))
    return s

# pm = bmc.add_start_end(bmc.get_process_model_example())
# buildXML(pm)