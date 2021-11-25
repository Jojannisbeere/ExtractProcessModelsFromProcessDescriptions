from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from ProcessModelToBPMN.ConverterBPMN import buildXML
from TextProcessing import TextToProcessModel as ttpm
from os import listdir
from fastapi.responses import PlainTextResponse

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/getProcessModel/{process_description}')
def get_legacy_data(process_description: str):
    pm = ttpm.create_process_model(process_description)
    data = buildXML(pm)
    print('SENDING XML')
    return Response(content=data, media_type="application/xml")


@app.get('/test/{identifier}', response_class=PlainTextResponse)
def get_legacy_data(identifier: str):

    evaluation_directory = '../ProcessDescriptions/Evaluation Set'

    files = listdir(evaluation_directory)
    process_description = ''

    for filename in files:
        if identifier + ':' in filename:
            file_path = evaluation_directory + '/' + filename
            with open(file_path, "r") as process_description_file:
                data = process_description_file.readlines()
                for i in range(len(data)):
                    data[i] = data[i].replace('\n', '')
                process_description = ' '.join(data)

    return process_description
