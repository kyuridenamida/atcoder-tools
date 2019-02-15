import * as React from 'react';
import {
    Collapse,
    Nav,
    Navbar,
    NavbarBrand,
    NavbarToggler,
    NavItem,
    NavLink} from 'reactstrap';

class NavigationBar extends React.Component<{},{isOpen: boolean}> {
    constructor(props: any) {
        super(props);

        this.toggle = this.toggle.bind(this);
        this.state = {
            isOpen: false
        };
    }

    public render() {
        return (
            <div>
                <Navbar color="light" light expand="md">
                    <NavbarBrand href="#/">AtCoder Tools</NavbarBrand>
                    <NavbarToggler onClick={this.toggle} />
                    <Collapse isOpen={this.state.isOpen} navbar>
                        <Nav className="ml-auto" navbar>
                            <NavItem>
                                <NavLink href="#/templates">テンプレート</NavLink>
                            </NavItem>
                            <NavItem>
                                <NavLink href="#/quality/summary">各問題毎の解析結果</NavLink>
                            </NavItem>
                            <NavItem>
                                <NavLink href="https://github.com/kyuridenamida/atcoder-tools">GitHub</NavLink>
                            </NavItem>
                        </Nav>
                    </Collapse>
                </Navbar>
            </div>
        );
    }

    private toggle() {
        this.setState({
            isOpen: !this.state.isOpen
        });
    }
}

export default NavigationBar;
