import * as React from "react";
import {Col, Nav, Button, NavItem, NavLink, Row, TabContent, Table, TabPane} from "reactstrap";
import classNames from 'classnames';
import Code from "./Code";
import QualityResult from "../../../models/QualityResult";
import ProblemLink from "./ProblemLink";

interface ComponentProps {
    qualityResult: QualityResult
}

export default class Detail extends React.Component<ComponentProps, { activeTab: string }> {
    constructor(props) {
        super(props);

        this.toggle = this.toggle.bind(this);
        this.state = {
            activeTab: '1'
        };
    }

    toggle(tab) {
        if (this.state.activeTab !== tab) {
            this.setState({
                activeTab: tab
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
        ].map(([text, error]: [string, string | null]) => {
            if (error === null) return null;
            return <tr>
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
                <Nav tabs>
                    <NavItem>
                        <NavLink
                            className={classNames({active: this.state.activeTab === 'cpp'})}
                            onClick={() => {
                                this.toggle('cpp');
                            }}
                        >
                            C++
                        </NavLink>
                    </NavItem>
                    <NavItem>
                        <NavLink
                            className={classNames({active: this.state.activeTab === 'java'})}
                            onClick={() => {
                                this.toggle('java');
                            }}
                        >
                            Java
                        </NavLink>
                    </NavItem>
                    <NavItem>
                        <NavLink
                            className={classNames({active: this.state.activeTab === 'rust'})}
                            onClick={() => {
                                this.toggle('rust');
                            }}
                        >
                            Rust
                        </NavLink>
                    </NavItem>
                </Nav>
                <TabContent activeTab={this.state.activeTab}>
                    <TabPane tabId={1}>
                        <Row>
                            <Col sm={12}>
                                <Code code={qualityResult.codes.cpp || ""}/>
                            </Col>
                        </Row>
                    </TabPane>
                    <TabPane tabId={2}>
                        <Row>
                            <Col sm={12}>
                                <Code code={qualityResult.codes.cpp || ""}/>
                            </Col>
                        </Row>
                    </TabPane>
                </TabContent>
            </div>
            <Code code={qualityResult.codes.cpp || ""}/>
            <h3>定数</h3>
            <Table>
                <tbody>
                {
                    [
                        ["MOD", qualityResult.modulo.value],
                        ["NO", qualityResult.no_str.value],
                        ["YES", qualityResult.yes_str.value],
                    ].map(([text, value]: [string, string | null]) => {
                        return <tr>
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
