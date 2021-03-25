import DataDisplay from './DataDisplay';
import React from 'react';
import { Row } from 'react-bootstrap';

const SummaryDataRow = ({ dataPoints, secondLine }) => { 

    let rowClasses = 'summaryData';

    if (secondLine === true) {
        rowClasses = 'justify-content-end secondLine';
    } 

    return (
        <Row className={rowClasses}>
            {dataPoints.map(({ title, value }) => <DataDisplay key={title} title={title} value={value}/>)}
        </Row>
    );
};

SummaryDataRow.defaultProps = {
    secondLine: false
};

export default SummaryDataRow;
