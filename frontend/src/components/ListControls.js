import Col from 'react-bootstrap/Col';
import Form from 'react-bootstrap/Form';
import React from 'react';
import SearchRow from './SearchRow';

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


    const subprojectOptions = currentProject ? 
        projects.find(({ value }) => value === currentProject).subprojects : projects[0].subprojects;

    return (
        <Form>
            <Form.Row>
                { currentProject && <Col md={3} xl={2}>
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
                { handleProposalFilter && <Col md={3} xl={2}>
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
                { handleBandFilter && <Col md={3} xl={2}>
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
            <SearchRow 
                setIsTableView={setIsTableView}
                isTableView={isTableView}
                searchText={searchText}
                searchProps={searchProps}
                columnToggleProps={columnToggleProps}
                exportCSVProps={exportCSVProps}/>
        </Form>);
};
// <Dropdown.Item onClick={() => exportCSVProps.onExport()}>Export as csv</Dropdown.Item>

ListControls.defaultProps = {
    searchText: 'Find a pulsar...'
};

export default ListControls;
