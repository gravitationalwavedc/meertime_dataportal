import { Button, Col, Form, Row } from "react-bootstrap";
import { useState } from "react";
import { graphql, useFragment } from "react-relay";
import { formatProjectName } from "../helpers";
import { formatUTC, kronosLink, sessionLink } from "../helpers";
import DataDisplay from "./DataDisplay";
import ImageGrid from "./ImageGrid";
import MolongloImageGrid from "./MolongloImageGrid";
import SingleObservationFileDownload from "./SingleObservationFileDownload";

const SingleObservationTableFragment = graphql`
  fragment SingleObservationTableFragment on Query
  @argumentDefinitions(
    pulsar: { type: "String!" }
    utc: { type: "String!" }
    beam: { type: "Int!" }
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
              code
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
          pipelineRun {
            dm
            rm
            sn
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
  const [downloadModalVisible, setDownloadModalVisible] = useState(false);

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

  const dataItems = {
    Project:
      relayObservationModel.observation.project.code +
      " (" +
      relayObservationModel.observation.project.short +
      ")",
    "Duration (seconds)": relayObservationModel.observation.duration.toFixed(2),
    "Frequency (MHz)": relayObservationModel.observation.frequency.toFixed(2),
    "Bandwidth (MHz)": relayObservationModel.observation.bandwidth.toFixed(2),
    RA: relayObservationModel.observation.raj,
    DEC: relayObservationModel.observation.decj,
    "Number of Antennas": relayObservationModel.observation.nant,
    Nbin: relayObservationModel.observation.foldNbin,
    Nchan: relayObservationModel.observation.foldNchan,
    "Subint Time (s)": relayObservationModel.observation.foldTsubint,
    "SNR": relayObservationModel.pipelineRun.sn !== null ? relayObservationModel.pipelineRun.sn.toFixed(1) : null,
    "DM (pc cm^-3)": relayObservationModel.pipelineRun.dm !== null ? relayObservationModel.pipelineRun.dm.toFixed(4) : null,
    "RM (rad m^-2)": relayObservationModel.pipelineRun.rm !== null ? relayObservationModel.pipelineRun.rm.toFixed(4) : null,
  };

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
            className="mr-2 mb-2"
            href={kronosLink(
              relayObservationModel.observation.beam,
              jname,
              displayDate
            )}
            variant="outline-secondary"
          >
            View Kronos
          </Button>
          <Button
            size="sm"
            as="a"
            className="mr-2 mb-2"
            href={sessionLink(
              relayObservationModel.observation.calibration.idInt
            )}
            variant="outline-secondary"
          >
            View Observation Session
          </Button>
          {localStorage.isStaff === "true" && (
            <Button
              size="sm"
              className="mr-2 mb-2"
              variant="outline-secondary"
              onClick={() => setDownloadModalVisible(true)}
            >
              Download Data Files
            </Button>
          )}
        </Col>
      </Row>
      {localStorage.isStaff === "true" && (
        <SingleObservationFileDownload
          visible={downloadModalVisible}
          data={data}
          setShow={setDownloadModalVisible}
        />
      )}
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
