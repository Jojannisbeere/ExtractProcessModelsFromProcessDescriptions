from Models import BuisnessModelClasses as bmc, SentenceStructure as sen
from Models.BuisnessModelClasses import GatewayType
from TextProcessing.TextToProcessModel import RelationType
import TextProcessing.TextToProcessModel as tp
import TextProcessing.IndicatorLists as ind


def build_naive_process_model(sentences: [sen.SentencePart], relation: [sen.SentenceRelation], mergers) -> bmc.ProcessModel:
    swim_lanes: [bmc.SwimLane] = []
    transitions: [bmc.Transition] = []
    gateways: [bmc.Gateway] = []
    starts = []
    ends = []

    for sentence in sentences:

        relevant_activities = []

        for activity in sentence.activities:

            print(activity)
            if activity.is_relevant:

                relevant_activities.append(activity)

                def get_obj_act(act_name) -> (bmc.Prestructure, [bmc.Transition], [bmc.Gateway], [bmc.Activity]):
                    nodes = []
                    new_activities = []
                    new_gateways = []
                    new_transitions = []
                    if len(activity.obl) > 0:
                        for obj in activity.objects:
                            action = act_name + ' ' + obj
                            new_node, t, g, a = get_obl_act(action, 0)
                            new_transitions = new_transitions + t
                            new_gateways = new_gateways + g
                            new_activities = new_activities + a
                            nodes.append(new_node)
                    else:
                        for obj in activity.objects:
                            action = act_name + ' ' + obj
                            new_act = bmc.Activity(action)
                            nodes.append(bmc.Prestructure(new_act, new_act))
                            new_activities.append(new_act)

                    if activity.objects_or:
                        gateway1, transition1 = bmc.setup_gateway([], [node.ingoing for node in nodes], GatewayType.XOR)
                        gateway2, transition2 = bmc.setup_gateway([node.outgoing for node in nodes], [],
                                                                  GatewayType.XOR)
                        new_gateways = new_gateways + [gateway1, gateway2]
                        new_transitions = new_transitions + transition1 + transition2
                        return bmc.Prestructure(gateway1, gateway2), new_transitions, new_gateways, new_activities
                    else:
                        if len(nodes) > 1:
                            for i in range(len(nodes)-1):
                                new_transitions.append(bmc.Transition(nodes[i].outgoing, nodes[i + 1].ingoing))
                            return bmc.Prestructure(nodes[0].ingoing,
                                                    nodes[len(nodes) - 1].outgoing), new_transitions, new_gateways, new_activities
                        elif len(nodes) == 1:
                            return bmc.Prestructure(nodes[0].ingoing, nodes[0].outgoing), new_transitions, new_gateways, new_activities

                        else:
                            return None, new_transitions, new_gateways, new_activities

                def get_obl_act(act_name, j) -> (bmc.Prestructure, [bmc.Transition], [bmc.Gateway], [bmc.Activity]):
                    nodes = []
                    new_activities = []
                    new_gateways = []
                    new_transitions = []
                    if len(activity.obl) > 0:
                        if j == len(activity.obl) - 1:
                            for obl in activity.obl[j]:
                                action = act_name + ' ' + obl
                                new_act = bmc.Activity(action)
                                nodes.append(bmc.Prestructure(new_act, new_act))
                                new_activities.append(new_act)
                        else:
                            for obl in activity.obl[j]:
                                action = act_name + ' ' + obl
                                new_node, t, g, a = get_obl_act(action, j + 1)
                                new_transitions = new_transitions + t
                                new_gateways = new_gateways + g
                                new_activities = new_activities + a
                                nodes.append(new_node)

                        if activity.obl_or[j]:
                            gateway1, transition1 = bmc.setup_gateway([], [node.ingoing for node in nodes], GatewayType.XOR)
                            gateway2, transition2 = bmc.setup_gateway([node.outgoing for node in nodes], [],
                                                                      GatewayType.XOR)
                            new_gateways = new_gateways + [gateway1, gateway2]
                            new_transitions = new_transitions + transition1 + transition2
                            return bmc.Prestructure(gateway1, gateway2), new_transitions, new_gateways, new_activities

                        else:
                            if len(nodes) > 1:
                                for i in range(len(nodes)-1):
                                    new_transitions.append(bmc.Transition(nodes[i].outgoing, nodes[i + 1].ingoing))
                                return bmc.Prestructure(nodes[0].ingoing,
                                                        nodes[len(nodes) - 1].outgoing), new_transitions, new_gateways, new_activities

                            elif len(nodes) == 1:
                                return bmc.Prestructure(nodes[0].ingoing, nodes[0].outgoing), new_transitions, new_gateways, new_activities

                            else:
                                return None, [], new_gateways, new_activities
                    else:
                        return None, [], [], []


                def add_skip_option(activity):
                    ingoing = activity.matching_BPM_Activity_in
                    outgoing = activity.matching_BPM_Activity_out
                    gateway, transitions = bmc.setup_gateway([], [ingoing], GatewayType.XOR)
                    gateway2, transitions2 = bmc.setup_gateway([outgoing], [], GatewayType.XOR)
                    activity.matching_BPM_Activity_in = gateway
                    activity.matching_BPM_Activity_out = gateway2
                    return [gateway, gateway2], transitions + transitions2 + [bmc.Transition(gateway, gateway2)]

                actors = activity.actors.copy()

                if len(actors) == 0:
                    actors = ['unknown']

                subactivities = []

                for swim_lane in swim_lanes:
                    if set(swim_lane.actors) == set(actors):

                        if len(activity.objects) > 0:
                            n, t, g, a = get_obj_act(activity.action)
                            transitions.extend(t)
                            gateways.extend(g)
                        elif len(activity.obl) > 0:
                            n, t, g, a = get_obl_act(activity.action, 0)
                            transitions.extend(t)
                            gateways.extend(g)
                        else:
                            new_activity = bmc.Activity(activity.action)
                            a = [new_activity]
                            n = bmc.Prestructure(new_activity, new_activity)

                        subactivities.append(n)
                        swim_lane.activities.extend(a)

                        for actor in swim_lane.actors:
                            actors.remove(actor)

                for actor in actors:
                    if len(activity.objects) > 0:
                        n, t, g, a = get_obj_act(activity.action)
                        transitions.extend(t)
                        gateways.extend(g)
                    elif len(activity.obl) > 0:
                        n, t, g, a = get_obl_act(activity.action, 0)
                        transitions.extend(t)
                        gateways.extend(g)
                    else:
                        new_activity = bmc.Activity(activity.action)
                        a = [new_activity]
                        n = bmc.Prestructure(new_activity, new_activity)

                    subactivities.append(n)
                    swim_lanes.append(bmc.SwimLane([actor], a))

                if len(subactivities) > 1:
                    if activity.actors_or:
                        gateway_type = GatewayType.XOR
                    else:
                        gateway_type = GatewayType.AND
                    gateway1, transitions_gate1 = bmc.setup_gateway([], [subactivity.ingoing for subactivity in subactivities], gateway_type)
                    gateway2, transitions_gate2 = bmc.setup_gateway([subactivity.outgoing for subactivity in subactivities], [], gateway_type)

                    gateways = gateways + [gateway1, gateway2]

                    activity.matching_BPM_Activity_in = gateway1
                    activity.matching_BPM_Activity_out = gateway2
                    transitions = transitions + transitions_gate1 + transitions_gate2

                else:
                    if len(subactivities) == 1:
                        activity.matching_BPM_Activity_in = subactivities[0].ingoing
                        activity.matching_BPM_Activity_out = subactivities[0].outgoing

                if activity.optional:
                    gates, trans = add_skip_option(activity)
                    gateways.extend(gates)
                    transitions.extend(trans)

        if len(relevant_activities) == 1:
            sentence.entry_BPM = sentence.activities[0].matching_BPM_Activity_in
            sentence.exit_BPM = sentence.activities[0].matching_BPM_Activity_out
        elif not sentence.activities_or:
            sen_act = relevant_activities
            if len(sen_act) > 0:
                for i in range(len(sen_act) - 1):
                    transitions.append(bmc.Transition(sen_act[i].matching_BPM_Activity_out,
                                                      sen_act[i + 1].matching_BPM_Activity_in))
                sentence.entry_BPM = sen_act[0].matching_BPM_Activity_in
                sentence.exit_BPM = sen_act[len(sen_act) - 1].matching_BPM_Activity_out
        else:
            gate, trans = bmc.setup_gateway([], [a.matching_BPM_Activity_in for a in sentence.activities],
                                            GatewayType.XOR)
            transitions = transitions + trans
            gateways.append(gate)
            gate2, trans2 = bmc.setup_gateway([a.matching_BPM_Activity_out for a in sentence.activities], [],
                                              GatewayType.XOR)
            transitions = transitions + trans2
            gateways.append(gate2)
            sentence.entry_BPM = gate
            sentence.exit_BPM = gate2

        if sentence.is_start:
            starts.append(sentence.entry_BPM)
        if sentence.is_end:
            ends.append(sentence.exit_BPM)


    # print()
    # print(*relation, sep='\n')
    # print()

    print('POINT 2')
    print(transitions)

    rel_dict = sen.get_relation_dict(relation)

    def get_index(elem):
        return int(elem.indicator)

    all_follows = sorted(rel_dict[RelationType.FOLLOWINGSENTENCE], key=get_index)
    relevant_follows = []
    in_sen = None
    for rel in all_follows:
        if rel.s2.entry_BPM is not None and rel.s1.exit_BPM is not None:
            relevant_follows.append((rel.s1, rel.s2))
        elif rel.s2.entry_BPM is None and rel.s1.exit_BPM is not None:
            in_sen = rel.s1
        elif rel.s2.entry_BPM is not None and rel.s1.exit_BPM is None:
            if in_sen is not None:
                relevant_follows.append((in_sen, rel.s2))

    for rel in rel_dict[RelationType.PARALLEL]:
        if rel.s1 != rel.s2 and len(rel.s1.activities) > 0 and len(rel.s2.activities) > 0:
            gate, trans = bmc.setup_gateway([], [rel.s1.entry_BPM, rel.s2.entry_BPM], GatewayType.AND)
            transitions = transitions + trans
            gateways.append(gate)
            gate2, trans2 = bmc.setup_gateway([rel.s1.exit_BPM, rel.s2.exit_BPM], [], GatewayType.AND)
            transitions = transitions + trans2
            gateways.append(gate2)
            rel.s1.entry_BPM = gate
            rel.s2.entry_BPM = gate
            rel.s1.exit_BPM = gate2
            rel.s2.exit_BPM = gate2

    for rel in rel_dict[RelationType.CONDITION]:
        if rel.s1 != rel.s2 and rel.indicator not in ['if', 'or']:
            if len(rel.s1.activities) > 0 and len(rel.s2.activities) > 0:

                    new_rel_fol = []
                    for j in range(len(relevant_follows)):
                        if relevant_follows[j][1] == rel.s1:
                            if len(relevant_follows) - 1 > j and relevant_follows[j + 1][0] == rel.s1:
                                new_rel_fol.append((relevant_follows[j][0],
                                                    relevant_follows[j + 1][1]))
                        elif relevant_follows[j][0] != rel.s1:
                            new_rel_fol.append(relevant_follows[j])

                    relevant_follows = new_rel_fol

                    transitions.append(bmc.Transition(rel.s1.exit_BPM, rel.s2.entry_BPM))
                    rel.s1.exit_BPM = rel.s2.exit_BPM
                    rel.s2.entry_BPM = rel.s1.entry_BPM

    for rel in rel_dict[RelationType.SEQUENCE]:
        if rel.s1 != rel.s2:
            if len(rel.s1.activities) > 0 and len(rel.s2.activities) > 0:
                if rel.indicator in ind.following_ind:
                    transitions.append(bmc.Transition(rel.s1.exit_BPM, rel.s2.entry_BPM))
                    rel.s1.exit_BPM = rel.s2.exit_BPM
                    rel.s2.entry_BPM = rel.s1.entry_BPM
                elif rel.indicator in ind.preceding_ind:
                    transitions.append(bmc.Transition(rel.s2.exit_BPM, rel.s1.entry_BPM))
                    rel.s2.exit_BPM = rel.s1.exit_BPM
                    rel.s1.entry_BPM = rel.s2.entry_BPM

        if rel.s1 == rel.s2:
            if len(rel.s1.activities) > 0:
                pre_sentence = None
                for s in relevant_follows:
                    if s[1] == rel.s1:
                        relevant_follows.remove(s)
                        pre_sentence = s[0]
                if rel.indicator in ind.following_ind and pre_sentence is not None:
                    transitions.append(bmc.Transition(pre_sentence.exit_BPM, rel.s1.entry_BPM))
                    rel.s1.entry_BPM = pre_sentence.entry_BPM
                    pre_sentence.exit_BPM = rel.s1.exit_BPM
                elif rel.indicator in ind.preceding_ind and pre_sentence is not None:
                    transitions.append(bmc.Transition(rel.s1.exit_BPM, pre_sentence.entry_BPM))
                    pre_sentence.entry_BPM = rel.s1.entry_BPM
                    rel.s1.exit_BPM = pre_sentence.exit_BPM

    for rel in rel_dict[RelationType.PARALLEL]:
        if rel.s1 == rel.s2 and len(rel.s1.activities) > 0:
            for rel2 in rel_dict[RelationType.FOLLOWINGSENTENCE]:
                if rel2.s2 == rel.s1:
                    gate, trans = bmc.setup_gateway([], [rel.s1.entry_BPM, rel2.s1.entry_BPM], GatewayType.AND)
                    transitions = transitions + trans
                    gateways.append(gate)
                    gate2, trans2 = bmc.setup_gateway([rel.s1.exit_BPM, rel2.s1.exit_BPM], [], GatewayType.AND)
                    transitions = transitions + trans2
                    rel.s1.entry_BPM = gate
                    rel2.s1.entry_BPM = gate
                    rel.s1.exit_BPM = gate2
                    rel2.s1.exit_BPM = gate2
                    gateways.append(gate2)

    print('POINT 1.5')
    print(rel_dict[RelationType.CONDITION])
    print(transitions)

    main_sentence_follow = []
    for rel in rel_dict[RelationType.FOLLOWINGSENTENCE]:
        if not rel.s1.isSubsentence and rel.s1 not in main_sentence_follow:
            main_sentence_follow.append(rel.s1)
        if not rel.s2.isSubsentence:
            main_sentence_follow.append(rel.s2)

    print('POINT 1.4')
    print(main_sentence_follow)

    used_cond_rel = []
    for rel in rel_dict[RelationType.CONDITION]:
        if rel.indicator == 'or' and len(rel.s1.activities) > 0 and len(rel.s2.activities) > 0:
            gate, trans = bmc.setup_gateway([], [rel.s2.entry_BPM, rel.s1.entry_BPM], GatewayType.XOR)
            rel.s2.entry_BPM = gate
            rel.s1.entry_BPM = gate
            transitions = transitions + trans
            gateways.append(gate)

            gate2, trans2 = bmc.setup_gateway([rel.s2.exit_BPM, rel.s1.exit_BPM], [], GatewayType.XOR)
            rel.s2.exit_BPM = gate2
            rel.s1.exit_BPM = gate2
            transitions = transitions + trans2
            gateways.append(gate2)

        elif rel.indicator == 'if' and rel not in used_cond_rel:

            if len(rel.s2.activities) > 0:

                other_cases = []
                found_other_cases = False
                no_next = False
                check_sen = rel.s2
                while not no_next:
                    no_next = True
                    check_next_sen = check_sen
                    for cond_rel in rel_dict[RelationType.CONDITION]:
                        if cond_rel.indicator == 'if':
                            for i in range(len(main_sentence_follow) - 1):
                                if main_sentence_follow[i+1] == cond_rel.s2 and main_sentence_follow[i] == check_sen:
                                    used_cond_rel.append(cond_rel)
                                    if len(cond_rel.s2.activities) > 0:
                                        print('_________')
                                        print(cond_rel.s2)
                                        print(relevant_follows)

                                        new_rel_fol = []
                                        for j in range(len(relevant_follows)):
                                            if relevant_follows[j][1] == cond_rel.s2:
                                                if len(relevant_follows)-1 > j and relevant_follows[j+1][0] == cond_rel.s2:
                                                    new_rel_fol.append((relevant_follows[j][0], relevant_follows[j+1][1]))
                                            elif relevant_follows[j][0] != cond_rel.s2:
                                                new_rel_fol.append(relevant_follows[j])
                                        relevant_follows = new_rel_fol
                                        print(relevant_follows)

                                        no_next = False
                                        check_next_sen = cond_rel.s2
                                        found_other_cases = True
                                        other_cases.append((cond_rel.s1, cond_rel.s2))
                    check_sen = check_next_sen

                found_exception = False
                exception: sen.SentencePart
                for exc_rel in rel_dict[RelationType.EXCEPTION]:
                    if exc_rel.s1 == exc_rel.s2:
                        for i in range(len(main_sentence_follow) - 1):
                            if main_sentence_follow[i+1] == exc_rel.s1 and main_sentence_follow[i] == check_sen:
                                if len(exc_rel.s1.activities) > 0:

                                    new_rel_fol = []
                                    for j in range(len(relevant_follows)):
                                        if relevant_follows[j][1] == cond_rel.s2:
                                            if len(relevant_follows)-1 > j and relevant_follows[j + 1][0] == cond_rel.s2:
                                                new_rel_fol.append((relevant_follows[j][0],
                                                                   relevant_follows[j + 1][1]))
                                        elif relevant_follows[j][0] != cond_rel.s2:
                                            new_rel_fol.append(relevant_follows[j])

                                    relevant_follows = new_rel_fol

                                    found_exception = True
                                    exception = exc_rel.s1

                if found_other_cases or found_exception:
                    condition = tp.get_condition(rel.s1.dep_dict)
                    conditions = [condition]
                    input_case = [rel.s2.entry_BPM]
                    output_case = [rel.s2.exit_BPM]
                    if found_other_cases:
                        for case in other_cases:
                            cond = tp.get_condition(case[0].dep_dict)
                            for case2 in other_cases:
                                if case2 != case and case2[1] == case[1]:
                                    cond = cond + ' && ' + tp.get_condition(case2[0].dep_dict)
                                    other_cases.remove(case2)
                            conditions.append(cond)
                            input_case.append(case[1].entry_BPM)
                            output_case.append(case[1].exit_BPM)
                    if found_exception:
                        except_cond = ''
                        if condition != '':
                            except_cond = f'!({condition})'
                        for i in range(len(conditions)-1):
                            if conditions[i+1] != '':
                                except_cond = except_cond + ' and ' + f'!({conditions[i+1]})'
                        conditions.append(except_cond)
                        input_case.append(exception.entry_BPM)
                        output_case.append(exception.exit_BPM)

                    gate, trans = bmc.setup_gateway([], input_case, GatewayType.XOR, conditions)
                    transitions = transitions + trans
                    gateways.append(gate)

                    gate2, trans2 = bmc.setup_gateway(output_case, [], GatewayType.XOR)
                    transitions = transitions + trans2
                    gateways.append(gate2)

                    rel.s2.entry_BPM = gate
                    rel.s2.exit_BPM = gate2

                    if found_other_cases:
                        print('#####')
                        print(other_cases)
                        for case in other_cases:
                            case[1].entry_BPM = gate
                            case[1].exit_BPM = gate2
                    if found_exception:
                        exception.entry_BPM = gate
                        exception.exit_BPM = gate2
                else:
                    condition = tp.get_condition(rel.s1.dep_dict)
                    gate, trans = bmc.setup_gateway([], [rel.s2.entry_BPM], GatewayType.XOR, [condition])
                    rel.s2.entry_BPM = gate
                    transitions = transitions + trans
                    gateways.append(gate)

                    gate2, trans2 = bmc.setup_gateway([rel.s2.exit_BPM], [], GatewayType.XOR)
                    rel.s2.exit_BPM = gate2
                    transitions = transitions + trans2
                    gateways.append(gate2)

                    transitions.append(bmc.Transition(gate, gate2))

    print('Point 1.25')
    print(transitions)
    print(relevant_follows)
    print('MERGERS:')
    print(mergers)
    mergers_to_delet = []
    for i in range(len(mergers)):
        for j in range(len(mergers)):
            if i < j and mergers[i][3][0] == mergers[j][3][0]:
                for merger in mergers:
                    if merger[3][0] == mergers[i][3][1] and merger[3][1] == mergers[j][3][1]:
                        mergers_to_delet.append(merger)
                        print(mergers_to_delet)
    for merger in mergers_to_delet:
        if merger in mergers:
            mergers.remove(merger)

    print('REDUCED MERGERS:')
    print(mergers)

    for merger in mergers:

        activity1: sen.Activity = merger[3][1]
        activity2 = merger[3][0]
        start = [activity2.matching_BPM_Activity_in]
        actor_equal = False
        for swim_lane in swim_lanes:
            if swim_lane.actors[0] == merger[0]:
                if start[0] in swim_lane.activities:
                    actor_equal = True
        if type(start[0]) == bmc.Activity and merger[1] in start[0].activity_name and merger[2] in start[0].activity_name and actor_equal:
            print('THIS WAY')
            node = start[0]
        else:

            search_done = False
            while not search_done and len(start) > 0:
                for t in transitions:
                    if start[0] == t.going_from:
                        if type(t.going_to) == bmc.Activity:
                            n = t.going_to.activity_name

                            actor_equal = False
                            for swim_lane in swim_lanes:
                                if swim_lane.actors[0] == merger[0]:
                                    if t.going_to in swim_lane.activities:
                                        actor_equal = True

                            if merger[1] in n and merger[2] in n and actor_equal:
                                node = t.going_to
                                search_done = True
                        start.append(t.going_to)
                start.remove(start[0])

        print(transitions)
        print(node.id)
        print(node)

        start = activity1.matching_BPM_Activity_in
        search_done = False
        while not search_done:
            found_one = False
            for t in transitions:
                if start == t.going_to:
                    start = t.going_from
                    found_one = True
            if not found_one:
                search_done = True
        activity1_in = start

        already_one = False
        candidates = [activity1_in]

        while len(candidates) > 0 and already_one == False:
            candidate = candidates[0]
            if candidate == node:
                already_one = True
            for trans in transitions:
                if trans.going_from == candidate:
                    candidates.append(trans.going_to)
            candidates.remove(candidate)

        print(already_one)

        if not already_one:

            start = activity1.matching_BPM_Activity_out
            search_done = False
            while not search_done:
                found_one = False
                for t in transitions:
                    if start == t.going_from:
                        start = t.going_to
                        found_one = True
                if not found_one:
                    search_done = True
            activity1_out = start

            for trans in transitions:
                if trans.going_from == node:
                    print('CHANGE OUT')
                    trans.going_from = activity1_out
                if trans.going_to == node:
                    print('CHANGE IN')
                    trans.going_to = activity1_in

            if node == activity2.matching_BPM_Activity_in:
                activity2.matching_BPM_Activity_in = activity1_in
            if node == activity2.matching_BPM_Activity_out:
                activity2.matching_BPM_Activity_out = activity1_out

            for sl in swim_lanes:
                if sl.actors == [merger[0]]:
                    for a in sl.activities:
                        if a == node:
                            sl.activities.remove(a)

            for index, rel_fol in enumerate(relevant_follows):

                if rel_fol[1].entry_BPM == node or rel_fol[1].exit_BPM == node:
                    new_from = rel_fol[0]
                    if len(relevant_follows) > index + 1 and relevant_follows[index + 1][0] == rel_fol[1]:
                        relevant_follows[index] = (new_from, relevant_follows[index + 1][1])
                        relevant_follows.remove(relevant_follows[index + 1])
                    else:
                        relevant_follows.remove(rel_fol)

                if rel_fol[1] == merger[4][1]:
                    new_from = rel_fol[0]
                    if len(relevant_follows) > index + 1 and relevant_follows[index+1][0] == merger[4][1]:
                        relevant_follows[index] = (new_from, relevant_follows[index + 1][1])
                        relevant_follows.remove(relevant_follows[index + 1])
                    else:
                        if rel_fol in relevant_follows:
                            relevant_follows.remove(rel_fol)
        print('Merger processed')

    # print(rel_dict)

    print(relevant_follows)

    print('POINT 1')

    print(transitions)

    for rel in relevant_follows:
        has_ingoing = False
        for transition in transitions:
            if transition.going_to == rel[1].entry_BPM:
                has_ingoing = True
        if not has_ingoing:
            follower = rel[0].exit_BPM
            follower_new = True
            while follower_new:
                follower_new = False
                for t in transitions:
                    if t.going_from == follower:
                        follower = t.going_to
                        follower_new = True
            if follower != rel[1].exit_BPM and follower != rel[1].entry_BPM:
                transitions.append(bmc.Transition(follower, rel[1].entry_BPM))

    # print(rel_dict[RelationType.EXCEPTION])

    print('POINT 0')

    print(transitions)

    print('FINIIIIISHED')

    return bmc.add_start_end(bmc.ProcessModel(swim_lanes, gateways, transitions), starts, ends)
