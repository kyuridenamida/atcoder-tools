import SyntaxHighlighter from 'react-syntax-highlighter';
import { docco } from 'react-syntax-highlighter/dist/styles/hljs';
import * as React from "react";
import Language from "../../../models/Language";

interface ComponentProps {
    code: string,
    language: Language
}

export default class Code extends React.Component<ComponentProps, {}> {
    render() {
        return <SyntaxHighlighter language={this.props.language} style={docco}>{this.props.code}</SyntaxHighlighter>;
    }
};
