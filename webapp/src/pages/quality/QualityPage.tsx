import * as React from 'react';
import ReactTable from 'react-table'
import qualityResultList from "../../auto_generated/qualityResultList.js"
import QualityResult from "../../models/QualityResult";
import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";


export default class QualityPage extends React.Component<{}, {
    qualityResultList: QualityResult[]
}> {
    constructor(props: any) {
        super(props);
        this.state = {
            qualityResultList: [],
        };
    }

    componentDidMount() {
    }

    render() {
        const renderValueOrError = ({value}, with_ok_mark = true) => {
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
                {with_ok_mark && <FontAwesomeIcon icon="check" color="green"/>}
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
                Cell: renderValueOrError,
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