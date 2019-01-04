import * as React from 'react';
import * as marked from "marked";

const loadReadme = async () => {
    const readmePath = require("../../auto_generated/README.md");
    const response = await fetch(readmePath);
    return response.text()
};

class HomePage extends React.Component<{}, {readme_html: any}> {
    constructor(props: any) {
        super(props);
        this.state = {
            readme_html: '',
        }

    }

    componentDidMount() {
        loadReadme()
            .then(text=>{
                this.setState({
                    readme_html: marked(text)
                });
            });
    }

    render() {
        return (
            <div>
                <div className="text-left" dangerouslySetInnerHTML={
                    {__html: this.state.readme_html}
                } />
            </div>
        );
    }
}

export default HomePage;
