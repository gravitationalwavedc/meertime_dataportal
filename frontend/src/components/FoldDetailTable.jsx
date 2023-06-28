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
  data: { foldPulsarResult },
  jname,
  project,
}) => {
  const { screenSize } = useScreenSize();
  const allRows = foldPulsarResult.edges.reduce(
    (result, edge) => [
      ...result,
      {
        ...edge.node,
        key: `${edge.node.observation.utc_start}:${edge.node.observation.beam}`,
        jname: jname,
        embargo: edge.node.restricted
          ? "Embargoed until " + formatDDMonYYYY(edge.node.embargoEndDate)
          : "",
        utc: formatUTC(edge.node.observation.utc_start),
        plotLink: `/${jname}/${formatUTC(edge.node.observation.utc_start)}/${edge.node.beam}/`,
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
              to={`/${jname}/${formatUTC(edge.node.observation.utc_start)}/${edge.node.beam}/`}
              size="sm"
              variant="outline-secondary"
              as={Button}
            >
              View
            </Link>
            <Link
              to={`/session/${formatUTC(edge.node.observation.utc_start)}/`}
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

  const ephemeris =
    foldPulsarResult.edges[foldPulsarResult.edges.length - 1].node
      .ephemeris;
  const ephemerisUpdated =
    foldPulsarResult.edges[foldPulsarResult.edges.length - 1].node
      .ephemerisIsUpdatedAt;

  const columns =
    project === "MONSPSR" ? molonglo.columns : meertime.columns;

  const columnsSizeFiltered = columnsSizeFilter(columns, screenSize);

  // totalEstimatedDiskSpace is a human readable formatted byte string in the form of "900.2\u00a0MB".
  // We split on this character so we can use the number and the units separately.
  const [size, sizeFormat] =
    foldPulsarResult.totalEstimatedDiskSpace.split("\u00a0");

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
    { title: "Observations", value: foldPulsarResult.totalObservations },
    { title: "Projects", value: foldPulsarResult.totalProjects },
    {
      title: "Timespan [days]",
      value: foldPulsarResult.totalTimespanDays,
    },
    { title: "Hours", value: foldPulsarResult.totalObservationHours },
    { title: `Size [${sizeFormat}]`, value: size },
  ];

  return (
    <div className="fold-detail-table">
      <Row className="mb-3">
        <Col md={5}>
          <ReactMarkdown>{foldPulsarResult.description}</ReactMarkdown>
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
            foldPulsarResult.ephemerisLink && (
              <Button
                size="sm"
                className="mr-2 mb-2"
                variant="outline-secondary"
                onClick={() => createLink(foldPulsarResult.ephemerisLink)}
              >
                Download ephemeris
              </Button>
            )}
          {localStorage.isStaff === "true" &&
            foldPulsarResult.toasLink && (
              <Button
                size="sm"
                className="mr-2 mb-2"
                variant="outline-secondary"
                onClick={() => createLink(foldPulsarResult.toasLink)}
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
        maxPlotLength={foldPulsarResult.maxPlotLength}
        minPlotLength={foldPulsarResult.minPlotLength}
        project={project}
        keyField="key"
        card={FoldDetailCard}
      />
    </div>
  );
};

export default FoldDetailTable;
