import re
import nltk
from Models.SentenceStructure import RelationType
import Models.SentenceStructure as sen
from TextProcessing.AnaphoraResolution import get_resolved_text
from ProcessModelBuilder import build_naive_process_model
import TextProcessing.IndicatorLists as ind
from nltk.corpus import wordnet as wn


def create_triples(sentence: str) -> [((str, str), str, (str, str))]:
    dep_parser = nltk.CoreNLPDependencyParser(url='http://localhost:9000')
    helpl = list(dep_parser.parse(nltk.casual_tokenize(sentence)))
    triples = []
    for triple in helpl[0].triples():
        triples.append(triple)
    return triples


def triples_to_dict(triples: [((str, str), str, (str, str))]) -> dict:
    triples_dict = {'aux': [], 'conj': [], 'nsubj': [], 'nsubjpass': [], 'obj': [], 'obl': [], 'case': [],
                    'compound': [], 'auxpass': [], 'det': [], 'amod': [], 'aclrelcl': [], 'cc': [], 'mark': [],
                    'nmod': [], 'advmod': [], 'amod': []}

    print(*triples, sep='\n')
    print('_____________')

    for i in triples:
        if i[1] == 'aux':
            triples_dict['aux'].append(i)
        elif i[1] == 'conj':
            triples_dict['conj'].append(i)
        elif i[1] == 'nsubj':
            triples_dict['nsubj'].append(i)
        elif i[1] == 'nsubj:pass':
            triples_dict['nsubjpass'].append(i)
        elif i[1] == 'obj':
            triples_dict['obj'].append(i)
        elif i[1] == 'obl':
            triples_dict['obl'].append(i)
        elif i[1] == 'case':
            triples_dict['case'].append(i)
        elif i[1] == 'compound':
            triples_dict['compound'].append(i)
        elif i[1] == 'aux:pass':
            triples_dict['auxpass'].append(i)
        elif i[1] == 'det':
            triples_dict['det'].append(i)
        elif i[1] == 'amod':
            triples_dict['amod'].append(i)
        elif i[1] == 'acl:relcl':
            triples_dict['aclrelcl'].append(i)
        elif i[1] == 'cc':
            triples_dict['cc'].append(i)
        elif i[1] == 'mark':
            triples_dict['mark'].append(i)
        elif i[1] == 'nmod':
            triples_dict['nmod'].append(i)
        elif i[1] == 'advmod':
            triples_dict['advmod'].append(i)
        elif i[1] == 'amod':
            triples_dict['nmod'].append(i)

    return triples_dict


####################################################
# Tests with WordNet

# print(wn.synsets('teacher'))
# print(wn.synset('food.n.01'))
# print(wn.synset('food.n.01').hypernyms())

# synsets1 = wn.synsets('monkey', pos='n')
# synsets2 = wn.synsets('ape', pos='n')
# minSim1 = 0
# minSim2 = 0

# for synset1 in synsets1:
#     for synset2 in synsets2:

#         sim1 = wn.path_similarity(synset1,synset2)
#         if sim1 > minSim1:
#             minSim1 = sim1

#         sim2 = wn.lch_similarity(synset1,synset2)
#         if sim2 > minSim2:
#             minSim2 = sim2

# print(minSim1)
# print(minSim2)

######################################################

# Split text into sentences and split sentences into subsentences (e.g. caused by 'and')
def split_sentences(text: str) -> ([sen.SentencePart], [sen.SentenceRelation]):
    sentences = []
    relation = []
    sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
    for sentence in sent_detector.tokenize(text.strip()):
        sen, rel = split_subsentences(sentence)
        sentences = sentences + sen
        relation = relation + rel
    return sentences, relation


