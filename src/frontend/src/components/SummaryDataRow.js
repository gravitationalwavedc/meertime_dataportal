import DataDisplay from './DataDisplay';
import React from 'react';
import { Row } from 'react-bootstrap';

const mainStyle = {
    margin: '-17rem 256px 4rem auto',
};

const secondLineStyle = {
    margin: '0 256px 4rem auto',
};


const SummaryDataRow = ({ dataPoints, secondLine }) => 
    <Row className="justify-content-end" style={secondLine ? secondLineStyle : mainStyle}>
        {dataPoints.map(({ title, value }) => <DataDisplay key={title} title={title} value={value}/>)}
    </Row>;

SummaryDataRow.defaultProps = {
    secondLine: false
};

export default SummaryDataRow;
