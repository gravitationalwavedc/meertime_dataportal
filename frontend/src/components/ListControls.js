import { getProject, getSubProjectOptions, projectOptions } from '../telescopes';
import Col from 'react-bootstrap/Col';
import Form from 'react-bootstrap/Form';
import React from 'react';
import SearchRow from './SearchRow';


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

    const currentProject = getProject(mainProject); 
    const subprojectOptions = getSubProjectOptions(currentProject.subprojects);

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
                            {projectOptions}
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
                            {subprojectOptions}
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
                            {currentProject.bandOptions.map(
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
