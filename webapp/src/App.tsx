import * as React from 'react';
import './App.css';

import NavigationBar from './components/navbar/NavigationBar'
import HomePage from "./pages/homepage/HomePage";

class App extends React.Component {
    public render() {
        return (
            <div className="App">
                <NavigationBar/>
                <HomePage/>
            </div>
        );
    }
}

export default App;
