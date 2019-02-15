import * as React from 'react';
import * as marked from "marked";

class MarkDownView extends React.Component<{
    loadMarkDown:  () => Promise<string>,
}, {readme_html: any}> {
    constructor(props: any) {
        super(props);
        this.state = {
            readme_html: '',
        }

    }

    componentDidMount() {
        this.props.loadMarkDown()
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

export default MarkDownView;
