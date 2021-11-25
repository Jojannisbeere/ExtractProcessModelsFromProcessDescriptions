import {useText2model} from "../text-2-model";
import React, {useEffect, useRef, useState} from "react";
import './CreateBPMN.css'
import Modeler from "bpmn-js/lib/Modeler";
import "bpmn-js/dist/assets/diagram-js.css";
import "bpmn-js/dist/assets/bpmn-font/css/bpmn-embedded.css";
import "bpmn-js-properties-panel/dist/assets/bpmn-js-properties-panel.css";

var setupDone = false
var viewer = null

export const CreateBPMN = () => {
    const {xmlFile, loadDisplayedModel, setDisplayedModel, setLoadDisplayedModel} = useText2model()
    const [model, setModel] = useState('')

    const containerRef = useRef()

    useEffect(async () => {
            if (xmlFile !== undefined) {
                console.log(setupDone)
                if (!setupDone) {
                    viewer = new Modeler({
                        container: containerRef.current,
                        height: 600,
                    })
                    setupDone = true
                }
                await viewer.importXML(xmlFile)
                viewer.get('canvas').zoom('fit-viewport')
                const viewbox = viewer.get('canvas').viewbox()
                viewbox.x = -250
                viewer.get('canvas').viewbox(viewbox)
                setModel('')
            }
        }, [xmlFile]
    )

    useEffect( async () => {
        if(viewer && loadDisplayedModel){
            const displayedModelXML = await viewer.saveXML({ format: true })
            setDisplayedModel(displayedModelXML.xml)
            setLoadDisplayedModel(false)
        }
        setLoadDisplayedModel(false)
        }, [loadDisplayedModel]
    )

    return <div className="bpmn-diagram-container" ref={containerRef}/>
}