import { HiDownload, HiViewGrid, HiViewList } from 'react-icons/hi';

import Button from 'react-bootstrap/Button';
import Col from 'react-bootstrap/Col';
import CustomColumnToggle from './CustomColumnToggle';
import Form from 'react-bootstrap/Form';
import React from 'react';
import { Search } from 'react-bootstrap-table2-toolkit';
import ToggleButton from 'react-bootstrap/ToggleButton';
import ToggleButtonGroup from 'react-bootstrap/ToggleButtonGroup';

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
            </Form.Row>
            <Form.Row style={{ marginTop: '-20px' }}>
                <Col md={4}>
                    <Form.Group controlId="jobSearch">
                        <Form.Label>Search</Form.Label>
                        <SearchBar label="Search" placeholder={searchText} {...searchProps}/>
                    </Form.Group>
                </Col>
                <Form.Group>
                    <ToggleButtonGroup 
                        style={{ marginTop: '2.3rem' }} type="radio" name="viewType" defaultValue="table">
                        <ToggleButton 
                            data-testid="table-view-button"
                            variant="link" 
                            size="sm"
                            value="table"
                            active={isTableView} 
                            onClick={() => setIsTableView(true)}>
                            <HiViewGrid className="mr-2" />
                            Table view 
                        </ToggleButton>
                        <ToggleButton
                            data-testid="list-view-button"
                            variant="link"
                            value="list"
                            size="sm"
                            active={!isTableView}
                            onClick={() => setIsTableView(false)}>
                            <HiViewList className="mr-2"/>
                            List view
                        </ToggleButton>
                    </ToggleButtonGroup>
                </Form.Group>
                <CustomColumnToggle {...columnToggleProps} exportCSVProps={exportCSVProps}/>
                <Form.Group>
                    <Button 
                        style={{ marginTop: '2.3rem' }} 
                        variant="link" 
                        size="sm"
                        onClick={() => exportCSVProps.onExport()}>
                        <HiDownload/>
                      Download CSV
                    </Button>
                </Form.Group>
            </Form.Row>
        </Form>);
};
// <Dropdown.Item onClick={() => exportCSVProps.onExport()}>Export as csv</Dropdown.Item>

ListControls.defaultProps = {
    searchText: 'Find a pulsar...'
};

export default ListControls;
