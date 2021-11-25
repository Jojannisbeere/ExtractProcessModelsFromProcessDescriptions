# How to run the backend
Install all required packages.

Clone neuralcoref package into the folder (https://github.com/huggingface/neuralcoref).
The normal installation of the package over pip did not work for me.

The stanford-corenlp server have to be downloaded manually too (https://stanfordnlp.github.io/CoreNLP/).

To start the api for the frontend run:

hypercorn ApiXML.py

To start the stanford-corenlp server run this command in the root folder:
 
java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port 9000 -timeout 15000
