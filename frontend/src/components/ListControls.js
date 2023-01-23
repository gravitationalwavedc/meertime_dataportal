import Col from 'react-bootstrap/Col';
import Form from 'react-bootstrap/Form';
import React from 'react';
import SearchRow from './SearchRow';

const mainProjects = [
    {
        value: 'meertime',
        title: 'MeerTime',
        subprojects: [
            'All',
            'TPA',
            'RelBin',
            'PTA',
            'GC',
            'NGC6440',
            'MeerTime',
            'Flux',
            'Unknown'
        ],
        bandOptions: [
            'All',
            'L-BAND',
            'UHF',
            'S-BAND',
            'UNKNOWN'
        ]
    },
    {
        value: 'trapum',
        title: 'Trapum',
        subprojects: [
            'All'
        ],
        bandOptions: [
            'All',
            'L-BAND',
            'UHF',
            'S-BAND',
            'UNKNOWN'
        ]
    },
    {
        value: 'MONSPSR',
        title: 'Molonglo',
        subprojects: [
            'All',
            'Mo-NS',
            'Mo-EW',
        ],
        bandOptions: [
            'UHF-NS',
            'UHF-EW'
        ]
    }
];

const ListControls = ({
    searchText,
    handleProjectFilter,
    handleBandFilter,
    handleMainProjectFilter,
    mainProject,
    mainProjectSelect,
    project,
    searchProps,
    isTableView,
    setIsTableView,
    columnToggleProps,
    exportCSVProps }) => {

    const currentMainProject = mainProjects.find(({ value }) => value === mainProject);

    const subprojectOptions = mainProject ?
        currentMainProject.subprojects : mainProjects[0].subprojects;

    return (
        <>
            <Form.Row>
                {mainProjectSelect && <Col md={3} xl={2}>
                    <Form.Group controlId="mainProjectSelect">
                        <Form.Label>Main Project</Form.Label>
                        <Form.Control
                            custom
                            as="select"
                            value={mainProject}
                            onChange={(event) => handleMainProjectFilter(event.target.value)}>
                            {mainProjects.map(
                                ({ value, title }) => <option value={value} key={value}>{title}</option>)
                            }
                        </Form.Control>
                    </Form.Group>
                </Col>}
                {handleProjectFilter && <Col md={3} xl={2}>
                    <Form.Group controlId="projectSelect">
                        <Form.Label>Project</Form.Label>
                        <Form.Control
                            custom
                            as="select"
                            value={project}
                            onChange={(event) => handleProjectFilter(event.target.value)}>
                            {subprojectOptions.map(value => <option value={value} key={value}>{value}</option>)}
                        </Form.Control>
                    </Form.Group>
                </Col>}
                {handleBandFilter && <Col md={3} xl={2}>
                    <Form.Group controlId="bandSelect">
                        <Form.Label>Band</Form.Label>
                        <Form.Control
                            custom
                            as="select"
                            onChange={(event) => handleBandFilter(event.target.value)}>
                            <option value='All'>All</option>
                            {currentMainProject.bandOptions.map(
                                value => <option value={value} key={value}>{value}</option>
                            )}
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
                exportCSVProps={exportCSVProps} />
        </>);
};

ListControls.defaultProps = {
    searchText: 'Find a pulsar...'
};

export default ListControls;
