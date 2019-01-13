import * as React from 'react';
import './App.css';

import NavigationBar from './components/navbar/NavigationBar'
import HomePage from "./pages/homepage/HomePage";
import {BrowserRouter as Router, Route} from "react-router-dom";
import QualityPage from "./pages/quality/QualityPage";

class App extends React.Component {
    public render() {
        return (
            <Router>
                <div className="App">
                    <NavigationBar/>
                    <div className="text-left page-wrapper">
                        <Route path="/" exact component={HomePage}/>
                        <Route path="/quality/" component={QualityPage}/>
                    </div>
                </div>
            </Router>
        );
    }
}

export default App;
