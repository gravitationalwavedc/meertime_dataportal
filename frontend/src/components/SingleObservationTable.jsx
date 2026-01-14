import { Button, Col, Row } from "react-bootstrap";
import { graphql, useFragment } from "react-relay";
import {
  formatUTC,
  kronosLink,
  sessionLink,
  generateObservationUrl,
} from "../helpers";
import DataDisplay from "./DataDisplay";
import ImageGrid from "./ImageGrid";
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
          nextObservation {
            observation {
              utcStart
              beam
            }
          }
          previousObservation {
            observation {
              utcStart
              beam
            }
          }
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

const SingleObservationTable = ({ observationData, jname }) => {
  const relayData = useFragment(
    SingleObservationTableFragment,
    observationData
  );
  const { pulsarFoldResult } = relayData;
  const relayObservationModel = pulsarFoldResult.edges[0].node;

  const displayDate = formatUTC(relayObservationModel.observation.utcStart);

  const previousObservationUrl = relayObservationModel.previousObservation
    ? generateObservationUrl(
        relayObservationModel.observation.project.mainProject.name,
        jname,
        relayObservationModel.previousObservation.observation
      )
    : null;

  const nextObservationUrl = relayObservationModel.nextObservation
    ? generateObservationUrl(
        relayObservationModel.observation.project.mainProject.name,
        jname,
        relayObservationModel.nextObservation.observation
      )
    : null;

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
    SNR:
      relayObservationModel.pipelineRun.sn !== null
        ? relayObservationModel.pipelineRun.sn.toFixed(1)
        : null,
    "DM (pc cm^-3)":
      relayObservationModel.pipelineRun.dm !== null
        ? relayObservationModel.pipelineRun.dm.toFixed(6)
        : null,
    "RM (rad m^-2)":
      relayObservationModel.pipelineRun.rm !== null
        ? relayObservationModel.pipelineRun.rm.toFixed(4)
        : null,
  };

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
          {previousObservationUrl && (
            <Button
              size="sm"
              as="a"
              className="mr-2 mb-2"
              href={previousObservationUrl}
              variant="outline-secondary"
            >
              View Previous
            </Button>
          )}
          {nextObservationUrl && (
            <Button
              size="sm"
              as="a"
              className="mr-2 mb-2"
              href={nextObservationUrl}
              variant="outline-secondary"
            >
              View Next
            </Button>
          )}
          <SingleObservationFileDownload
            jname={jname}
            utc={formatUTC(relayObservationModel.observation.utcStart)}
            beam={relayObservationModel.observation.beam}
            mainProject={
              relayObservationModel.observation.project.mainProject.name
            }
          />
        </Col>
      </Row>
      <Row>
        <Col>
          <ImageGrid images={relayObservationModel.images} />
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
