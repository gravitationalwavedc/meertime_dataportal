import { Button, ButtonGroup, Col, Row } from "react-bootstrap";
import { useState } from "react";
import { graphql, useFragment } from "react-relay";
import ReactMarkdown from "react-markdown";
import { Link } from "found";
import {
  columnsSizeFilter,
  createLink,
  formatDDMonYYYY,
  formatUTC,
  meerWatchLink,
} from "../helpers";
import { useScreenSize } from "../context/screenSize-context";
import { meertime, molonglo } from "../telescopes";
import DataView from "./DataView";
import Ephemeris from "./Ephemeris";
import FoldDetailCard from "./FoldDetailCard";

const FoldDetailTableFragment = graphql`
  fragment FoldDetailTableFragment on Query
  @argumentDefinitions(
    pulsar: { type: "String", defaultValue: "All" }
    mainProject: { type: "String", defaultValue: "MeerTIME" }
    dmCorrected: { type: "Boolean", defaultValue: false }
    minimumNsubs: { type: "Boolean", defaultValue: true }
    obsNchan: { type: "Int", defaultValue: 1 }
  ) {
    observationSummary(
      pulsar_Name: $pulsar
      obsType: "fold"
      calibration_Id: "All"
      mainProject: $mainProject
      project_Short: "All"
      band: "All"
    ) {
      edges {
        node {
          observations
          observationHours
          projects
          pulsars
          estimatedDiskSpaceGb
          timespanDays
          maxDuration
          minDuration
        }
      }
    }
    pulsarFoldResult(pulsar: $pulsar, mainProject: $mainProject) {
      residualEphemeris {
        ephemerisData
        createdAt
      }
      description
      toasLink
      allProjects
      edges {
        node {
          observation {
            utcStart
            dayOfYear
            binaryOrbitalPhase
            duration
            beam
            bandwidth
            nchan
            band
            foldNbin
            nant
            nantEff
            restricted
            embargoEndDate
            project {
              short
            }
            ephemeris {
              dm
            }
            calibration {
              idInt
            }
            toas(
              dmCorrected: $dmCorrected
              minimumNsubs: $minimumNsubs
              obsNchan: $obsNchan
            ) {
              edges {
                node {
                  freqMhz
                  length
                  project {
                    short
                  }
                  residual {
                    mjd
                    dayOfYear
                    binaryOrbitalPhase
                    residualSec
                    residualSecErr
                    residualPhase
                    residualPhaseErr
                  }
                }
              }
            }
          }
          pipelineRun {
            dm
            dmErr
            rm
            rmErr
            sn
            flux
          }
        }
      }
    }
  }
`;

