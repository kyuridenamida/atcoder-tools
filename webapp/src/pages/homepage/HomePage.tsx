import * as React from 'react';
import MarkDownView from "../../common/MarkDownView";

const loadReadme = async () => {
    const readmePath = require("../../auto_generated/README.md");
    const response = await fetch(readmePath);
    return response.text()
};

class HomePage extends React.Component<{}, {readme_html: any}> {
    render() {
        return (
            <MarkDownView loadMarkDown={loadReadme} />
        );
    }
}

export default HomePage;
