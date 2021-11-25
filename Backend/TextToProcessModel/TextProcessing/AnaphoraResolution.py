import spacy
import neuralcoref


# Neuralcoref for anaphora resolution, gets a text and returns a text with resolved dependencies.
def get_resolved_text(text: str) -> str:
    nlp = spacy.load('en_core_web_md')  # load the model
    neuralcoref.add_to_pipe(nlp)

    doc = nlp(text)

    to_replace = []
    for cluster in doc._.coref_clusters:
        for mention in cluster.mentions:
            if mention.text.lower() in ['it', 'they', 'he', 'she', 'its']:
                to_replace.append((mention.start, mention.end, cluster.main.text))
                print(f'replaced ||{mention.text}|| with ||{cluster.main.text}||')

    new_text = []
    for t in doc:
        new_text.append(t.text)
    for replace in to_replace:
        new_text[replace[0]] = replace[2]
        for index in range(replace[1] - replace[0] - 1):
            new_text[replace[0] + index + 1] = ''

    end_text = ''
    for word in new_text:
        if not word == '':
            end_text = end_text + ' ' + word

    return end_text
    # return doc._.coref_resolved
