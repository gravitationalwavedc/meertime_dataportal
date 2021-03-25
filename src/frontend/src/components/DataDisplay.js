import Col from 'react-bootstrap/Col';
import React from 'react';

const DataDisplay = ({ title, value }) => 
    <Col lg={2} md={3} sm xs>
        <p className="mb-1 text-primary-600">{ title }</p>
        <h4>{ value ? value : 'N/A' }</h4>
    </Col>;
export default DataDisplay;
