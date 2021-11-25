import math

import numpy as np

from ProcessModelToBPMN.ConverterBPMN import buildXML
from TextProcessing.TextToProcessModel import create_process_model
from Models.BuisnessModelClasses import GatewayType
from os import listdir
import multiprocessing
import time
import nltk
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Command to start the CoreNLP Server
# java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port 9000 -timeout 15000

# Command to start API
# hypercorn --reload ApiXML.py

# At the first use, download packages:
# nltk.download('punkt')
# nltk.download('averaged_perceptron_tagger')
# nltk.download('wordnet')
# nltk.download('framenet_v17')


def test_create_process_model(input_text: str, file_input=False):
    if file_input:
        file_name = input_text
        input_file = open(file_name, 'r')
        text = input_file.read()
    else:
        text = input_text
    return create_process_model(text)


# pm = test_create_process_model('The manager sends the invitation confirmation. In the meantime, the secretary enters the appointment in the calendar.')
# print(buildXML(pm))
def test_evaluation_set():
    evaluation_directory = '../ProcessDescriptions/Evaluation Set'


    process_descriptions = []
    files = listdir(evaluation_directory)
    files.sort()

    print(files)

    for filename in files:
        file_path = evaluation_directory + '/' + filename
        with open(file_path, "r") as process_description_file:
            data = process_description_file.readlines()
            for i in range(len(data)):
                data[i] = data[i].replace('\n', '')
            process_description = ' '.join(data)
            process_descriptions.append((filename, process_description))


    class ProcessModelInfo:
        def __init__(self, activities, transitions, gateways, swimlanes, xml):
            self.activities = activities
            self.transitions = transitions
            self.gateways = gateways
            self.swimlanes = swimlanes
            self.xml = xml

        def __str__(self):
            return '{A:' + str(self.activities) + ',\n' + 'G:' + str(self.gateways) + ',\n' + 'T:' + str(self.transitions) + ',\n' + 'S:' + str(self.swimlanes) + '}'

        def __repr__(self):
            return '{A:' + str(self.activities) + ',\n' + 'G:' + str(self.gateways) + ',\n' + 'T:' + str(self.transitions) + ',\n' + 'S:' + str(self.swimlanes) + '}'

    def evaluate(swimlanes, gateways):
        # and_gateways = 0
        # or_gateways = 0
        # for gateway in gateways:
        #     if gateway.gateway_type == GatewayType.AND:
        #         and_gateways += 1
        #     if gateway.gateway_type == GatewayType.XOR:
        #         or_gateways += 1
        #
        # return f'|swimlanes|: {len(swimlanes)} |parallel-gateways|: {and_gateways} |exclusive-gateways|: {or_gateways}'

        unknown_actors = 0

        for swimlane in swimlanes:
            if swimlane.actors == ['unknown']:
                unknown_actors = len(swimlane.activities)

        return f'|unknown_actors|: {unknown_actors}'

    results = []

    for description in process_descriptions:
        print(' ----------------> ' + description[0])
        pm = create_process_model(description[1])
        # transitions = len(pm.transitions)
        # gateways = len(pm.gateways)
        # swimlanes = len(pm.swim_lanes)
        # activities = 0
        # for sl in pm.swim_lanes:
        #     activities += len(sl.activities)
        # xml = buildXML(pm)
        results.append((description[0], evaluate(pm.swim_lanes, pm.gateways)))


    print('##############################################')
    print(*results, sep='\n')

# test_evaluation_set()

# Generate Metrics for Evaluation set

def get_amount_sentences():
    sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')

    evaluation_directory = '../ProcessDescriptions/Evaluation Set'
    files = listdir(evaluation_directory)
    files.sort()
    print(files)

    datapoints = []
    datapoints2 = []

    for filename in files:
        file_path = evaluation_directory + '/' + filename
        with open(file_path, "r") as process_description_file:
            data = process_description_file.readlines()
            for i in range(len(data)):
                data[i] = data[i].replace('\n', '')
            process_description = ' '.join(data)



            shortfilename = filename.split(':')[0].split('Description')[1].replace(" ", "")

            sentences = sent_detector.tokenize(process_description.strip())
            amount_sen = len(sentences)
            datapoints.append((shortfilename,amount_sen))
            words = 0
            for sentence in sentences:
                words += len(nltk.word_tokenize(sentence))
            datapoints2.append((shortfilename,words/amount_sen))

    def takeSecond(elem):
        return elem[1]

    plt.xticks(rotation=90)
    datapoints.sort(key=takeSecond)
    plt.ylabel("Number of Sentences")
    d1, d2 = zip(*datapoints)
    plt.bar(d1, d2)
    plt.figure(figsize=(23, 23))
    plt.show()

    plt.xticks(rotation=90)
    datapoints2.sort(key=takeSecond)
    plt.ylabel("Average Sentences Length")
    d1, d2 = zip(*datapoints2)
    plt.bar(d1, d2)
    plt.figure(figsize=(23, 23))
    plt.show()

    return datapoints, datapoints2

