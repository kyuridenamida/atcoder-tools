import * as React from 'react';
import './App.css';

import NavigationBar from './components/navbar/NavigationBar'
import HomePage from "./pages/homepage/HomePage";
import {HashRouter as Router, Route} from "react-router-dom";
import QualityPage from "./pages/quality/QualityPage";
import TemplatesPage from "./pages/templates/TemplatesPage";

class App extends React.Component {
    public render() {
        return (
            <Router>
                <div className="App">
                    <NavigationBar/>
                    <div className="text-left page-wrapper">
                        <Route path="/" exact component={HomePage}/>
                        <Route path="/quality/" component={QualityPage}/>
                        <Route path="/templates/" component={TemplatesPage}/>
                    </div>
                </div>
            </Router>
        );
    }
}

export default App;
