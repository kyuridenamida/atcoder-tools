import * as React from "react";
import {Col, Button, Row, TabContent, Table} from "reactstrap";
import Code from "./Code";
import QualityResult from "../../../models/QualityResult";
import ProblemLink from "./ProblemLink";
import Scrollable from "../../../common/Scrollable";
import Language from "../../../models/Language";
import LanguageTabs from '../../../common/LanguageTabs';
import {judgeMethodToText} from "../../../models/JudgeMethod";

interface ComponentProps {
    qualityResult: QualityResult
}


export default class Detail extends React.Component<ComponentProps, { activeLanguage: Language }> {
    constructor(props) {
        super(props);

        this.toggle = this.toggle.bind(this);
        this.state = {
            activeLanguage: 'cpp'
        };
    }

    toggle(language: Language) {
        if (this.state.activeLanguage !== language) {
            this.setState({
                activeLanguage: language
            });
        }
    }

    renderLabel = (text: string, active: boolean) => {
        if (active) {
            return text;
        } else {
            return <span style={{color: "lightgray"}}>{text}</span>;
        }
    };

    createReportUrl = () => {
        const problemId = this.props.qualityResult.problem.problem_id;
        const body = `問題 ${problemId} におけるコード生成結果が正しくないようです。 (↓以下に詳細を書く)`;
        return `https://github.com/kyuridenamida/atcoder-tools/issues/new?title=Wrong code generation on ${problemId}&body=${body}&assignee=kyuridenamida&labels=generator%20bug`;
    };

    render() {
        const {qualityResult} = this.props;

        const errorTableContents = [
            ["Statement Parsing", qualityResult.statement_parse.error],
            ["Format Prediction", qualityResult.format_prediction.error],
            ["MOD", qualityResult.modulo.error],
            ["NO", qualityResult.no_str.error],
            ["YES", qualityResult.yes_str.error],
            ["JUDGE", qualityResult.judge_method.error],

        ].map(([text, error]: [string, string | null]) => {
            if (error === null) {
                return null;
            }
            return <tr key={text}>
                <th scope="row">{this.renderLabel(text, error !== null)}</th>
                <td>{error || ""}</td>
            </tr>
        }).filter(tag => tag !== null);


        return <div>
            <h3 style={{display: 'inline-block'}}>{qualityResult.problem.problem_id}</h3>
            {' '}
            <ProblemLink contest_id={qualityResult.problem.contest.contest_id}
                         problem_id={qualityResult.problem.problem_id}>[問題文]
            </ProblemLink>
            <hr/>
            <h3>自動生成コード</h3>
            <div>
                <LanguageTabs onLanguageSelected={this.toggle} activeLanguage={this.state.activeLanguage}/>
                <TabContent activeTab={this.state.activeLanguage}>
                    <Row>
                        <Col sm={12}>
                            <Scrollable height={400}>
                                <Code
                                    code={qualityResult.codes[this.state.activeLanguage] || ""}
                                    language={this.state.activeLanguage}
                                />
                            </Scrollable>
                        </Col>
                    </Row>
                </TabContent>
            </div>
            <h3>定数</h3>
            <Table>
                <tbody>
                {
                    [
                        ["MOD", qualityResult.modulo.value],
                        ["NO", qualityResult.no_str.value],
                        ["YES", qualityResult.yes_str.value],
                        ["JUDGE METHOD", qualityResult.judge_method.value ? judgeMethodToText(qualityResult.judge_method.value) : null],
                    ].map(([text, value]: [string, string | null]) => {
                        return <tr key={text}>
                            <th scope="row">{this.renderLabel(text, value !== null)}</th>
                            <td>{value || ""}</td>
                        </tr>
                    })
                }
                </tbody>
            </Table>
            {errorTableContents.length > 0 &&
            <div>
                <h3>エラー</h3>
                <Table>
                    <tbody>
                    {errorTableContents}
                    </tbody>
                </Table>
            </div>
            }

            <hr/>
            <Button color="danger" target="_blank" size="sm" href={this.createReportUrl()}>不具合を報告する</Button>

        </div>
    }
};
