import { Button, Col, Form, Row } from "react-bootstrap";
import { useState } from "react";
import { graphql, useFragment } from "react-relay";
import { formatProjectName, formatSingleObservationData } from "../helpers";
import { formatUTC, kronosLink, sessionLink } from "../helpers";
import DataDisplay from "./DataDisplay";
import ImageGrid from "./ImageGrid";
import MolongloImageGrid from "./MolongloImageGrid";
import DownloadFluxcalButtons from "./DownloadFluxcalButtons";

const SingleObservationTableFragment = graphql`
  fragment SingleObservationTableFragment on Query
  @argumentDefinitions(
    pulsar: { type: "String!" }
    utc: { type: "String" }
    beam: { type: "Int" }
  ) {
    pulsarFoldResult(pulsar: $pulsar, utcStart: $utc, beam: $beam) {
      edges {
        node {
          observation {
            calibration {
              id
              idInt
            }
            beam
            utcStart
            obsType
            project {
              id
              short
              mainProject {
                name
              }
            }
            frequency
            bandwidth
            raj
            decj
            duration
            foldNbin
            foldNchan
            foldTsubint
            nant
          }
          images {
            edges {
              node {
                image
                cleaned
                imageType
                resolution
                url
              }
            }
          }
        }
      }
    }
  }
`;

const SingleObservationTable = ({ data, jname }) => {
  const relayData = useFragment(SingleObservationTableFragment, data);
  const { pulsarFoldResult } = relayData;
  const relayObservationModel = pulsarFoldResult.edges[0].node;

  // const projectChoices = Array.from(
  //   relayObservationModel.images.edges.reduce(
  //     (plotTypesSet, { node }) => plotTypesSet.add(node.project.short),
  //     new Set()
  //   )
  // )
  const projectChoices = ["pta"];

  const [project, setProject] = useState(projectChoices[0]);



  const displayDate = formatUTC(relayObservationModel.observation.utcStart);

  const dataItems = formatSingleObservationData(
    relayObservationModel.observation
  );

  const isMolonglo = relayObservationModel.observation.project.mainProject.name
    .toLowerCase()
    .includes("monspsr");

  console.log(relayObservationModel);
  console.log(relayObservationModel.observation.calibration.idInt);
  return (
    <div className="single-observation">
      <h5 className="single-observation-subheading">{displayDate}</h5>
      <h5>Beam {relayObservationModel.observation.beam}</h5>
      <Row>
        <Col>
          <Button
            size="sm"
            as="a"
            className="mr-2"
            href={kronosLink(
              relayObservationModel.observation.beam,
              jname,
              displayDate
            )}
            variant="outline-secondary"
          >
            View Kronos
          </Button>
          <DownloadFluxcalButtons data={data} />
          <Button
            size="sm"
            as="a"
            className="mr-2"
            href={sessionLink(
              relayObservationModel.observation.calibration.idInt
            )}
            variant="outline-secondary"
          >
            View Observation Session
          </Button>
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
    </div>
  );
};

export default SingleObservationTable;
