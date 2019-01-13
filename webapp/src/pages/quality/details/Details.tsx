import * as React from 'react';
import ReactTable from 'react-table'
import qualityResultList from "../../../auto_generated/qualityResultList.js"
import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";
import Code from "../Code";
import QualityResult from "../../../models/QualityResult";
import "./Summary.scss";
import {PopoverBody, PopoverHeader} from "reactstrap";
import Popover from "reactstrap/lib/Popover";

export default class Details extends React.Component<{}, {
    activeProblemId: string | null,
    showingCode: boolean,
}> {
    constructor(props: any) {
        super(props);
        this.state = {
            activeProblemId: null,
            showingCode: false
        }
    }

    updateActiveProblem = (problemId: string) => {
        this.setState({
            activeProblemId: problemId,
            showingCode: true,
        });
    };

    isActive = (problemId: string) => {
        return problemId == this.state.activeProblemId
    };


    render() {
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

        const columns = [{
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
                        <a target="_blank"
                           href={`https://atcoder.jp/contests/${original.contest.contest_id}/tasks/${value}`}>{value}</a>
                }
            ]
        }, {
            Header: 'Sample Parsing',
            accessor: 'statement_parse',
            Cell: renderValueOrError,
            sortMethod: this.sortForErrorAndValue,
        }
            , {
                Header: 'Format Pred.',
                accessor: 'format_prediction',
                Cell: (props) => {
                    const original = props.original as QualityResult;
                    return <div id={original.problem.problem_id}>
                        <Popover placement="right"
                                 isOpen={this.state.showingCode && this.isActive(original.problem.problem_id)}
                                 target={original.problem.problem_id}>
                            <PopoverHeader>Generated Code</PopoverHeader>
                            <PopoverBody>
                                <Code code={original.codes.cpp || ""} />
                            </PopoverBody>
                        </Popover>
                        {renderValueOrError(props)}
                    </div>;
                },
                sortMethod: this.sortForErrorAndValue,
            }, {
                Header: 'Constants Prediction',
                columns: [
                    {
                        Header: 'MOD',
                        accessor: 'modulo',
                        Cell: renderValueOrErrorWithoutOkMark,
                        sortMethod: this.sortForErrorAndValue,
                    }, {
                        Header: 'YES',
                        accessor: 'yes_str',
                        Cell: renderValueOrErrorWithoutOkMark,
                        sortMethod: this.sortForErrorAndValue,
                    }, {
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
            <h3>Summary</h3>
            <ReactTable
                filterable
                data={qualityResultList}
                columns={columns}
                defaultFilterMethod={defaultFilterMethod}
                style={{
                    height: "100%"
                }}
                getTrProps={(state, rowInfo) => {
                    const original = rowInfo.original as QualityResult;
                    console.log(this.state.activeProblemId, original.problem.problem_id);
                    return {
                        onClick: () => this.updateActiveProblem(original.problem.problem_id),
                        className: this.isActive(original.problem.problem_id) ? "selected" : ""
                    }
                }}
            />
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