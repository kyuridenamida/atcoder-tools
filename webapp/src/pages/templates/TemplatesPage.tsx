import * as React from 'react';
import {Row, Col} from 'reactstrap';
import TemplateItem from "./TemplateItem";
import LanguageTabs from "../../common/LanguageTabs";
import Language from "../../models/Language";
import MarkDownView from "../../common/MarkDownView";

const loadReadmeTemplateSection = async () => {
    const readmePath = require("../../auto_generated/README_TEMPLATE_SECTION.md");
    const response = await fetch(readmePath);
    return response.text()
};


class TemplatesPage extends React.Component<{}, { activeLanguage: Language }>{
    constructor(props) {
        super(props);
        this.state = {
            activeLanguage: 'cpp'
        };
    }
    public render() {
        return <React.Fragment>
            <Row>
                <Col sm={6}>
                    <h3>テンプレートの仕様</h3>
                    <p>問題文から自動生成された入力部分・抽出された定数はテンプレートを通じて利用することができます。テンプレートエンジンには jinja2 を使っています。</p>

                    <MarkDownView loadMarkDown={loadReadmeTemplateSection}/>
                    <p>いくつかの言語については標準テンプレートを用意していますが、ユーザー独自のものを使用することもできます。</p>
                    <p>また、テンプレートに渡す引数を生成するコードジェネレーターに関しても、入力部の中間表現からコードへの変換モジュールを定義すればユーザー独自のものを使用することができます。</p>
                </Col>


                <Col sm={6}>
                    <h3>各言語毎のデフォルトテンプレート / コードジェネレーター</h3>
                    <LanguageTabs activeLanguage={this.state.activeLanguage}
                                  onLanguageSelected={
                                      (language: Language) => this.setState({activeLanguage: language})
                                  }/>
                    <TemplateItem language={this.state.activeLanguage} />
                </Col>

            </Row>
        </React.Fragment>;
    }
}

export default TemplatesPage;
