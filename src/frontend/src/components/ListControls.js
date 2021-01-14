import { HiOutlineViewGrid, HiOutlineViewList } from 'react-icons/hi';

import Button from 'react-bootstrap/Button';
import Col from 'react-bootstrap/Col';
import CustomColumnToggle from './CustomColumnToggle';
import Form from 'react-bootstrap/Form';
import React from 'react';
import { Search } from 'react-bootstrap-table2-toolkit';

const projects = [
    {
        value: 'meertime',
        title: 'MeerTime',
        subprojects: [
            'All',
            'TPA',
            'Relbin',
            'PTA',
            'GC',
            'NGC6440',
            'MeerTime',
            'Flux',
            'Unknown'
        ]
    },
    {
        value: 'trapum',
        title: 'Trapum',
        subprojects: [
            'All'
        ]
    }
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
    handleProjectFilter,
    currentProject,
    searchProps, 
    isTableView,
    setIsTableView,
    columnToggleProps, 
    exportCSVProps }) => {
    const { SearchBar } = Search;
    const subprojectOptions = currentProject ? 
        projects.find(({ value }) => value === currentProject).subprojects : projects[0].subprojects;
    return (
        <Form>
            <Form.Row>
                <Col md={4}>
                    <Form.Group controlId="jobSearch">
                        <Form.Label>Search</Form.Label>
                        <SearchBar label="Search" placeholder={searchText} {...searchProps}/>
                    </Form.Group>
                </Col>
                { currentProject && <Col md={2}>
                    <Form.Group controlId="mainProjectSelect">
                        <Form.Label>Main Project</Form.Label>
                        <Form.Control 
                            custom
                            as="select"  
                            value={currentProject}
                            onChange={(event) => handleProjectFilter(event.target.value)}>
                            {projects.map(
                                ({ value, title })=> <option value={value} key={value}>{title}</option>)
                            }
                        </Form.Control>
                    </Form.Group>
                </Col> }
                { handleProposalFilter && <Col md={2}>
                    <Form.Group controlId="projectSelect">
                        <Form.Label>Project</Form.Label>
                        <Form.Control 
                            custom
                            as="select"  
                            onChange={(event) => handleProposalFilter(event.target.value)}>
                            {subprojectOptions.map(value => <option value={value} key={value}>{value}</option>)}
                        </Form.Control>
                    </Form.Group>
                </Col>}
                { handleBandFilter && <Col md={2}>
                    <Form.Group controlId="bandSelect">
                        <Form.Label>Band</Form.Label>
                        <Form.Control 
                            custom 
                            as="select" 
                            onChange={(event) => handleBandFilter(event.target.value)}>
                            {bandOptions.map(value => <option value={value} key={value}>{value}</option>)}
                        </Form.Control>
                    </Form.Group>
                </Col>}
                <Col md={1} className="d-flex align-items-center">
                    <CustomColumnToggle {...columnToggleProps} exportCSVProps={exportCSVProps}/>
                    <Button 
                        data-testid="table-view-button"
                        variant="icon" 
                        className="ml-2 mr-1" 
                        active={isTableView} 
                        onClick={() => setIsTableView(true)}>
                        <HiOutlineViewList className='h5' />
                    </Button>
                    <Button 
                        data-testid="list-view-button"
                        variant="icon"
                        active={!isTableView}
                        onClick={() => setIsTableView(false)}>
                        <HiOutlineViewGrid className='h5' />
                    </Button>
                </Col>
            </Form.Row>
        </Form>);
};

ListControls.defaultProps = {
    searchText: 'Find a pulsar...'
};

export default ListControls;