def split_subsentences(sentence: str) -> ([sen.SentencePart], [sen.SentenceRelation]):
    sentences = []
    relation = []

    main = []

    extra_dep = get_who(sentence)

    parser = nltk.CoreNLPParser(url='http://localhost:9000')
    parser_output = list(parser.raw_parse(sentence))

    # parser_output[0].draw()

    extra_rel = detect_relation(parser_output[0][0])

    subsentences, conj_indicator = find_subsentences(parser_output[0][0])

    for subsentence in subsentences:
        side_sentences, conj_sig = split_sbar(subsentence)

        lib1 = sen.SentencePart(' '.join(subsentence.leaves()))
        sentences.append(lib1)
        main.append(lib1)

        if type(extra_rel[0]) == RelationType:
            relation.append(sen.SentenceRelation(lib1, lib1, extra_rel[0], extra_rel[1]))

        for s in side_sentences:
            lib2 = sen.SentencePart(' '.join(s.leaves()))
            lib2.isSubsentence = True
            sentences.append(lib2)
            lib2.dep_dict = lib2.dep_dict + extra_dep
            relation = relation + check_for_relation(s, lib2, lib1)
            # print(find_in(side_sentences[0]))

    if conj_indicator == 'and':
        for i in range(len(main) - 1):
            relation.append(sen.SentenceRelation(main[i], main[i + 1], RelationType.SEQUENCE, 'and'))
    elif conj_indicator == 'or':
        for i in range(len(main) - 1):
            relation.append(sen.SentenceRelation(main[i], main[i + 1], RelationType.CONDITION, 'or'))
    return sentences, relation


def find_subsentences(tree: nltk.Tree) -> ([nltk.Tree], str):
    split_sentences = []
    conj_indicator = ''
    for subsen in tree:
        if type(subsen) is nltk.Tree:
            if subsen.label() == 'S':
                split_sentences.append(subsen)
            if subsen.label() == 'CC':
                conj_indicator = subsen.leaves()[0].lower()
    return ([tree], conj_indicator) if len(split_sentences) == 0 else (split_sentences, conj_indicator)


def detect_relation(tree: nltk.Tree) -> (RelationType, str):
    clauses = []
    while type(tree) is nltk.Tree:
        if tree.label() in ['ADVP', 'PP']:
            indicator = ' '.join(tree.leaves()).lower()
            if indicator in ind.sequenceIndicators:
                return RelationType.SEQUENCE, indicator
            elif indicator in ind.parallelIndicators:
                return RelationType.PARALLEL, indicator
            elif indicator in ind.exceptionIndicators:
                return RelationType.EXCEPTION, indicator
        tree = tree[0]
    return '', ''


# def split_sbar(tree: nltk.Tree):
#     clauses = []
#     for node in tree:
#         if type(node) is nltk.Tree:
#             if node.label() == 'SBAR':
#                 clauses.append(node)
#                 tree.remove(node)
#             clauses = split_sbar(node) + clauses
#     return clauses

def split_sbar(tree: nltk.Tree) -> ([nltk.Tree], ([int], str)):
    candidates = [tree]
    sbars = []
    dep = []
    index = 0
    while len(candidates) > 0:
        for child in candidates[0]:
            if type(child) is nltk.Tree:
                candidates.append(child)
                if child.label() == 'SBAR':
                    candidates[0].remove(child)
                    s = []
                    conjunction = False
                    conj_sig = ''
                    conj_sen = []
                    for c in child:
                        if type(c) is nltk.Tree:
                            if c.label() == 'SBAR':
                                s.append(c)
                                conj_sen.append(index)
                                index += 1
                            if c.label() == 'CC':
                                conjunction = True
                                conj_sig = c.leaves()[0]
                    if conjunction:
                        dep.append((conj_sen, conj_sig))
                        sbars = sbars + s
                    else:
                        sbars.append(child)
                        index += 1
        candidates.remove(candidates[0])
    return sbars, dep


# Extracts the dependency of the person that is referenced by 'who'
# (e.g. The [person] cooks [who] then makes the dishes.)
def get_who(sentence: str) -> [((str, str), str, (str, str))]:
    depends = []
    for dep in create_triples(sentence):
        if dep[1] == 'acl:relcl':
            depends.append(dep)
    return depends


def generator_to_list(generator) -> []:
    new_list = []
    for element in generator:
        new_list.append(element)
    return new_list


def find_in(tree: nltk.Tree) -> str:
    while type(tree) is nltk.Tree:
        tree = tree[0]
    return tree


def check_for_relation(tree: nltk.Tree, child_sentence: sen.SentencePart, parent_sentence: sen.SentencePart) \
        -> [sen.SentenceRelation]:
    relations = []
    while type(tree) is nltk.Tree:
        if tree.label() == 'WHADVP' or tree.label() == 'IN':
            indicator = ' '.join(tree.leaves()).lower()
            if indicator in ind.conditionIndicators:
                relations.append(
                    sen.SentenceRelation(child_sentence, parent_sentence, RelationType.CONDITION, indicator))
            elif indicator in ind.sequenceIndicators:
                relations.append(
                    sen.SentenceRelation(child_sentence, parent_sentence, RelationType.SEQUENCE, indicator))
            elif indicator in ind.parallelIndicators:
                relations.append(
                    sen.SentenceRelation(child_sentence, parent_sentence, RelationType.PARALLEL, indicator))
            elif indicator in ind.exceptionIndicators:
                relations.append(
                    sen.SentenceRelation(child_sentence, parent_sentence, RelationType.EXCEPTION, indicator))
        tree = tree[0]
    return relations


