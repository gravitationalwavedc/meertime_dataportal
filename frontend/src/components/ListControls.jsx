import Col from "react-bootstrap/Col";
import Form from "react-bootstrap/Form";
import SearchRow from "./SearchRow";
import { useProjectConfig } from "../context/project-config-context";

const option = (value, label = value) => (
  <option value={value} key={value}>
    {label}
  </option>
);

const allOption = option("All");

const matchesProject = (project, mainProject) =>
  !mainProject ||
  project.mainProject?.name?.toLowerCase() === mainProject.toLowerCase();

const uniqueValues = (values) => [...new Set(values.filter(Boolean))];

const mainProjectOptions = (projects) => {
  const seen = new Set();
  return projects
    .filter(({ mainProject }) => {
      if (!mainProject?.name || seen.has(mainProject.name)) {
        return false;
      }
      seen.add(mainProject.name);
      return true;
    })
    .map(({ mainProject }) =>
      option(mainProject.name, mainProject.telescope?.name || mainProject.name)
    );
};

const projectOptions = (projects, mainProject) => [
  allOption,
  ...projects
    .filter((project) => matchesProject(project, mainProject))
    .map(({ short }) => option(short)),
];

const bandOptions = (projects, mainProject) => [
  allOption,
  ...uniqueValues(
    projects
      .filter((project) => matchesProject(project, mainProject))
      .flatMap(({ bandOptions }) => bandOptions)
  ).map((value) => option(value)),
];

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
  const { projects } = useProjectConfig();
  const activeMainProject =
    projects.find(
      (project) =>
        project.mainProject?.name?.toLowerCase() === mainProject?.toLowerCase()
    )?.mainProject?.name || mainProject;
  const configuredProjectOptions = projectOptions(projects, activeMainProject);

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
                value={activeMainProject}
                onChange={(event) =>
                  handleMainProjectFilter(event.target.value)
                }
              >
                {mainProjectOptions(projects)}
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
                {configuredProjectOptions}
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
                {configuredProjectOptions}
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
                {bandOptions(projects, activeMainProject)}
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
