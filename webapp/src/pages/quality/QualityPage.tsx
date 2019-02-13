import * as React from 'react';

import {BrowserRouter as Router, Route} from "react-router-dom";
import Summary from "./summary/Summary";

class QualityPage extends React.Component{
    public render() {
        return (
            <div>
                <Router>
                    <div>
                        <Route path="/quality/summary" exact component={Summary}/>
                    </div>
                </Router>
            </div>
        );
    }
}

export default QualityPage;
