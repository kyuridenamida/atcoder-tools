import * as React from 'react';
import "./Details.scss";
import {decorators, Treebeard} from 'react-treebeard';
import {Col, Row} from "reactstrap";
import QualityResult from "../../../models/QualityResult";
import qualityResultList from "../../../auto_generated/qualityResultList.js"
import listStyles from "./listStyles";
import styled from '@emotion/styled';
import Code from "../Code";
import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";


const buildData = () => {
    const res = {} as { [contest: string]: QualityResult[] };

    qualityResultList.forEach((result: QualityResult) => {
        if (!res.hasOwnProperty(result.contest.contest_id)) {
            res[result.contest.contest_id] = []
        }
        res[result.contest.contest_id].push(result);
    });


    const tree: any[] = [];


    Object.keys(res).sort().forEach(contest => {
        const resultList = res[contest];
        const subtree: any[] = [];
        let is_prefect_contest = true;
        resultList.forEach((r: QualityResult) => {
            const children: any[] = [];
            if( r.codes.cpp ) {
                children.push({
                    name: "main.cpp",
                    code: r.codes.cpp,
                });
            }
            const successful = !!r.codes.cpp;

            subtree.push({
                name: r.problem.problem_id,
                toggled: true,
                children: children.length > 0 ? children : undefined,
                successful: successful,
            });

            is_prefect_contest = is_prefect_contest && successful;
        });
        tree.push({
            name: contest,
            children: subtree,
            successful: is_prefect_contest,
        });
    });
    return {
        name: "Contests",
        toggled: true,
        children: tree
    };
};

const builtData = buildData();

const Div = styled('Div', {
    shouldForwardProp: prop => ['className', 'children'].indexOf(prop) !== -1
})(({style}) => style);

decorators.Header = ({style, node}) => {
    let icon: any = null;

    if (node.hasOwnProperty("successful")) {
        if (node.successful) {
            icon = <FontAwesomeIcon icon="check" color="green"/>;
        } else {
            icon = <FontAwesomeIcon icon="times" color="red"/>;
        }
    }


    return (
        <Div style={style.base}>
            <Div style={style.title}>
                {icon}
                {' '}
                {node.name}
            </Div>
        </Div>
    );
};


const Scrollable = ({children}) => {
    return <div style={{height: 500, overflowY: "scroll"}}>
        {children}
    </div>
};

class TreeExample extends React.Component<{}, { cursor: any }> {
    constructor(props) {
        super(props);
        this.state = {
            cursor: null,
        };
        this.onToggle = this.onToggle.bind(this);
    }

    onToggle(node, toggled) {
        if (this.state.cursor) {
            this.state.cursor.active = false;
        }
        node.active = true;
        if (node.children) {
            node.toggled = toggled;
        }
        this.setState({cursor: node});
    }

    render() {
        const {cursor} = this.state;
        console.log(this.state.cursor);
        return (
            <Row>
                <Col sm={4}>
                    <Scrollable>
                        <Div style={listStyles.component}>
                            <Treebeard data={builtData}
                                       decorators={decorators}
                                       onToggle={this.onToggle}/>
                        </Div>
                    </Scrollable>
                </Col>
                <Col sm={8}>
                    {cursor && cursor.code && <Code code={cursor.code}/>}
                </Col>
            </Row>

        );
    }
}

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


    render() {
        return <TreeExample/>
    }

}