# Creates DirectlyFollows Relation for the MainSentences (Subsentences are excluded)
def get_directly_follows(sentences: [sen.SentencePart]) -> [sen.SentenceRelation]:
    relation = []
    if len(sentences) == 0:
        return []
    last_sentence = -1
    for index, sentence in enumerate(sentences):
        # if not sentence.isSubsentence:
            if last_sentence >= 0:
                relation.append(sen.SentenceRelation(sentences[last_sentence], sentence, RelationType.FOLLOWINGSENTENCE,
                                                     str(index)))
            last_sentence = index
    return relation


def extract_candidates(sentence: sen.SentencePart, dep_dict: dict) -> [str]:
    verb_candidates = []
    # tokenized_sentence = nltk.casual_tokenize(sentence)
    # for word in nltk.pos_tag(tokenized_sentence):
    #     if word[1] in ['VB', 'VBP', 'VBZ', 'VBN', 'VBG']:
    #         verb_candidates.append(word[0])

    for nsubj_dep in dep_dict['nsubj']:
        if not nsubj_dep[0][0] in verb_candidates:
            if nsubj_dep[0][1] in ['VB', 'VBP', 'VBZ', 'VBN', 'VBG']:
                verb_candidates.append(nsubj_dep[0][0])
                conj, cc = get_conj(nsubj_dep[0], dep_dict)
                if cc == 'or':
                    sentence.activities_or = True
                verb_candidates = verb_candidates + conj

    for nsubjpass_dep in dep_dict['nsubjpass']:
        if not nsubjpass_dep[0][0] in verb_candidates:
            if nsubjpass_dep[0][1] in ['VB', 'VBP', 'VBZ', 'VBN', 'VBG']:
                verb_candidates.append(nsubjpass_dep[0][0])
                conj, cc = get_conj(nsubjpass_dep[0], dep_dict)
                if cc == 'or':
                    sentence.activities_or = True
                verb_candidates = verb_candidates + conj

    # Remove help verbs from candidate list (e.g. The message [is] sent.)
    for auxpass_dep in dep_dict['auxpass']:
        for verb_candidate in verb_candidates:
            if auxpass_dep[2][0] == verb_candidate:
                verb_candidates.remove(verb_candidate)

    return verb_candidates


def find_object(verb: str, dep_dict: dict) -> ([str], bool):
    obj = []
    or_conj = False
    # Searches objects in active case (e.g. The boy plays [football].)
    for obj_dep in dep_dict['obj']:
        if verb == obj_dep[0][0]:
            obj.append(find_compound(obj_dep[2][0], dep_dict))
            conj, cc = get_conj(obj_dep[2], dep_dict)
            if cc == 'or':
                or_conj = True
            obj = obj + conj
    if len(obj) == 0:
        for conj_dep in dep_dict['conj']:
            if verb == conj_dep[0][0]:
                obj = obj + find_object(conj_dep[2][0], dep_dict)[0]

    # Searches objects in passive case (e.g. The [confirmation] is received.)
    for nsubjpass_dep in dep_dict['nsubjpass']:
        if verb == nsubjpass_dep[0][0]:
            obj.append(find_compound(nsubjpass_dep[2][0], dep_dict))
            conj, cc = get_conj(nsubjpass_dep[2], dep_dict)
            if cc == 'or':
                or_conj = True
            obj = obj + conj

    return obj, or_conj


# Example: I go [to school (and) the office] [in the morning (or) evening].
def find_obl(verb: str, dep_dict: dict) -> ([[str]], [bool]):
    obl_list = []
    or_conj_list = []

    for obl_dep in dep_dict['obl']:
        or_conj = False
        if verb == obl_dep[0][0]:
            obl = [obl_dep[2][0]]
            conj, cc = get_conj(obl_dep[2], dep_dict)
            if cc == 'or':
                or_conj = True
            obl = obl + conj
            case = ''
            for case_dep in dep_dict['case']:
                if case_dep[0][0] in obl:
                    for i in range(len(obl)):
                        case = case_dep[2][0]
                        obl[i] = case + ' ' + find_compound(obl[i], dep_dict)
            if case != 'by':
                obl_list.append(obl)
                or_conj_list.append(or_conj)

    return obl_list, or_conj_list


