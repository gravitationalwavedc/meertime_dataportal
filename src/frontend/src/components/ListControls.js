import React from 'react';
import Form from 'react-bootstrap/Form';
import Col from 'react-bootstrap/Col';
import { Search } from 'react-bootstrap-table2-toolkit';

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

const ListControls = ({handleProposalFilter, handleBandFilter, searchProps}) => {
    const { SearchBar } = Search;
    return (
        <Form>
            <Form.Row>
                <Col>
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
                <Col>
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
                <Col>
                    <Form.Group controlId="jobSearch">
                        <Form.Label>Search</Form.Label>
                        <SearchBar label="Search" {...searchProps}/>
                    </Form.Group>
                </Col>
            </Form.Row>
        </Form>);};

export default ListControls;