/* eslint-disable complexity */
const FoldDetailTable = ({ tableData, jname, mainProject, setShow }) => {
  const dmCorrected = false;
  const minimumNsubs = true;
  const obsNchan = 1;
  console.log(
    "Input arguments:",
    jname,
    mainProject,
    dmCorrected,
    minimumNsubs,
    obsNchan
  );
  console.log("tableData:", tableData);
  const relayData = useFragment(FoldDetailTableFragment, tableData);
  console.log("data:", relayData);
  console.log("observationData:", relayData.observationSummary);
  console.log("pulsarFoldResult:", relayData.pulsarFoldResult);
  const summaryNode = relayData.observationSummary?.edges[0]?.node;
  const pulsarFoldResult = relayData.pulsarFoldResult;
  const { screenSize } = useScreenSize();
  const allRows = pulsarFoldResult.edges.reduce(
    (result, edge) => [
      ...result,
      {
        ...edge.node,
        key: `${edge.node.observation.utcStart}:${edge.node.observation.beam}`,
        jname: jname,
        band: edge.node.observation.band,
        embargo: edge.node.observation.restricted
          ? "Embargoed until " +
            formatDDMonYYYY(edge.node.observation.embargoEndDate)
          : "",
        utc: formatUTC(edge.node.observation.utcStart),
        plotLink: `/${jname}/${formatUTC(edge.node.observation.utcStart)}/${
          edge.node.observation.beam
        }/`,
        action: edge.node.observation.restricted ? (
          <Button size="sm" variant="outline-dark">
            <span className="small">
              Embargoed
              <br />
              until
              <br />
              {formatDDMonYYYY(edge.node.observation.embargoEndDate)}
            </span>
          </Button>
        ) : (
          <ButtonGroup vertical>
            <Link
              to={`/${jname}/${formatUTC(edge.node.observation.utcStart)}/${
                edge.node.observation.beam
              }/`}
              size="sm"
              variant="outline-secondary"
              as={Button}
            >
              View
            </Link>
            <Link
              to={`/session/${edge.node.observation.calibration.idInt}/`}
              size="sm"
              variant="outline-secondary"
              as={Button}
            >
              View session
            </Link>
          </ButtonGroup>
        ),
      },
    ],
    []
  );

  const [rows, setRows] = useState(allRows);
  const [ephemerisVisible, setEphemerisVisible] = useState(false);

  const ephemeris = pulsarFoldResult.residualEphemeris
    ? pulsarFoldResult.residualEphemeris.ephemerisData
    : null;
  const ephemerisUpdated = pulsarFoldResult.residualEphemeris
    ? pulsarFoldResult.residualEphemeris.createdAt
    : null;

  const columns =
    mainProject === "MONSPSR" ? molonglo.columns : meertime.columns;

  const columnsSizeFiltered = columnsSizeFilter(columns, screenSize);

  const handleBandFilter = (band) => {
    if (band.toLowerCase() === "all") {
      setRows(allRows);
      return;
    }

    const newRows = allRows.filter(
      (row) => row.band.toLowerCase() === band.toLowerCase()
    );
    setRows(newRows);
  };

  const handleProjectFilter = (project) => {
    if (project === "All") {
      setRows(allRows);
      return;
    }

    const newRows = allRows.filter(
      (row) => row.project.toLowerCase() === project.toLowerCase()
    );
    setRows(newRows);
  };

  const summaryData = [
    { title: "Observations", value: summaryNode.observations },
    { title: "Projects", value: summaryNode.projects },
    {
      title: "Timespan [days]",
      value: summaryNode.timespanDays,
    },
    { title: "Hours", value: summaryNode.observationHours },
    summaryNode.estimatedDiskSpaceGb
      ? {
          title: `Size [GB]`,
          value: summaryNode.estimatedDiskSpaceGb.toFixed(1),
        }
      : { title: `Size [GB]`, value: summaryNode.estimatedDiskSpaceGb },
  ];

  return (
    <div className="fold-detail-table">
      <Row className="mb-3">
        <Col md={5}>
          <ReactMarkdown>{pulsarFoldResult.description}</ReactMarkdown>
        </Col>
      </Row>
      <Row>
        <Col>
          <Button
            size="sm"
            variant="outline-secondary"
            className="mr-2 mb-2"
            disabled={!ephemeris}
            onClick={() => setEphemerisVisible(true)}
          >
            {ephemeris
              ? "View folding ephemeris"
              : "Folding ephemeris unavailable"}
          </Button>
          {mainProject !== "MONSPSR" && (
            <Button
              size="sm"
              className="mr-2 mb-2"
              as="a"
              href={meerWatchLink(jname)}
              variant="outline-secondary"
            >
              View MeerWatch
            </Button>
          )}
          {localStorage.isStaff === "true" &&
            pulsarFoldResult.ephemerisLink && (
              <Button
                size="sm"
                className="mr-2 mb-2"
                variant="outline-secondary"
                onClick={() => createLink(pulsarFoldResult.ephemerisLink)}
              >
                Download ephemeris
              </Button>
            )}
          {localStorage.isStaff === "true" && pulsarFoldResult.toasLink && (
            <Button
              size="sm"
              className="mr-2 mb-2"
              variant="outline-secondary"
              onClick={() => createLink(pulsarFoldResult.toasLink)}
            >
              Download TOAs
            </Button>
          )}
          {localStorage.isStaff === "true" && (
            <Button
              size="sm"
              className="mr-2 mb-2"
              variant="outline-secondary"
              onClick={() => setShow(true)}
            >
              Download data files
            </Button>
          )}
        </Col>
      </Row>
      {ephemeris && (
        <Ephemeris
          ephemeris={ephemeris}
          updated={ephemerisUpdated}
          show={ephemerisVisible}
          setShow={setEphemerisVisible}
        />
      )}
      <DataView
        summaryData={summaryData}
        columns={columnsSizeFiltered}
        rows={rows}
        setProject={handleProjectFilter}
        timingProjects={pulsarFoldResult.allProjects}
        setBand={handleBandFilter}
        plot
        mainProject={mainProject}
        keyField="key"
        card={FoldDetailCard}
      />
    </div>
  );
};

export default FoldDetailTable;
