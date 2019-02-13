import * as React from "react";
interface ComponentProps {
    problem_id: string,
    contest_id: string
}

export default class ProblemLink extends React.Component<ComponentProps> {
    render() {
        return <a target="_blank"
                  href={`https://atcoder.jp/contests/${this.props.contest_id}/tasks/${this.props.problem_id}`}>
            {this.props.children}
            </a>;
    }
};