def generate_evaluation():
    numb_sen, avg_sen_len =  get_amount_sentences()

    data = pd.read_csv("../Evaluation_metrics.csv")
    print(data.keys())
    matching_activities = data.loc[:,'Matching Activities']
    missing_activities = data.loc[:,'Missing Activities']
    activities = data.loc[:,'Amount Activities']
    desc_names =  data.loc[:,'Unnamed: 0']

    share_matching = []
    share_missing = []

    for i in range(len(activities)-1):

        share_matching.append((desc_names[i], (matching_activities[i]/activities[i])))
        share_missing.append((desc_names[i], (matching_activities[i] / (matching_activities[i]+missing_activities[i]))))

    def takeSecond(elem):
        return elem[1]

    plt.xticks(rotation=90)
    share_matching.sort(key=takeSecond)
    plt.ylabel("Share Matching Activities")
    d1, d2 = zip(*share_matching)
    plt.bar(d1, d2)
    plt.figure(figsize=(23, 23))
    plt.show()

    plt.xticks(rotation=90)
    share_missing.sort(key=takeSecond)
    plt.ylabel("Share Modeled Activities")
    d1, d2 = zip(*share_missing)
    plt.bar(d1, d2)
    plt.figure(figsize=(23, 23))
    plt.show()

    datainfo = dict()
    for element in share_matching:
        datainfo[element[0]] = {'avg_sen_len': 0, 'numb_sen': 0, 'share_matching': element[1], 'share_missing': 0}
    for element in share_missing:
        datainfo[element[0]]['share_missing'] = element[1]
    for element in numb_sen:
        datainfo[element[0]]['numb_sen'] = element[1]
    for element in avg_sen_len:
        datainfo[element[0]]['avg_sen_len'] = element[1]

    ordered_a = []
    ordered_b = []
    ordered_c = []
    ordered_d = []


    for key in datainfo.keys():
        ordered_a.append(datainfo[key]['avg_sen_len'])
        ordered_b.append(datainfo[key]['numb_sen'])
        ordered_c.append(datainfo[key]['share_missing'])
        ordered_d.append(datainfo[key]['share_matching'])

    coef = np.polyfit(ordered_a,ordered_d,1)
    poly1d_fn = np.poly1d(coef)
    print("Average Sentences Length-Share Matching Activities")
    print(np.corrcoef(ordered_a, ordered_d))

    plt.xlabel("Average Sentences Length")
    plt.ylabel("Share Matching Activities")
    plt.plot(ordered_a, ordered_d, 'ro', range(9,27), poly1d_fn(range(9,27)), '--k')
    plt.show()


    coef = np.polyfit(ordered_b,ordered_d,1)
    poly1d_fn = np.poly1d(coef)
    print("Number of Sentences-Share Matching Activities")
    print(np.corrcoef(ordered_b,ordered_d))

    plt.xlabel("Number of Sentences")
    plt.ylabel("Share Matching Activities")
    plt.plot(ordered_b, ordered_d, 'ro', range(4,40), poly1d_fn(range(4,40)), '--k')
    plt.show()

    coef = np.polyfit(ordered_a,ordered_c,1)
    poly1d_fn = np.poly1d(coef)
    print("Average Sentences Length-Share Modeled Activities")
    print(np.corrcoef(ordered_a, ordered_c))

    plt.xlabel("Average Sentences Length")
    plt.ylabel("Share Modeled Activities")
    plt.plot(ordered_a, ordered_c, 'ro', range(9,27), poly1d_fn(range(9,27)), '--k')
    plt.show()


    coef = np.polyfit(ordered_b,ordered_c,1)
    poly1d_fn = np.poly1d(coef)
    print("Number of Sentences-Share Modeled Activities")
    print(np.corrcoef(ordered_b, ordered_c))

    plt.xlabel("Number of Sentences")
    plt.ylabel("Share Modeled Activities")
    plt.plot(ordered_b, ordered_c, 'ro', range(4,40), poly1d_fn(range(4,40)), '--k')
    plt.show()



    coef = np.polyfit(ordered_d,ordered_c,1)
    poly1d_fn = np.poly1d(coef)
    print("Share Matching Activities-Share Modeled Activities")
    print(np.corrcoef(ordered_d, ordered_c))

    plt.xlabel("Share Matching Activities")
    plt.ylabel("Share Modeled Activities")
    plt.plot(ordered_d, ordered_c, 'ro', [0,1], poly1d_fn([0,1]), '--k')
    plt.show()

