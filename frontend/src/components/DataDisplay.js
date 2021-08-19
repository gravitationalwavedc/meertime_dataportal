import Col from 'react-bootstrap/Col';
import React from 'react';

const DataDisplay = ({ title, value, full }) => 
    <Col lg={full ? 12 : 2} md={full ? 12 : 3} sm xs>
        <p className="mb-1 text-primary-600">{ title }</p>
        <h4>{ value ? value : 'N/A' }</h4>
    </Col>;

DataDisplay.defaultProps = {
    full: false
};

export default DataDisplay;