def find_compound(word: str, dep_dict: dict) -> str:
    compound_word = word
    for comp in dep_dict['compound']:
        if comp[0][0] == word:
            compound_word = comp[2][0] + ' ' + compound_word

    for amod_dep in dep_dict['amod']:
        if amod_dep[0][0] == word:
            compound_word = amod_dep[2][0] + ' ' + compound_word

    for det_dep in dep_dict['det']:
        if det_dep[0][0] == word and det_dep[2][0] == 'no':
            compound_word = det_dep[2][0] + ' ' + compound_word
    return compound_word


# Returns a list of words that seem to be the actor for the verb
def add_actors(verb: str, dep_dict: dict) -> ([str], bool):
    or_conj = False

    # Searches actors in active case (e.g. The [supplier] sends the message.)
    actors = []
    for conj_dep in dep_dict['conj']:
        if conj_dep[2][0] == verb:
            actors = actors + add_actors(conj_dep[0][0], dep_dict)[0]
    for nsubj_dep in dep_dict['nsubj']:
        if nsubj_dep[0][0] == verb:
            if nsubj_dep[2][0] == 'who':
                for aclrelcl_dep in dep_dict['aclrelcl']:
                    if aclrelcl_dep[2][0] == verb:
                        actors.append(aclrelcl_dep[0][0])
            else:
                actors.append(find_compound(nsubj_dep[2][0], dep_dict))
                conj, cc = get_conj(nsubj_dep[2], dep_dict)
                if cc == 'or':
                    or_conj = True
                actors = actors + conj

    # Searches actors in passive case (e.g. The package is ordered by the [manager].)
    for obl_dep in dep_dict['obl']:
        if verb == obl_dep[0][0]:
            for case_dep in dep_dict['case']:
                if case_dep[0][0] == obl_dep[2][0] and 'by' == case_dep[2][0]:
                    actors.append(find_compound(obl_dep[2][0], dep_dict))
                    conj, cc = get_conj(obl_dep[2], dep_dict)
                    if cc == 'or':
                        or_conj = True
                    actors = actors + conj

    return actors, or_conj


def get_conj(pair: (str, str), dep_dict: dict) -> [str]:
    conj = []
    cc = 'undefined'
    for conj_dep in dep_dict['conj']:
        if conj_dep[0] == pair:
            conj.append(find_compound(conj_dep[2][0], dep_dict))
            for cc_dep in dep_dict['cc']:
                if cc_dep[0] == conj_dep[2]:
                    cc = cc_dep[2][0]
    return conj, cc


def set_activity_relevance(activity):
    if activity.action in ind.start_syn:
        for actor in activity.actors:
            if actor in ind.process_synonyms:
                activity.is_relevant = False


def verbify(verb_word):
    noun_synsets = wn.synsets(verb_word, pos="n")

    if not noun_synsets:
        return None

    noun_lemmas = [l for s in noun_synsets for l in s.lemmas() if s.name().split('.')[1] == 'n']

    derivationally_related_forms = [(l, l.derivationally_related_forms()) for l in noun_lemmas]

    related_verb_lemmas = [l for drf in derivationally_related_forms for l in drf[1] if
                           l.synset().name().split('.')[1] == 'v']

    words = [l.name() for l in related_verb_lemmas]
    len_words = len(words)

    result = [[w, float(words.count(w)) / len_words] for w in set(words)]

    ps = nltk.stem.PorterStemmer()
    verb_stem = ps.stem(verb_word)
    for r in result:
        if r[0].startswith(verb_stem):
            r[1] = r[1] + 1

    result.sort(key=lambda w: -w[1])

    print(result)

    if len(result) > 0:
        return result[0][0]


