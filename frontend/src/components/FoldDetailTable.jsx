import { Button, ButtonGroup, Col, Row } from "react-bootstrap";
import { useState } from "react";
import { graphql, useRefetchableFragment } from "react-relay";
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
  @refetchable(queryName: "FoldDetailTableRefetchQuery")
  @argumentDefinitions(
    pulsar: { type: "String" }
    mainProject: { type: "String", defaultValue: "MeerTIME" }
    dmCorrected: { type: "Boolean", defaultValue: false }
    minimumNsubs: { type: "Boolean", defaultValue: true }
    maximumNsubs: { type: "Boolean", defaultValue: true }
    obsNchan: { type: "Int", defaultValue: 1 }
    obsNpol: { type: "Int", defaultValue: 4 }
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
      allNchans
      edges {
        node {
          observation {
            id
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
            toas (
              dmCorrected: $dmCorrected,
              minimumNsubs: $minimumNsubs,
              maximumNsubs: $maximumNsubs,
              obsNchan: $obsNchan,
              obsNpol: $obsNpol,
            ){
              edges {
                node {
                  obsNchan
                  obsNpol
                  minimumNsubs
                  maximumNsubs
                  dmCorrected
                  freqMhz
                  length
                  project {
                    short
                  }
                  residual {
                    id
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
const FoldDetailTable = ({
  tableData,
  jname,
  mainProject,
  match: {
    location: { query },
  },
  setShow
}) => {

  console.log(
    "Input arguments:",
    jname,
    mainProject,
    query.dmCorrected,
    query.minimumNsubs,
    query.maximumNsubs,
    query.obsNchan,
    query.obsNpol
  );
  const [relayData, refetch] = useRefetchableFragment(FoldDetailTableFragment, tableData);
  console.log("data:", relayData);
  console.log("observationData:", relayData.observationSummary);
  console.log("pulsarFoldResult:", relayData.pulsarFoldResult);
  const summaryNode = relayData.observationSummary?.edges[0]?.node;
  const pulsarFoldResult = relayData.pulsarFoldResult;

  const { screenSize } = useScreenSize();
  const [dmCorrected, setDmCorrected ] = useState(query.dmCorrected || false );
  const [minimumNsubs, setMinimumNsubs] = useState(query.minimumNsubs || true);
  const [maximumNsubs, setMaximumNsubs] = useState(query.maximumNsubs || true);
  const [obsNchan, setObsNchan] = useState(query.obsNchan || 1);
  const [obsNpol, setObsNpol] = useState(query.obsNpol || 4);

  const handleRefetch = ({
    newDmCorrected = dmCorrected,
    newMinimumNsubs = minimumNsubs,
    newMaximumNsubs = maximumNsubs,
    newObsNchan = obsNchan,
    newObsNpol = obsNpol,
  } = {}) => {
    const url = new URL(window.location);
    url.searchParams.set("dmCorrected", newDmCorrected);
    url.searchParams.set("minimumNsubs", newMinimumNsubs);
    url.searchParams.set("maximumNsubs", newMaximumNsubs);
    url.searchParams.set("obsNchan", newObsNchan);
    url.searchParams.set("obsNpol", newObsNpol);
    window.history.pushState({}, "", url);
    console.log("Refetching with:", newDmCorrected, newMinimumNsubs, newMaximumNsubs, newObsNchan, newObsNpol);
    refetch({
      dmCorrected: newDmCorrected,
      minimumNsubs: newMinimumNsubs,
      maximumNsubs: newMaximumNsubs,
      obsNchan: newObsNchan,
      obsNpol: newObsNpol,
    });
  };

  const handleSetMaxNsub = (newMaximumNsubs) => {
    setMaximumNsubs(newMaximumNsubs === "true" ? true : false);
    handleRefetch({
      newMaximumNsubs: newMaximumNsubs,
    });
  };

  const handleSetNchan = (newObsNchan) => {
    setObsNchan(parseInt(newObsNchan, 10));
    handleRefetch({
      newObsNchan: newObsNchan,
    });
  };

  const handleSetNpol = (newObsNpol) => {
    setObsNpol(parseInt(newObsNpol, 10));
    handleRefetch({
      newObsNpol: newObsNpol,
    });
  };

  const allRows = pulsarFoldResult.edges.reduce(
    (result, edge) => [
      ...result,
      {
        ...edge.node,
        key: `${edge.node.observation.utcStart}:${edge.node.observation.beam}`,
        jname: jname,
        mainProject: mainProject,
        band: edge.node.observation.band,
        embargo: edge.node.observation.restricted
          ? "Embargoed until " +
            formatDDMonYYYY(edge.node.observation.embargoEndDate)
          : "",
        utc: formatUTC(edge.node.observation.utcStart),
        plotLink: `/${mainProject}/${jname}/${formatUTC(
          edge.node.observation.utcStart
        )}/${edge.node.observation.beam}/`,
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
              to={`/${mainProject}/${jname}/${formatUTC(
                edge.node.observation.utcStart
              )}/${edge.node.observation.beam}/`}
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

  console.log("pulsarFoldResult.allNchans", pulsarFoldResult.allNchans);

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
        allNchans={pulsarFoldResult.allNchans}
        setBand={handleBandFilter}
        maximumNsubs={maximumNsubs}
        handleSetMaxNsub={handleSetMaxNsub}
        obsNchan={obsNchan}
        handleSetNchan={handleSetNchan}
        obsNpol={obsNpol}
        handleSetNpol={handleSetNpol}
        plot
        mainProject={mainProject}
        keyField="key"
        card={FoldDetailCard}
      />
    </div>
  );
};

export default FoldDetailTable;
