import './PopupContent.css'
import {useText2model} from "../text-2-model";

export const PopupContent = (props) => {
    const {setTestModel} = useText2model()

    const loadTestData = async (identifier) => {
        await setTestModel(identifier)
        props.closeLinker.current.close()
    }

    return (
        <div>
            <h1>Load One of the Test Process Descriptions</h1>
            <table className={'button_table'}>
                <tbody>
                    <tr>
                        <td className={'example_button'} onClick={() => loadTestData('1-1')}>1-1</td>
                        <td className={'example_button'} onClick={() => loadTestData('1-2')}>1-2</td>
                        <td className={'example_button'} onClick={() => loadTestData('1-3')}>1-3</td>
                        <td className={'example_button'} onClick={() => loadTestData('1-4')}>1-4</td>
                        <td className={'example_button'} onClick={() => loadTestData('2-1')}>2-1</td>
                        <td className={'example_button'} onClick={() => loadTestData('2-2')}>2-2</td>
                        <td className={'example_button'} onClick={() => loadTestData('3-1')}>3-1</td>
                        <td className={'example_button'} onClick={() => loadTestData('3-2')}>3-2</td>
                    </tr>
                    <tr>
                        <td className={'example_button'} onClick={() => loadTestData('3-3')}>3-3</td>
                        <td className={'example_button'} onClick={() => loadTestData('3-4')}>3-4</td>
                        <td className={'example_button'} onClick={() => loadTestData('3-5')}>3-5</td>
                        <td className={'example_button'} onClick={() => loadTestData('3-6')}>3-6</td>
                        <td className={'example_button'} onClick={() => loadTestData('3-7')}>3-7</td>
                        <td className={'example_button'} onClick={() => loadTestData('3-8')}>3-8</td>
                        <td className={'example_button'} onClick={() => loadTestData('4-1')}>4-1</td>
                        <td className={'example_button'} onClick={() => loadTestData('5-1')}>5-1</td>
                    </tr>
                    <tr>
                        <td className={'example_button'} onClick={() => loadTestData('5-2')}>5-2</td>
                        <td className={'example_button'} onClick={() => loadTestData('5-3')}>5-3</td>
                        <td className={'example_button'} onClick={() => loadTestData('5-4')}>5-4</td>
                        <td className={'example_button'} onClick={() => loadTestData('6-1')}>6-1</td>
                        <td className={'example_button'} onClick={() => loadTestData('6-2')}>6-2</td>
                        <td className={'example_button'} onClick={() => loadTestData('6-3')}>6-3</td>
                        <td className={'example_button'} onClick={() => loadTestData('6-4')}>6-4</td>
                        <td className={'example_button'} onClick={() => loadTestData('7-1')}>7-1</td>
                    </tr>
                    <tr>
                        <td className={'example_button'} onClick={() => loadTestData('8-1')}>8-1</td>
                        <td className={'example_button'} onClick={() => loadTestData('8-2')}>8-2</td>
                        <td className={'example_button'} onClick={() => loadTestData('8-3')}>8-3</td>
                        <td className={'example_button'} onClick={() => loadTestData('9-1')}>9-1</td>
                        <td className={'example_button'} onClick={() => loadTestData('9-2')}>9-2</td>
                        <td className={'example_button'} onClick={() => loadTestData('9-3')}>9-3</td>
                        <td className={'example_button'} onClick={() => loadTestData('9-4')}>9-4</td>
                        <td className={'example_button'} onClick={() => loadTestData('9-5')}>9-5</td>
                    </tr>
                    <tr>
                        <td className={'example_button'} onClick={() => loadTestData('9-6')}>9-6</td>
                        <td className={'example_button'} onClick={() => loadTestData('10-1')}>10-1</td>
                        <td className={'example_button'} onClick={() => loadTestData('10-2')}>10-2</td>
                        <td className={'example_button'} onClick={() => loadTestData('10-3')}>10-3</td>
                        <td className={'example_button'} onClick={() => loadTestData('10-4')}>10-4</td>
                        <td className={'example_button'} onClick={() => loadTestData('10-5')}>10-5</td>
                        <td className={'example_button'} onClick={() => loadTestData('10-6')}>10-6</td>
                        <td className={'example_button'} onClick={() => loadTestData('10-7')}>10-7</td>
                    </tr>
                    <tr>
                        <td className={'example_button'} onClick={() => loadTestData('10-8')}>10-8</td>
                        <td className={'example_button'} onClick={() => loadTestData('10-9')}>10-9</td>
                        <td className={'example_button'} onClick={() => loadTestData('10-10')}>10-10</td>
                        <td className={'example_button'} onClick={() => loadTestData('10-11')}>10-11</td>
                        <td className={'example_button'} onClick={() => loadTestData('10-12')}>10-12</td>
                        <td className={'example_button'} onClick={() => loadTestData('10-13')}>10-13</td>
                        <td className={'example_button'} onClick={() => loadTestData('10-14')}>10-14</td>
                    </tr>
                </tbody>
            </table>
        </div>
    )
}