def create_noun_based_activity(verb, depends, relation, sent_part) -> [sen.Activity]:
    new_acts1 = []
    new_acts2 = []
    actors, act1_or = add_actors(verb, depends)
    activity1 = actors
    activity2, act2_or = find_object(verb, depends)
    a1 = []
    a2 = []
    for act in activity1:
        action = verbify(act)
        if action is not None:
            obj, cc = find_nmod(act, depends)
            print(action)
            print(obj)
            new_act = sen.Activity(action, [], obj, [])
            new_act.objects_or = cc
            new_acts1.append(new_act)

    for act in activity2:
        action = verbify(act)
        if action is not None:
            obj, cc = find_nmod(act, depends)
            print(action)
            print(obj)
            new_act = sen.Activity(action, [], obj, [])
            new_act.objects_or = cc
            new_acts2.append(new_act)

    lemma = nltk.wordnet.WordNetLemmatizer()
    inf_verb = lemma.lemmatize(verb, 'v')

    if inf_verb in ind.follow_flow:
        return new_acts2 + new_acts1
    elif inf_verb in ind.preceding_flow:
        return new_acts1 + new_acts2
    elif inf_verb in ind.start_syn:
        if len(set(ind.process_syn).intersection(set(actors))) > 0:
            found_sth = False
            for rel in relation:
                if rel.s2 == sent_part and rel.rel == RelationType.CONDITION and rel.indicator == 'when':
                    found_sth = True
                    rel.s1.is_start = True

            for obl_dep in depends['obl']:
                if obl_dep[0][0] == verb:
                    acts = []
                    conj, cc1 = get_conj(obl_dep[2], depends)
                    obls = [obl_dep[2][0]] + conj
                    for o in obls:
                        action = verbify(o)
                        if action is not None:
                            if not found_sth:
                                sent_part.is_start = True
                            obj, cc = find_nmod(o, depends)
                            new_act = sen.Activity(action, [], obj, [])
                            new_act.objects_or = cc
                            acts.append(new_act)
                    if cc1 == 'or':
                        sent_part.activities_or = True
                    return acts
            return []
        else:
            return new_acts2

    elif inf_verb in ind.end_syn:
        if len(set(ind.process_syn).intersection(set(actors))) > 0:
            found_sth = False
            for rel in relation:
                if rel.s2 == sent_part and rel.rel == RelationType.CONDITION and rel.indicator == 'when':
                    found_sth = True
                    rel.s1.is_end = True

            for obl_dep in depends['obl']:
                if obl_dep[0][0] == verb:
                    acts = []
                    conj, cc1 = get_conj(obl_dep[2], depends)
                    obls = [obl_dep[2][0]] + conj
                    for o in obls:
                        action = verbify(o)
                        if action is not None:
                            if not found_sth:
                                sent_part.is_end = True
                            obj, cc = find_nmod(o, depends)
                            new_act = sen.Activity(action, [], obj, [])
                            new_act.objects_or = cc
                            acts.append(new_act)
                    if cc1 == 'or':
                        sent_part.activities_or = True
                    return acts
            return []
        else:
            return new_acts2

    else:
        return []


def find_nmod(act, dep_dict) -> ([str], bool):
    obj = []
    or_conj = False

    for nmod_dep in dep_dict['nmod']:
        if act == nmod_dep[0][0]:
            obj.append(find_compound(nmod_dep[2][0], dep_dict))
            conj, cc = get_conj(nmod_dep[2], dep_dict)
            if cc == 'or':
                or_conj = True
            obj = obj + conj

    return obj, or_conj


def check_optional(verb: str, dep_dict) -> bool:
    for aux_dep in dep_dict['aux']:
        if aux_dep[0][0] == verb and aux_dep[2][0] in ind.optional_aux:
            return True
    for advmod_dep in dep_dict['advmod']:
        if advmod_dep[0][0] == verb and advmod_dep[2][0] in ind.optional_advmod:
            return True
    for conj_dep in dep_dict['conj']:
        if conj_dep[2][0] == verb:
            return check_optional(conj_dep[0][0], dep_dict)
    return False


