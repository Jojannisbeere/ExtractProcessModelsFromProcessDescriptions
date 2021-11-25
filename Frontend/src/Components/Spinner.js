import './Spinner.css'
import {useText2model} from "../text-2-model";

export const Spinner = () => {
    const{loadingModel} = useText2model()
    if(loadingModel){
        return <div className='spinner'></div>
    }
    else{
        return <div></div>
    }
}