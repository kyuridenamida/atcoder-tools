import * as React from 'react';

import {Route, BrowserRouter as Router} from "react-router-dom";
import Summary from "./summary/Summary";
import {NavLink} from "reactstrap";
import Details from "./details/Details";

class QualityPage extends React.Component{
    public render() {
        return (
            <div>
                <NavLink href="/quality/summary">Summary</NavLink>
                <NavLink href="/quality/details">Details</NavLink>

                <Router>
                    <Route path="/quality/details" exact component={Details}/>
                    <Route path="/quality/summary" exact component={Summary}/>
                </Router>
            </div>
        );
    }
}

export default QualityPage;
