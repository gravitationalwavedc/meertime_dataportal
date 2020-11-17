import React from 'react';
import Form from 'react-bootstrap/Form';
import Col from 'react-bootstrap/Col';
import { Search } from 'react-bootstrap-table2-toolkit';
import CustomColumnToggle from './CustomColumnToggle';

const projectOptions = [
    'All',
    'TPA',
    'Relbin',
    'PTA',
    'GC',
    'NGC6440',
    'MeerTime',
    'Flux',
    'Unknown'
];

const bandOptions = [
    'All',
    'L-band',
    'UHF'
];

const ListControls = ({ 
    searchText, 
    handleProposalFilter, 
    handleBandFilter, 
    searchProps, 
    columnToggleProps, 
    exportCSVProps }) => {
    const { SearchBar } = Search;
    return (
        <Form>
            <Form.Row>
                <Col>
                    <Form.Group controlId="jobSearch">
                        <Form.Label>Search</Form.Label>
                        <SearchBar label="Search" placeholder={searchText} {...searchProps}/>
                    </Form.Group>
                </Col>
                <Col md={3}>
                    <Form.Group controlId="projectSelect">
                        <Form.Label>Project</Form.Label>
                        <Form.Control 
                            custom
                            as="select"  
                            onChange={(event) => handleProposalFilter(event.target.value)}>
                            {projectOptions.map(value => <option value={value} key={value}>{value}</option>)}
                        </Form.Control>
                    </Form.Group>
                </Col>
                <Col md={3}>
                    <Form.Group controlId="bandSelect">
                        <Form.Label>Band</Form.Label>
                        <Form.Control 
                            custom 
                            as="select" 
                            onChange={(event) => handleBandFilter(event.target.value)}>
                            {bandOptions.map(value => <option value={value} key={value}>{value}</option>)}
                        </Form.Control>
                    </Form.Group>
                </Col>
                <Col md={1} className="d-flex align-items-center">
                    <CustomColumnToggle {...columnToggleProps} exportCSVProps={exportCSVProps}/>
                </Col>
            </Form.Row>
        </Form>);
};

ListControls.defaultProps = {
    searchText: 'Find a pulsar...'
};

export default ListControls;
