import React, {useEffect, useState} from "react";
import AutoLayout from 'bpmn-auto-layout'

const autoLayout = new AutoLayout()

const Text2model = React.createContext()

export const Text2ModelProvider = ({ children }) => {
    const text2model = useProvideText2model()

    return (
        <Text2model.Provider value={text2model}>
            {children}
        </Text2model.Provider>)
}

export const useText2model = () => {
    return React.useContext(Text2model)
}

const useProvideText2model = () => {
    const [text, setText] = useState('')
    const [xmlFile, setXmlFile] = useState()
    const [loadingModel, setLoadingModel] = useState(false)
    const [displayedModel, setDisplayedModel] = useState('')
    const [loadDisplayedModel, setLoadDisplayedModel] = useState(false)
    const [value, setValue] = React.useState('')
    const [testTestProcessModel, setTestTestProcessModel] = React.useState(false)

    useEffect(async () => {
        if(text !== '' && loadingModel) {
            await fetchText2Model()
        }
        else{
            setLoadingModel(false)
        }
        }, [loadingModel]
    )

    useEffect(() => {
        if(testTestProcessModel){
            setText(value)
            setLoadingModel(true)
            setTestTestProcessModel(false)
        }
        }, [testTestProcessModel]
    )

    const fetchText2Model = async () => {
        console.log(text)
        let url = "http://127.0.0.1:8000/getProcessModel/" + text
        try {
            let res = await fetch(url, {
                method: 'GET',
            })
            if (res.ok) {
                const processModelXML = await res.text()
                const layoutedProcessModelXML = await autoLayout.layoutProcess(processModelXML)
                console.log(layoutedProcessModelXML)
                setXmlFile(layoutedProcessModelXML)
            }
            else{
                console.log(res)
            }
            setLoadingModel(false)
        }
        catch (e) {
            console.log(e)
            setLoadingModel(false)
        }
    }

    const setTestModel = async (identifier) => {
        let url = "http://127.0.0.1:8000/test/" + identifier
        try {
            let res = await fetch(url, {
                method: 'GET',
            })
            if (res.ok) {
                const processDescription = await res.text()
                console.log(processDescription)
                setValue(processDescription)
                setTestTestProcessModel(true)
            }
            else{
                console.log(res)
            }
        }
        catch (e) {
            console.log(e)
        }
    }

    return  {
        setTestModel,
        value,
        setValue,
        text,
        setText,
        xmlFile,
        setXmlFile,
        loadingModel,
        setLoadingModel,
        fetchText2Model,
        displayedModel,
        setDisplayedModel,
        loadDisplayedModel,
        setLoadDisplayedModel
    }
}