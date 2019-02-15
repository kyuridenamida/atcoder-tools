import * as React from 'react';
import {ALL_LANGUAGES, langToDisplayName} from "../models/Language";
import {Nav, NavItem, NavLink} from 'reactstrap';
import * as classNames from 'classnames';
import Language from "../models/Language";
interface ComponentProps {
    onLanguageSelected: (Language) => void,
    activeLanguage: Language
}

export default class LanguageTabs extends React.Component<ComponentProps, {}> {
    public render(){
        return <Nav tabs>
            {ALL_LANGUAGES.map((lang) => {
                return <NavItem key={lang}>
                    <NavLink
                        className={classNames({active: this.props.activeLanguage === lang})}
                        onClick={() => this.props.onLanguageSelected(lang)}
                    >
                        {langToDisplayName(lang)}
                    </NavLink>
                </NavItem>;
            })}
        </Nav>;
    }
}