import * as React from 'react';
import {Col} from 'reactstrap';
import Language from "../../models/Language";
import templateData from 'src/auto_generated/templateData.js';
import Code from "../quality/summary/Code";
import Scrollable from "../../common/Scrollable";

interface ComponentProps {
    language: Language,
}

class TemplateItem extends React.Component<ComponentProps> {
    public render() {
        return <Col sm={12}>
            <h5>テンプレート</h5>
            <Scrollable height={500}>
                <Code code={templateData[this.props.language].template} language={this.props.language}/>
            </Scrollable>
            <h5 style={{display: 'inline-block'}}>コードジェネレーター</h5>
            {' '}
            <a href={templateData[this.props.language].generator_url} target="_blank">[GitHub]</a>
            <Scrollable height={500}>
                <Code code={templateData[this.props.language].generator} language="python"/>
            </Scrollable>
        </Col>
    }
}

export default TemplateItem;
