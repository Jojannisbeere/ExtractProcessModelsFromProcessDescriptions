import Models.BuisnessModelClasses as bmc
from enum import Enum


class RelationType(Enum):
    CONDITION = 'Condition'
    SEQUENCE = 'Sequence'
    FOLLOWINGSENTENCE = 'FollowingSentence'
    PARALLEL = 'Parallel'
    EXCEPTION = 'Exception'

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


class SentencePart:
    def __init__(self, text: str):
        self.text = text
        self.isSubsentence = False
        self.activities = []
        self.activities_or = False
        self.dep_dict = []
        self.is_start = False
        self.is_end = False
        self.entry_BPM: bmc.Activity or bmc.Transition = None
        self.exit_BPM: bmc.Activity or bmc.Transition = None

    def __repr__(self):
        return 'Text(' + self.text + ')'

    def __str__(self):
        return 'Text(' + self.text + ')'


class SentenceRelation:
    def __init__(self, s1: SentencePart, s2: SentencePart, rel: RelationType, indicator: str):
        self.s1 = s1
        self.s2 = s2
        self.rel = rel
        self.indicator = indicator

    def __repr__(self):
        return 'Relation(' + str(self.s1) + ', ' + str(self.s2) + ', ' + str(self.rel) + ', <<' + self.indicator + '>>)'

    def __str__(self):
        return 'Relation(' + str(self.s1) + ', ' + str(self.s2) + ', ' + str(self.rel) + ', <<' + self.indicator + '>>)'


def get_relation_dict(relation: [SentenceRelation]) -> dict:
    rel_dict = {RelationType.SEQUENCE: [],
                RelationType.CONDITION: [],
                RelationType.FOLLOWINGSENTENCE: [],
                RelationType.PARALLEL: [],
                RelationType.EXCEPTION: []}

    for rel in relation:
        if rel.rel == RelationType.SEQUENCE:
            rel_dict[RelationType.SEQUENCE].append(rel)
        elif rel.rel == RelationType.CONDITION:
            rel_dict[RelationType.CONDITION].append(rel)
        elif rel.rel == RelationType.FOLLOWINGSENTENCE:
            rel_dict[RelationType.FOLLOWINGSENTENCE].append(rel)
        elif rel.rel == RelationType.PARALLEL:
            rel_dict[RelationType.PARALLEL].append(rel)
        elif rel.rel == RelationType.EXCEPTION:
            rel_dict[RelationType.EXCEPTION].append(rel)

    return rel_dict


class Activity:
    def __init__(self, action: str, actors: [str] = [], objects: [str] = [], obl: [[str]] = []):
        self.actors = actors
        self.objects = objects
        self.action = action
        self.obl = obl
        self.actors_or = False
        self.objects_or = False
        self.obl_or = []
        self.optional = False
        self.is_relevant = True
        self.matching_BPM_Activity_in: bmc.Activity or bmc.Gateway
        self.matching_BPM_Activity_out: bmc.Activity or bmc.Gateway

    def __str__(self):
        return 'Activity(' + str(self.actors) + ', ' + str(self.action) + ', ' + str(self.objects) + ')'

    def __repr__(self):
        return 'Activity(' + str(self.actors) + ', ' + str(self.action) + ', ' + str(self.objects) + ')'
