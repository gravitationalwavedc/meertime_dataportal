import { Button, ButtonGroup, Col, Row } from "react-bootstrap";
import { useState } from "react";
import {
  columnsSizeFilter,
  createLink,
  formatDDMonYYYY,
  formatUTC,
  meerWatchLink,
} from "../helpers";
import { meertime, molonglo } from "../telescopes";
import DataView from "./DataView";
import Ephemeris from "./Ephemeris";
import FileDownloadModal from "./FileDownloadModal";
import FoldDetailCard from "./FoldDetailCard";
import ReactMarkdown from "react-markdown";
import { Link } from "found";
import { useScreenSize } from "../context/screenSize-context";

/* eslint-disable complexity */
const FoldDetailTable = ({
  data: { observationSummary, pulsarFoldResult },
  jname,
  project,
}) => {
  const { screenSize } = useScreenSize();
  const summaryNode = observationSummary.edges[0]?.node;
  const allRows = pulsarFoldResult.edges.reduce(
    (result, edge) => [
      ...result,
      {
        ...edge.node,
        key: `${edge.node.observation.utcStart}:${edge.node.observation.beam}`,
        jname: jname,
        band: edge.node.observation.band,
        embargo: edge.node.restricted
          ? "Embargoed until " + formatDDMonYYYY(edge.node.embargoEndDate)
          : "",
        utc: formatUTC(edge.node.observation.utcStart),
        plotLink: `/${jname}/${formatUTC(edge.node.observation.utcStart)}/${edge.node.observation.beam}/`,
        action: edge.node.restricted ? (
          <Button size="sm" variant="outline-dark">
            <span className="small">
              Embargoed
              <br />
              until
              <br />
              {formatDDMonYYYY(edge.node.embargoEndDate)}
            </span>
          </Button>
        ) : (
          <ButtonGroup vertical>
            <Link
              to={`/${jname}/${formatUTC(edge.node.observation.utcStart)}/${edge.node.observation.beam}/`}
              size="sm"
              variant="outline-secondary"
              as={Button}
            >
              View
            </Link>
            <Link
              to={`/session/${formatUTC(edge.node.observation.utcStart)}/`}
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
  const [downloadModalVisible, setDownloadModalVisible] = useState(false);

  const ephemeris        = pulsarFoldResult.residualEphemeris ? pulsarFoldResult.residualEphemeris.ephemerisData : null;
  const ephemerisUpdated = pulsarFoldResult.residualEphemeris ? pulsarFoldResult.residualEphemeris.createdAt     : null;

  const columns =
    project === "MONSPSR" ? molonglo.columns : meertime.columns;

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
    { title: `Size [GB]`, value: summaryNode.estimatedDiskSpaceGb.toFixed(1) },
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
          {project !== "MONSPSR" && (
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
          {localStorage.isStaff === "true" &&
            pulsarFoldResult.toasLink && (
              <Button
                size="sm"
                className="mr-2 mb-2"
                variant="outline-secondary"
                onClick={() => createLink(pulsarFoldResult.toasLink)}
              >
                Download TOAs
              </Button>
            )}
          {/* {localStorage.isStaff === "true" &&
            foldPulsar.files.edges.length > 0 && (
              <Button
                size="sm"
                className="mr-2 mb-2"
                variant="outline-secondary"
                onClick={() => setDownloadModalVisible(true)}
              >
                Download data files
              </Button>
            )} */}
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
      {/* {localStorage.isStaff === "true" && foldPulsar.files && (
        <FileDownloadModal
          visible={downloadModalVisible}
          files={foldPulsar.files}
          setShow={setDownloadModalVisible}
        />
      )} */}
      <DataView
        summaryData={summaryData}
        columns={columnsSizeFiltered}
        rows={rows}
        setProject={handleProjectFilter}
        setBand={handleBandFilter}
        plot
        maxPlotLength={summaryNode.maxDuration}
        minPlotLength={summaryNode.minDuration}
        project={project}
        keyField="key"
        card={FoldDetailCard}
      />
    </div>
  );
};

export default FoldDetailTable;