generate_evaluation()

def generateOverview():
    x = np.arange(len(['Parallel Gateways']))  # the label locations
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width/2, [36], width, label='Our Model')
    rects2 = ax.bar(x + width/2, [24], width, label='Human Model')

    ax.set_ylabel('Number Parallel Gateways')
    ax.set_xticks(x)
    ax.set_xticklabels(['Parallel Gateways'])
    ax.legend()

    ax.bar_label(rects1, padding=3)
    ax.bar_label(rects2, padding=3)

    fig.tight_layout()

    plt.show()

    x = np.arange(len(['Exclusive Gateways']))  # the label locations
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width/2, [184], width, label='Our Model')
    rects2 = ax.bar(x + width/2, [123], width, label='Human Model')

    ax.set_ylabel('Number Exclusive Gateways')
    ax.set_xticks(x)
    ax.set_xticklabels(['Exclusive Gateways'])
    ax.legend()

    ax.bar_label(rects1, padding=3)
    ax.bar_label(rects2, padding=3)

    fig.tight_layout()

    plt.show()

    x = np.arange(len(['Gateways']))  # the label locations
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width, [220], width, label='Our Model')
    rects2 = ax.bar(x, [147], width, label='Human Model')
    rects3 = ax.bar(x + width, [164], width, label="Friedrich's Model")

    ax.set_ylabel('Number Gateways')
    ax.set_xticks(x)
    ax.set_xticklabels(['Gateways'])
    ax.legend()

    ax.bar_label(rects1, padding=3)
    ax.bar_label(rects2, padding=3)
    ax.bar_label(rects3, padding=3)

    fig.tight_layout()

    plt.show()

    x = np.arange(len(['Transitions']))  # the label locations
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width, [968], width, label='Our Model')
    rects2 = ax.bar(x, [1052], width, label='Human Model')
    rects3 = ax.bar(x + width, [1189], width, label="Friedrich's Model")

    ax.set_ylabel('Number Transitions')
    ax.set_xticks(x)
    ax.set_xticklabels(['Transitions'])
    ax.legend()

    ax.bar_label(rects1, padding=3)
    ax.bar_label(rects2, padding=3)
    ax.bar_label(rects3, padding=3)

    fig.tight_layout()

    plt.show()


    x = np.arange(len(['Transitions']))  # the label locations
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width, [968], width, label='Our Model')
    rects2 = ax.bar(x, [1052], width, label='Human Model')
    rects3 = ax.bar(x + width, [1189], width, label="Friedrich's Model")

    ax.set_ylabel('Number Transitions')
    ax.set_xticks(x)
    ax.set_xticklabels(['Transitions'])
    ax.legend()

    ax.bar_label(rects1, padding=3)
    ax.bar_label(rects2, padding=3)
    ax.bar_label(rects3, padding=3)

    fig.tight_layout()

    plt.show()

# Tests if there are any programming errors

# results = []
#
# for description in process_descriptions:
#     try:
#         p = multiprocessing.Process(target=create_process_model, name="CREATE_PROCESS_MODEL", args=(description[1],))
#         p.start()
#
#         # Wait 10 seconds for foo
#         p.join(60)
#
#         # Terminate foo
#         if p.is_alive():
#             results.append('ERROR (After 60 seconds not finished): ' + description[0])
#             p.terminate()
#             p.join()
#         else:
#             results.append(description[0] + ' SUCCESS')
#     except:
#         results.append('ERROR (Implementation): ' + description[0])
#
# print('##############################################')
# print(results)
