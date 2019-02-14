import * as React from 'react';

import {HashRouter as Router, Route} from "react-router-dom";
import Summary from "./summary/Summary";

class QualityPage extends React.Component{
    public render() {
        return (
            <Router>
                <React.Fragment>
                    <Route path="/quality/summary" exact component={Summary}/>
                </React.Fragment>
            </Router>
        );
    }
}

export default QualityPage;
