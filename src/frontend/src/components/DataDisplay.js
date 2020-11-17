import React from 'react';
import Col from 'react-bootstrap/Col';

const DataDisplay = ({ title, value }) => 
    <Col md={1}>
        <p className="mb-1 text-primary-600">{ title }</p>
        <h4>{ value }</h4>
    </Col>;
export default DataDisplay;
