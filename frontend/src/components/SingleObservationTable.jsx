import { Button, Col, Form, Row } from "react-bootstrap";
import { useState } from "react";
import { formatProjectName, formatSingleObservationData } from "../helpers";
import { formatUTC, kronosLink } from "../helpers";
import DataDisplay from "./DataDisplay";
import ImageGrid from "./ImageGrid";
import { Link } from "found";
import MainLayout from "./MainLayout";
import MolongloImageGrid from "./MolongloImageGrid";
import DownloadFluxcalButtons from "./DownloadFluxcalButtons";

const SingleObservationTable = ({
  data: { foldPulsarResult },
  jname,
}) => {
  const relayObservationModel = foldPulsarResult.edges[0].node;

  // const projectChoices = Array.from(
  //   relayObservationModel.images.edges.reduce(
  //     (plotTypesSet, { node }) => plotTypesSet.add(node.project.short),
  //     new Set()
  //   )
  // )
  const projectChoices = ['pta'];


  const [project, setProject] = useState(projectChoices[0]);

  const title = (
    <Link size="sm" to={`/fold/meertime/${jname}/`}>
      {jname}
    </Link>
  );

  const displayDate = formatUTC(relayObservationModel.observation.utcStart);

  const dataItems = formatSingleObservationData(relayObservationModel.observation);

  const isMolonglo = relayObservationModel.observation.project.mainProject.name
    .toLowerCase()
    .includes("monspsr");

  return (
    <MainLayout title={title}>
      <h5 className="single-observation-subheading">{displayDate}</h5>
      <h5>Beam {relayObservationModel.observation.beam}</h5>
      <Row>
        <Col>
          <Button
            size="sm"
            as="a"
            className="mr-2"
            href={kronosLink(relayObservationModel.observation.beam, jname, displayDate)}
            variant="outline-secondary"
          >
            View Kronos
          </Button>
          <DownloadFluxcalButtons data={data} />
        </Col>
      </Row>
      {projectChoices.length >= 1 ? (
        <Row className="mt-2">
          <Col sm={4} md={4}>
            <Form.Group controlId="mainProjectSelect">
              <Form.Label>Cleaned Data Project</Form.Label>
              <Form.Control
                custom
                as="select"
                value={project}
                onChange={(event) => setProject(event.target.value)}
              >
                {projectChoices.map((value) => (
                  <option value={value} key={value}>
                    {formatProjectName(value)}
                  </option>
                ))}
              </Form.Control>
            </Form.Group>
          </Col>
        </Row>
      ) : null}
      <Row>
        <Col>
          {isMolonglo ? (
            <MolongloImageGrid
              images={relayObservationModel.images}
              project={project}
            />
          ) : (
            <ImageGrid
              images={relayObservationModel.images}
              project={project}
            />
          )}
        </Col>
        <Col lg={4}>
          {Object.keys(dataItems).map((key) => (
            <DataDisplay key={key} title={key} value={dataItems[key]} full />
          ))}
        </Col>
      </Row>
    </MainLayout>
  );
};

export default SingleObservationTable;
