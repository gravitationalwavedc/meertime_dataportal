import {
  getProject,
  getSubProjectOptions,
  projectOptions,
} from "../telescopes";
import Col from "react-bootstrap/Col";
import Form from "react-bootstrap/Form";
import React from "react";
import SearchRow from "./SearchRow";

const ListControls = ({
  query,
  searchText,
  mainProject,
  handleMainProjectFilter,
  mostCommonProject,
  handleMostCommonProjectFilter,
  project,
  handleProjectFilter,
  band,
  handleBandFilter,
  searchProps,
  isTableView,
  setIsTableView,
  columnToggleProps,
  rememberSearch,
  exportCSVProps,
}) => {
  const currentProject = getProject(mainProject);
  const subprojectOptions = getSubProjectOptions(currentProject.subprojects);

  return (
    <>
      <Form.Row>
        {handleMainProjectFilter && (
          <Col md={3} xl={2}>
            <Form.Group controlId="mainProjectSelect">
              <Form.Label>Main Project</Form.Label>
              <Form.Control
                role="main-project-select"
                custom
                as="select"
                value={mainProject}
                onChange={(event) =>
                  handleMainProjectFilter(event.target.value)
                }
              >
                {projectOptions}
              </Form.Control>
            </Form.Group>
          </Col>
        )}
        {handleMostCommonProjectFilter && (
          <Col md={3} xl={2}>
            <Form.Group controlId="mostCommonProjectSelect">
              <Form.Label>Most Common Project</Form.Label>
              <Form.Control
                custom
                role="most-common-project-select"
                as="select"
                value={mostCommonProject}
                onChange={(event) =>
                  handleMostCommonProjectFilter(event.target.value)
                }
              >
                {subprojectOptions}
              </Form.Control>
            </Form.Group>
          </Col>
        )}
        {handleProjectFilter && (
          <Col md={3} xl={2}>
            <Form.Group controlId="projectSelect">
              <Form.Label>Project</Form.Label>
              <Form.Control
                custom
                role="project-select"
                as="select"
                value={project}
                onChange={(event) => handleProjectFilter(event.target.value)}
              >
                {subprojectOptions}
              </Form.Control>
            </Form.Group>
          </Col>
        )}
        {handleBandFilter && (
          <Col md={3} xl={2}>
            <Form.Group controlId="bandSelect">
              <Form.Label>Band</Form.Label>
              <Form.Control
                custom
                as="select"
                role="band-select"
                value={band}
                onChange={(event) => handleBandFilter(event.target.value)}
              >
                {currentProject.bandOptions.map((value) => (
                  <option value={value} key={value}>
                    {value}
                  </option>
                ))}
              </Form.Control>
            </Form.Group>
          </Col>
        )}
      </Form.Row>
      <SearchRow
        query={query}
        setIsTableView={setIsTableView}
        isTableView={isTableView}
        searchText={searchText}
        searchProps={searchProps}
        columnToggleProps={columnToggleProps}
        exportCSVProps={exportCSVProps}
        rememberSearch={rememberSearch}
      />
    </>
  );
};

ListControls.defaultProps = {
  searchText: "Find a pulsar...",
  rememberSearch: false,
};

export default ListControls;
