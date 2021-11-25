# All this indicator lists are by far not complete. These are just samples of some important indicators.

# Indicators for noun based activities and there flow relations
start_syn = ['start', 'begin', 'launch', 'initiate']
end_syn = ['stop', 'close', 'complete', 'finish', 'end', 'terminate']
preceding_flow = ['precede', 'lead', 'head']
follow_flow = ['follow']
flow_indicators = ['happen', 'occur'] + start_syn + end_syn + preceding_flow + follow_flow

process_syn = ['process', 'instance', 'case', 'procedure', 'activity', 'task', 'action']

# Indicators for dependencies that determine specific relations between activities
conditionIndicators = ['if', 'when', 'whenever', 'in order']
parallelIndicators = ['meanwhile', 'in the meantime', 'in parallel', 'parallel with', 'besides', 'during', 'while',
                      'meantime']
exceptionIndicators = ['otherwise', 'else']

following_ind = ['after', 'following', 'afterwards', 'as next step', 'after that', 'then', 'later', 'from then on',
                 'next', 'subsequently', 'in the following', 'thereafter']
preceding_ind = ['before', 'previously', 'before that']
sequenceIndicators = following_ind + preceding_ind


example_indicators = ['for example', 'e.g.', 'for instance', 'to illustrate', 'in particular', 'i.e.']

state_verbs = ['have', 'be', 'like', 'love', 'want', 'hate', 'own', 'prefer', 'sound', 'dislike', 'deserve', 'mean',
               'know', 'belong', 'depend', 'consist', 'contain']

optional_aux = ['can', 'could', 'might', 'may']
optional_advmod = ['sometimes']