def create_process_model(input_text: str):
    text = ''
    for s in input_text.split('\n'):
        if len(s) > 0 and s[0] != '#':
            text = text + s + '\n'

    text = re.sub(r'\([^()]*\)', '', text)

    input_text = get_resolved_text(text)
    # input_text = text
    print(input_text)

    input_sentences, relation = split_sentences(input_text)

    relation = relation + get_directly_follows(input_sentences)

    verbs = []
    lemma = nltk.wordnet.WordNetLemmatizer()
    for sentence in input_sentences:
        sentence_verbs = []
        depends = triples_to_dict(create_triples(sentence.text) + sentence.dep_dict)
        sentence.dep_dict = depends

        no_verbs = False
        for rel in relation:
            if rel.s1 == sentence and rel.rel == RelationType.CONDITION and rel.indicator == 'if':
                no_verbs = True

        if not no_verbs:
            for verb in extract_candidates(sentence, depends):
                inf_verb = lemma.lemmatize(verb, 'v')
                if inf_verb not in ind.state_verbs:
                    if inf_verb not in ind.flow_indicators:
                        actors, actors_or = add_actors(verb, depends)
                        objects, objects_or = find_object(verb, depends)
                        obl, obl_or = find_obl(verb, depends)
                        sentence_verbs.append((actors, inf_verb, objects))
                        new_act = sen.Activity(inf_verb, actors, objects, obl)
                        new_act.actors_or = actors_or
                        new_act.objects_or = objects_or
                        new_act.obl_or = obl_or
                        new_act.optional = check_optional(verb, depends)
                        set_activity_relevance(new_act)
                        sentence.activities.append(new_act)
                    else:
                        new_act = create_noun_based_activity(verb, depends, relation, sentence)
                        sentence.activities.extend(new_act)

            verbs.append(sentence_verbs)

    all_atomic_activities = []
    for i_sen in input_sentences:
        for activity in i_sen.activities:
            objs = activity.objects
            actors = activity.actors
            action = activity.action
            if len(objs) > 0:
                for obj in objs:
                    if len(actors) > 0:
                        for actor in actors:
                            all_atomic_activities.append((actor, action, obj, activity, i_sen))
                    else:
                        all_atomic_activities.append((None, action, obj, activity, i_sen))
            else:
                if len(actors) > 0:
                    for actor in actors:
                        all_atomic_activities.append((actor, action, None, activity, i_sen))
                else:
                    all_atomic_activities.append((None, action, None, activity, i_sen))

    merge_candidats = []
    for i, aaa1 in enumerate(all_atomic_activities):
        for j, aaa2 in enumerate(all_atomic_activities):
            if aaa1 != aaa2 and aaa1[0] is not None and aaa1[2] is not None and aaa2[0] is not None and \
                    aaa2[2] is not None and j > i:
                if aaa1[0] == aaa2[0] and aaa1[1] == aaa2[1] and aaa1[2] == aaa2[2]:
                    merge_candidats.append((aaa1[0], aaa1[1], aaa1[2], (aaa1[3], aaa2[3]), (aaa1[4], aaa2[4])))

    print(merge_candidats)

    print(*verbs, sep='\n')
    print('--')
    return build_naive_process_model(input_sentences, relation, merge_candidats)


def get_condition(dep_dict: dict) -> str:
    formula = []
    for mark_dep in dep_dict['mark']:
        if mark_dep[2][0].lower() == 'if':
            condition = mark_dep[0]
            for nsubj_dep in dep_dict['nsubj']:
                if condition == nsubj_dep[0]:
                    specification1 = ''
                    specification2 = ''
                    for amod_dep in dep_dict['amod']:
                        if amod_dep[0] == nsubj_dep[0]:
                            specification2 = amod_dep[2][0] + ' '
                        elif amod_dep[0] == nsubj_dep[2]:
                            specification1 = amod_dep[2][0] + ' '
                    is_not = False
                    person = find_compound(nsubj_dep[2][0], dep_dict)
                    for advmod_dep in dep_dict['advmod']:
                        if advmod_dep[0] == nsubj_dep[0] and advmod_dep[2][0] == 'not':
                            is_not = True
                            formula.append(specification1 + person + ' != ' + specification2 + condition[0])
                    if not is_not:
                        formula.append(specification1 + person + ' == ' + specification2 + condition[0])
            conj, cc = get_conj(condition, dep_dict)
            print('CONJUNCTION')
            print(conj)
            for c in conj:
                for nsubj_dep in dep_dict['nsubj']:
                    if nsubj_dep[0][0] == c:
                        specification1 = ''
                        specification2 = ''
                        for amod_dep in dep_dict['amod']:
                            if amod_dep[0] == nsubj_dep[0]:
                                specification2 = amod_dep[2][0] + ' '
                            elif amod_dep[0] == nsubj_dep[2]:
                                specification1 = amod_dep[2][0] + ' '
                        is_not = False
                        for advmod_dep in dep_dict['advmod']:
                            if advmod_dep[0] == nsubj_dep[0] and advmod_dep[2][0] == 'not':
                                is_not = True
                                formula.append(specification1 + nsubj_dep[2][0] + ' != ' + specification2 + c)
                        if not is_not:
                            formula.append(specification1 + nsubj_dep[2][0] + ' == ' + specification2 + c)

            if cc == 'or':
                return ' || '.join(formula)
            else:
                return ' && '.join(formula)
    return ''
