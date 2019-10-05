import * as React from 'react';
import {Col, Input, Label, Row, Table} from 'reactstrap';
import ReactTable from 'react-table'
import qualityResultList from "../../../auto_generated/qualityResultList.js"
import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";
import QualityResult from "../../../models/QualityResult";
import "./Summary.scss";
import Detail from "./Detail";
import ProblemLink from "./ProblemLink";
import Scrollable from "../../../common/Scrollable";
import qualityResultDefinition from 'src/auto_generated/qualityResultDefinition.js';
import Hidable from "../../../common/Hidable";
import Code from "./Code";
import {judgeMethodToText} from "../../../models/JudgeMethod";


const filteredQualityResultList = (filterMethod) => {
    return qualityResultList.filter(filterMethod);
};


const isSomethingBad = (r) => r.statement_parse.error || r.format_prediction.error;

const getAccuracyData = (contestNameRe: string) => {
    const contestFilter = (r) => r.contest.contest_id.match(contestNameRe);
    const allContestCount = filteredQualityResultList(contestFilter).length;
    const correctContestCount = filteredQualityResultList((r) => !isSomethingBad(r) && contestFilter(r)).length;
    return [allContestCount, correctContestCount]
};

const [allRegularContestCount, correctRegularContestCount] = getAccuracyData("(abc|arc|agc)");
const [allAGC, correctAGC] = getAccuracyData("^agc");
const [allARC, correctARC] = getAccuracyData("^arc");
const [allABC, correctABC] = getAccuracyData("^abc");

