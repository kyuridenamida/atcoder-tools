import * as React from 'react';
import {Col, Input, Label, Row} from 'reactstrap';
import ReactTable from 'react-table'
import qualityResultList from "../../../auto_generated/qualityResultList.js"
import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";
import QualityResult from "../../../models/QualityResult";
import "./Summary.scss";
import Detail from "./Detail";
import ProblemLink from "./ProblemLink";

export default class Summary extends React.Component<{}, {
    showingCode: boolean,
    detailedSearchMode: boolean,
    activeQualityResult: QualityResult | null,
}> {
    constructor(props: any) {
        super(props);
        this.state = {
            activeQualityResult: null,
            showingCode: false,
            detailedSearchMode: false,
        }
    }

    updateActiveProblem = (qualityResult: QualityResult) => {
        this.setState({
            activeQualityResult: qualityResult,
            showingCode: true,
        });
    };

    isActive = (problemId: string) => {
        return this.state.activeQualityResult && problemId == this.state.activeQualityResult.problem.problem_id
    };


    render() {
        const {detailedSearchMode} = this.state;

        const renderValueOrError = ({value}, withOkMark = true) => {
            if (value.error) {
                if( value.error == "Skipped"){
                    return <span>
                        <FontAwesomeIcon icon="minus" color="lightgray"/>
                        {' '}
                        <span style={{color: 'lightgray'}}>Skipped</span>
                        </span>;
                }
                return <span>

                    {value.error != "Skipped" && <FontAwesomeIcon icon="times" color="red"/>}
                    {' '}
                    {value.error}
                    </span>
            }
            return <span>
                {withOkMark && <FontAwesomeIcon icon="check" color="green"/>}
                {' '}
                {value.value || ""}
                </span>
        };
        const renderValueOrErrorWithoutOkMark = (props) => renderValueOrError(props, false);

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
                    },
                ]
            }];

        const defaultFilterMethod = (filter, row, column) => {
            const id = filter.pivotId || filter.id;
            try {
                return row[id] !== undefined ? this.getCellText(column, row[id]).match(filter.value) != null : true;

            } catch (e) {
                return false;
            }
        };


        return <div>
            <Row>
                <h3>Summary</h3>
                <Col sm={12}>
                    <Label>
                        <Input type="checkbox" checked={this.state.detailedSearchMode}
                               onChange={() => this.setState({detailedSearchMode: !this.state.detailedSearchMode})}/>
                        詳細検索モード
                    </Label>
                </Col>
            </Row>
            <Row>
                <Col sm={this.state.detailedSearchMode ? 12 : 6}>
                    <ReactTable
                        filterable
                        data={qualityResultList}
                        columns={columns}
                        defaultFilterMethod={defaultFilterMethod}
                        style={{
                            height: "100%"
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
                    <Detail qualityResult={this.state.activeQualityResult}/>
                </Col>
                }
            </Row>
        </div>
    }

    private getCellText(column, value) {
        if (column.id == "modulo" ||
            column.id == "yes_str" ||
            column.id == "no_str" ||
            column.id == "statement_parse" ||
            column.id == "format_prediction"
        ) {
            return this.getCellTextWithErrorAndValue(value);
        }
        return String(value || "");
    }

    private getCellTextWithErrorAndValue(value) {
        return String(value.value || value.error || "");
    }

    private sortForErrorAndValue = (a, b, desc) => {
        a = this.getCellTextWithErrorAndValue(a);
        b = this.getCellTextWithErrorAndValue(b);
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
    };
}