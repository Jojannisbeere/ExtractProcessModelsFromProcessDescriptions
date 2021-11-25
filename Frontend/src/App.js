import './App.css'
import React, {useEffect, useRef} from "react"
import {Text2ModelProvider, useText2model} from './text-2-model'
import {CreateBPMN} from "./Components/CreateBPMN"
import {BsClipboardData, BsDownload, BsFileEarmarkArrowDown, BsFileText} from 'react-icons/bs'
import {Spinner} from "./Components/Spinner";
import Popup from 'reactjs-popup';
import {PopupContent} from "./Components/PopupContent";

function App() {

    const ref = useRef();

    return (
        <div className="App">
            <Heading/>
            <Text2ModelProvider>
                <InputProcessModelDescription opendLinker={ref}/>
                <Spinner/>
                <DownloadButton/>
                <CreateBPMN/>
                <Popup ref={ref} modal nested>
                    <PopupContent closeLinker={ref}/>
                </Popup>
            </Text2ModelProvider>

        </div>

    );
}


const Heading = () => {
    return (
        <div className='heading'>
            <h1> Create your own <span className='bigtext'> PROCESS MODEL </span> from your <span className='bigtext'> TEXTUAL DESCRIPTION </span>.
            </h1>
        </div>

    )
}


const InputProcessModelDescription = (props) => {

    const {setText, text, setLoadingModel, value, setValue, loadingModel} = useText2model()

    const [focussed, setFocussed] = React.useState(false)
    const [height, setHeight] = React.useState({height: 100})
    const [pdHeight, setPdHeight] = React.useState({height: 100})

    const label = 'Process Model Description'
    const id = 1

    const textAreaRef = useRef()

    const fieldClassName = `field ${(focussed || value) && "focussed"}`;

    useEffect( () => {
            if(loadingModel){
                textAreaRef.current.style.cssText = 'height:auto; padding:0'
                textAreaRef.current.style.cssText = 'height:' + textAreaRef.current.scrollHeight + 'px'
                setHeight({height: textAreaRef.current.scrollHeight + 65})
                setPdHeight({height: textAreaRef.current.scrollHeight + 65})
            }
        }, [loadingModel]
    )

    const updateTextAreaHeight = () => {
        textAreaRef.current.style.cssText = 'height:auto; padding:0'
        textAreaRef.current.style.cssText = 'height:' + textAreaRef.current.scrollHeight + 'px'
        setHeight({height: textAreaRef.current.scrollHeight})
    }

    const inputFile = useRef(null)

    const onButtonClick = () => {
        inputFile.current.click()
    }

    const handleFileUpload = e => {
        const {files} = e.target;
        if (files && files.length) {
            // const filename = files[0].name;
            const fr = new FileReader()
            fr.onload = () => {
                setValue(fr.result)
                updateTextAreaHeight()
            }
            fr.readAsText(files[0])
        }
    }

    const downloadFile = useRef(null)

    const download = (text, name) => {
        const file = new Blob([text], {type: 'text/plain'});
        downloadFile.current.href = URL.createObjectURL(file);
        downloadFile.current.download = name;
        downloadFile.current.click()
    }

    return (
        <div>
            <table className='buttonrow'>
                <tbody>
                <tr>
                    <td>
                        <button
                            title={'Test some Process Descriptions'}
                            className='filebutton'
                            onClick={() => props.opendLinker.current.open()}
                        >
                            <BsClipboardData
                                color='#fff'
                                size={37}
                            />
                        </button>
                    </td>
                    <td>
                        <input
                            style={{display: "none"}}
                            ref={inputFile}
                            type="file"
                            accept='.txt'
                            onChange={handleFileUpload}
                        />
                        <button
                            title={'Upload .txt with Process Description'}
                            className='filebutton'
                            onClick={() => onButtonClick()}
                        >
                            <BsFileText
                                color='#fff'
                                size={40}
                            />
                        </button>
                    </td>
                    <td>
                        <a
                            href=''
                            style={{display: 'none'}}
                            ref={downloadFile}
                        />
                        <button
                            title={'Download Process Description as .txt'}
                            className='filebutton'
                            onClick={() => {
                                let fileName = prompt('Please Enter a Name for your File')
                                if (fileName !== null) {
                                    if (fileName === '') {
                                        fileName = 'process_description'
                                    }
                                    download(text, fileName + '.txt')
                                }

                            }}
                        >
                            <BsFileEarmarkArrowDown
                                color='#fff'
                                size={40}
                            />
                        </button>
                    </td>
                </tr>
                </tbody>
            </table>

            <div className={fieldClassName} style={height}>
                <textarea
                    id={id}
                    ref={textAreaRef}
                    value={value}
                    placeholder={label}
                    onChange={(event) => {
                        setValue(event.target.value)
                        updateTextAreaHeight()
                    }}
                    onFocus={() => setFocussed(true)}
                    onBlur={() => setFocussed(false)}
                />
                <label htmlFor={id}>
                    {label}
                </label>
            </div>
            <button
                type="button"
                className='generatebutton'
                onClick={() => {
                    setText(value)
                    setLoadingModel(true)
                }}
            >
                Generate Process Model
            </button>
            <br/>
            <ProcessDescriptionField text={text} height={pdHeight}/>
        </div>
    )
}

export default App;

const ProcessDescriptionField = (props) => {

    const process_description = props.text
    const height = props.height

    return (
        <div className='descbox' style={height}>
            <textarea
                id={2}
                style={height}
                value={process_description}
                disabled="disabled"
            />
            <label htmlFor={2}>
                {'Your Process Description'}
            </label>
        </div>
    )
}

const DownloadButton = () => {

    const {setLoadDisplayedModel, displayedModel, xmlFile} = useText2model()

    const downloadFile = useRef(null)

    const download = (text, name) => {
        const file = new Blob([text], {type: 'text/plain'});
        downloadFile.current.href = URL.createObjectURL(file);
        downloadFile.current.download = name;
        downloadFile.current.click()
    }

    var fileName = 'test'

    useEffect( async () => {
            if(displayedModel){
                fileName = prompt('Please Enter a Name for your File')
                if (fileName !== null) {
                    if (fileName === '') {
                        fileName = 'process_model'
                    }
                    console.log('DOWNLOAD:')
                    console.log(displayedModel)
                    download(displayedModel, fileName + '.xml')
                }
            }
        }, [displayedModel]
    )

    if(xmlFile){
        return (
            <div className='downloadmodelbutton'>
                <a
                    href=''
                    style={{display: 'none'}}
                    ref={downloadFile}
                />
                <button
                    title={'Download the Process Model'}
                    className='filebutton'
                    onClick={() => setLoadDisplayedModel(true)}
                >
                    <BsDownload
                        color='#fff'
                        size={40}
                    />
                </button>
            </div>
        )
    }
    else{
        return( <div/>)
    }
}