export default class Summary extends React.Component<{}, {
    showingCode: boolean,
    detailedSearchMode: boolean,
    analysisMode: boolean,
    activeQualityResult: QualityResult | null,
    analysisQuery: string,
}> {
    constructor(props: any) {
        super(props);
        this.state = {
            activeQualityResult: null,
            detailedSearchMode: false,
            analysisMode: false,
            showingCode: false,
            analysisQuery: 'r.contest.contest_id.match("(abc|agc|arc)")',
        }
    }

    updateActiveProblem = (qualityResult: QualityResult) => {
        this.setState({
            activeQualityResult: qualityResult,
            showingCode: true,
        });
    };

    isActive = (problemId: string) => {
        return this.state.activeQualityResult && problemId === this.state.activeQualityResult.problem.problem_id
    };

    onQueryUpdated = (query: string) => {
        this.setState({analysisQuery: query});
    };

    render() {
        const {detailedSearchMode} = this.state;

        const renderValueOrError = ({value}, withOkMark = true, renderingJudgeMethod = false) => {
            if (value.error) {
                if( value.error === "Skipped"){
                    return <span>
                        <FontAwesomeIcon icon="minus" color="lightgray"/>
                        {' '}
                        <span style={{color: 'lightgray'}}>Skipped</span>
                        </span>;
                }
                return <span>

                    {value.error !== "Skipped" && <FontAwesomeIcon icon="times" color="red"/>}
                    {' '}
                    {value.error}
                    </span>
            }
            return <span>
                {withOkMark && <FontAwesomeIcon icon="check" color="green"/>}
                {' '}
                {renderingJudgeMethod ?
                    (value.value ? judgeMethodToText(value.value) : "")
                    : (value.value || "")
                }
                </span>
        };
        const renderValueOrErrorWithoutOkMark = (props) => renderValueOrError(props, false);
        const renderValueOrErrorWithoutOkMarkForJudgeMethod = (props) => renderValueOrError(props, false, true);

        const columns = [
            {
                Header: 'Problem Data',
                columns: [
                    {
                        Header: 'Contest',
                        accessor: 'contest.contest_id',
                        Cell: ({value}) => <a target="_blank" href={`https://atcoder.jp/contests/${value}`}>{value}</a>
                    }, {
                        Header: 'Problem',
                        accessor: 'problem.problem_id',
                        Cell: ({original, value}) =>
                            <ProblemLink contest_id={original.contest.contest_id} problem_id={value}>{value}</ProblemLink>
                    }
                ]
            },
            {
                Header: 'Input Analysis',
                columns:
                    [{
                        show: detailedSearchMode,
                        Header: 'Statement Parsing',
                        accessor: 'statement_parse',
                        Cell: renderValueOrError,
                        sortMethod: this.sortForErrorAndValue,
                    }, {
                        show: detailedSearchMode,
                        Header: 'Format Pred.',
                        accessor: 'format_prediction',
                        Cell: renderValueOrError,
                        sortMethod: this.sortForErrorAndValue,
                    }]
            }, {
                Header: 'Constants Prediction',
                columns: [
                    {
                        show: detailedSearchMode,
                        Header: 'MOD',
                        accessor: 'modulo',
                        Cell: renderValueOrErrorWithoutOkMark,
                        sortMethod: this.sortForErrorAndValue,
                    }, {
                        show: detailedSearchMode,
                        Header: 'YES',
                        accessor: 'yes_str',
                        Cell: renderValueOrErrorWithoutOkMark,
                        sortMethod: this.sortForErrorAndValue,
                    }, {
                        show: detailedSearchMode,
                        Header: 'NO',
                        accessor: 'no_str',
                        Cell: renderValueOrErrorWithoutOkMark,
                        sortMethod: this.sortForErrorAndValue,
                    }, {
                        show: detailedSearchMode,
                        Header: 'JUDGE METHOD',
                        accessor: 'judge_method',
                        Cell: renderValueOrErrorWithoutOkMarkForJudgeMethod,
                        sortMethod: this.sortForErrorAndValueForJudgeMethod,
                    },
                ]
            }];

        const defaultFilterMethod = (filter, row, column) => {
            const id = filter.pivotId || filter.id;
            try {
                return row[id] !== undefined ? this.getCellText(column, row[id]).match(filter.value) !== null : true;

            } catch (e) {
                return false;
            }
        };

        const analysisFilterMethod = (r) => {
            return eval(this.state.analysisQuery);
        };

        let failedToParse = false;

        let resultsForTable;
        if (this.state.analysisMode && this.state.analysisQuery.length > 0) {
            try {
                resultsForTable = filteredQualityResultList(analysisFilterMethod);
            } catch {
                resultsForTable = qualityResultList;
                failedToParse = true;
            }
        } else {
            resultsForTable = qualityResultList;
        }


        return <React.Fragment>
            <Row>
                <Col sm={12}>
                    <Row>
                        <Col sm={6}>
                            <Hidable
                                showButtonText={"入力フォーマット解析成功率を表示"}
                                hideButtonText={"入力フォーマット解析成功率を隠す"}
                                visibleByDefault
                            >
                                <h3 style={{display: "inline-block"}}>入力フォーマット解析成功率</h3>
                                <Table>
                                    <tbody>
                                    {
                                        [
                                            ["AGC", correctAGC, allAGC],
                                            ["ARC", correctARC, allARC],
                                            ["ABC", correctABC, allABC],
                                            ["レギュラーコンテスト全体(AGC,ABC,ARC)", correctRegularContestCount, allRegularContestCount],
                                        ].map(([text, correct, all]: [string, number, number]) => {
                                            return <tr key={text}>
                                                <th scope="row">{text}</th>
                                                <td> {correct} / {all} </td>
                                                <td>{Math.round(100 * correct / all)} %</td>
                                            </tr>
                                        })
                                    }
                                    </tbody>
                                </Table>
                            </Hidable>

                        </Col>
                    </Row>
                </Col>
                <Col sm={12}>
                    <h3>各問題毎の解析結果</h3>
                </Col>
                <Col sm={1}>
                    <Label>
                        <Input type="checkbox" checked={this.state.detailedSearchMode}
                               onChange={() => this.setState({detailedSearchMode: !this.state.detailedSearchMode})}/>
                        詳細検索モード
                    </Label>
                </Col>
                <Col sm={11}>
                    <Label>
                        <Input type="checkbox" checked={this.state.analysisMode}
                               onChange={() => {
                                   this.setState({analysisMode: !this.state.analysisMode})
                               }}/>
                        解析モード (開発者向け)
                    </Label>
                </Col>
                {this.state.analysisMode && <Col sm={6}>
                    <Hidable
                        showButtonText={"QualityResultの定義を表示"}
                        hideButtonText={"QualityResultの定義を隠す"}
                    >
                        <Scrollable height={300}>
                            <Code code={qualityResultDefinition} language={"typescript"}/>
                        </Scrollable>
                    </Hidable>
                    function filter(r: QualityResult) => {"{ return "}
                    <Input style={{display: "inline-block"}}
                           value={this.state.analysisQuery}
                           onChange={(e) => this.onQueryUpdated(e.target.value)}
                           placeholder={"javascript condition expression"}
                           invalid={failedToParse}
                    />
                    {"; }"}
                    <p> {resultsForTable.length} 件マッチしました。</p>
                </Col>}
            </Row>
            <Row className="page-content">
                <Col sm={this.state.detailedSearchMode ? 12 : 6}>
                    <ReactTable
                        filterable
                        data={resultsForTable}
                        columns={columns}
                        defaultFilterMethod={defaultFilterMethod}
                        pageSize={20}
                        style={{
                            height: "100%",
                            maxHeight: "1000px"
                        }}
                        getTrProps={(state, rowInfo) => {
                            if (!rowInfo || !rowInfo.hasOwnProperty("original")) {
                                return {};
                            }

                            const original: QualityResult = rowInfo.original;
                            return {
                                onClick: () => this.updateActiveProblem(original),
                                className: this.isActive(original.problem.problem_id) ? "selected" : ""
                            }
                        }}
                    />
                </Col>
                {!this.state.detailedSearchMode && this.state.activeQualityResult &&
                <Col sm={6}>
                    <Scrollable height={"100%"}>
                        <Detail qualityResult={this.state.activeQualityResult}/>
                    </Scrollable>
                </Col>
                }
            </Row>
        </React.Fragment>
    }

    private getCellText(column, value) {
        if (column.id === "modulo" ||
            column.id === "yes_str" ||
            column.id === "no_str" ||
            column.id === "statement_parse" ||
            column.id === "format_prediction"
        ) {
            return this.getCellTextWithErrorAndValue(value);
        }
        if (column.id === "judge_method") {
            if (value.value) {
                return judgeMethodToText(value.value)
            }

            if (value.error) {
                return String(value.error);
            }
        }
        return String(value || "");
    }

    private getCellTextWithErrorAndValue(value) {
        return String(value.value || value.error || "");
    }

    private sortForErrorAndValue = (a, b, desc) => {
        a = this.getCellTextWithErrorAndValue(a);
        b = this.getCellTextWithErrorAndValue(b);
        return this.compare(a, b);
    };

    private sortForErrorAndValueForJudgeMethod = (a, b, desc) => {
        a = a.value ? judgeMethodToText(a.value) : String(a.error);
        b = b.value ? judgeMethodToText(b.value) : String(b.error);
        return this.compare(a, b);
    };

    private compare = (a? : string | number | null, b? : string | number | null) => {
        a = a === null || a === undefined ? '' : a;
        b = b === null || b === undefined ? '' : b;

        a = typeof a === 'string' ? a.toLowerCase() : a;
        b = typeof b === 'string' ? b.toLowerCase() : b;
        if (a > b) {
            return 1;
        }
        if (a < b) {
            return -1;
        }
        return 0
    }
}