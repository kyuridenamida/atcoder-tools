import * as React from 'react';

const Scrollable = ({children, height}) => {
    return <div style={{height, overflowY: 'auto'}}>
        {children}
    </div>
};

export default Scrollable;