import * as React from 'react';
import { Collapse, Button } from 'reactstrap';

interface ComponentProps {
    showButtonText: string,
    hideButtonText: string,
    visibleByDefault?: boolean,
}

class Hidable extends React.Component<ComponentProps, {collapse: boolean}> {
    constructor(props) {
        super(props);
        this.toggle = this.toggle.bind(this);
        this.state = { collapse: !!this.props.visibleByDefault };
    }

    toggle() {
        this.setState({ collapse: !this.state.collapse });
    }

    render() {
        const {showButtonText, hideButtonText} = this.props;
        const {collapse} = this.state;
        return (
            <div>
                <Button size="sm" color={!collapse ? "primary" : "secondary"} onClick={this.toggle} style={{ marginBottom: '1rem' }}>{collapse ? hideButtonText : showButtonText}</Button>
                <Collapse isOpen={collapse}>
                    {this.props.children}
                </Collapse>
            </div>
        );
    }
}

export default Hidable;