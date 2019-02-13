import SyntaxHighlighter from 'react-syntax-highlighter';
import { docco } from 'react-syntax-highlighter/dist/styles/hljs';
import * as React from "react";

interface ComponentProps {
    code: string
}

export default class Code extends React.Component<ComponentProps, {}> {
    render() {
        return <SyntaxHighlighter language='cpp' style={docco}>{this.props.code}</SyntaxHighlighter>;
    }
};
