import * as React from 'react';
import ReactTable from 'react-table'
import qualityResultList from "../../auto_generated/qualityResultList.js"
import QualityResult from "../../models/QualityResult";

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
        const render_value_or_error = ({value}) => {
            return value.value || value.error || "";
        };

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
            accessor: 'statement_parse.error',
        }
            , {
                Header: 'Format Pred.',
                accessor: 'format_prediction.error'
            }, {
                Header: 'Constants Prediction',
                columns: [
                    {
                        Header: 'MOD',
                        accessor: 'modulo',
                        Cell: render_value_or_error
                    }, {
                        Header: 'YES',
                        accessor: 'yes_str',
                        Cell: render_value_or_error
                    }, {
                        Header: 'NO',
                        accessor: 'no_str',
                        Cell: render_value_or_error
                    },


                ]
            }];

        const defaultFilterMethod = (filter, row, column) => {
            const id = filter.pivotId || filter.id;
            try {
                let cell_text: string;
                //console.log(column);
                if (column.id == "modulo" || column.id == "yes_str" || column.id == "no_str") {
                    cell_text = String(row[id].value || row[id].error || "");
                }else{
                    cell_text = String(row[id] || "");
                }
                return row[id] !== undefined ? cell_text.match(filter.value) != null : true;

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
}