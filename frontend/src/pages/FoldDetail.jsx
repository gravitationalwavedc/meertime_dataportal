import { useState } from "react";
import { graphql, useLazyLoadQuery } from "react-relay";
import { Button, Col, Row } from "react-bootstrap";
import SummaryDataRow from "../components/SummaryDataRow";
import FoldDetailFileDownload from "../components/FoldDetailFileDownload";
import TanTableTest from "../components/fold-detail-table/TanTableTest";
import MainLayout from "../components/MainLayout";
import Ephemeris from "../components/Ephemeris";
import PlotContainer from "../components/plots/PlotContainer";
import { createLink, meerWatchLink } from "../helpers";

const FoldDetailQuery = graphql`
  query FoldDetailQuery($pulsar: String!, $mainProject: String) {
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
      description
      residualEphemeris {
        ephemerisData
        createdAt
      }
    }

    ...FoldDetailTableFragment
      @arguments(pulsar: $pulsar, mainProject: $mainProject)

    ...TanTableTestFragment
      @arguments(pulsar: $pulsar, mainProject: $mainProject)
  }
`;

const PlotContainerQuery = graphql`
  query FoldDetailPlotContainerQuery(
    $pulsar: String!
    $mainProject: String
    $projectShort: String
    $minimumNsubs: Boolean
    $maximumNsubs: Boolean
    $obsNchan: Int
    $obsNpol: Int
  ) {
    ...PlotContainerFragment
      @arguments(
        pulsar: $pulsar
        mainProject: $mainProject
        projectShort: $projectShort
        minimumNsubs: $minimumNsubs
        maximumNsubs: $maximumNsubs
        obsNchan: $obsNchan
        obsNpol: $obsNpol
      )
  }
`;

const FoldDetailFileDownloadQuery = graphql`
  query FoldDetailFileDownloadQuery($mainProject: String!, $pulsar: String!) {
    ...FoldDetailFileDownloadFragment
      @arguments(mainProject: $mainProject, jname: $pulsar)
  }
`;

const FoldDetail = ({ match }) => {
  const { jname, mainProject } = match.params;
  const urlQuery = match.location.query;

  const tableData = useLazyLoadQuery(FoldDetailQuery, {
    pulsar: jname,
    mainProject: mainProject,
  });

  const toaData = useLazyLoadQuery(PlotContainerQuery, {
    pulsar: jname,
    mainProject: mainProject,
    projectShort: match.location.query.timingProject || "All",
    minimumNsubs: true,
    maximumNsubs: false,
    obsNchan: 1,
    obsNpol: 1,
  });

  const fileDownloadData = useLazyLoadQuery(FoldDetailFileDownloadQuery, {
    mainProject: mainProject,
    pulsar: jname,
  });

  const [ephemerisVisible, setEphemerisVisible] = useState(false);
  const [downloadModalVisible, setDownloadModalVisible] = useState(false);

  const ephemeris = tableData.pulsarFoldResult.residualEphemeris
    ? tableData.pulsarFoldResult.residualEphemeris.ephemerisData
    : null;

  const ephemerisUpdated = tableData.pulsarFoldResult.residualEphemeris
    ? tableData.pulsarFoldResult.residualEphemeris.createdAt
    : null;

  const summaryNode = tableData.observationSummary?.edges[0]?.node;

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
    <MainLayout
      title={jname}
      description={tableData.pulsarFoldResult.description}
    >
      <Row>
        <Col>
          <Button
            size="sm"
            variant="outline-secondary"
            className="mr-2 mb-2"
            disabled={!ephemeris}
            onClick={() => setEphemerisVisible(true)}
          >
            {ephemeris === null
              ? "Folding ephemeris unavailable"
              : "View folding ephemeris"}
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
            tableData.pulsarFoldResult.ephemerisLink && (
              <Button
                size="sm"
                className="mr-2 mb-2"
                variant="outline-secondary"
                onClick={() =>
                  createLink(tableData.pulsarFoldResult.ephemerisLink)
                }
              >
                Download ephemeris
              </Button>
            )}
          {localStorage.isStaff === "true" &&
            tableData.pulsarFoldResult.toasLink && (
              <Button
                size="sm"
                className="mr-2 mb-2"
                variant="outline-secondary"
                onClick={() => createLink(tableData.pulsarFoldResult.toasLink)}
              >
                Download TOAs
              </Button>
            )}
          {localStorage.isStaff === "true" && (
            <Button
              size="sm"
              className="mr-2 mb-2"
              variant="outline-secondary"
              onClick={() => setDownloadModalVisible(true)}
            >
              Download data files
            </Button>
          )}
        </Col>
        {ephemeris && (
          <Ephemeris
            ephemeris={ephemeris}
            updated={ephemerisUpdated}
            show={ephemerisVisible}
            setShow={setEphemerisVisible}
          />
        )}
      </Row>
      <SummaryDataRow dataPoints={summaryData} />
      <Row className="d-none d-sm-block">
        <PlotContainer
          toaData={toaData}
          urlQuery={urlQuery}
          jname={jname}
          mainProject={mainProject}
        />
      </Row>
      <TanTableTest
        tableData={tableData}
        mainProject={mainProject}
        jname={jname}
      />
      {localStorage.isStaff === "true" && (
        <FoldDetailFileDownload
          visible={downloadModalVisible}
          data={fileDownloadData}
          setShow={setDownloadModalVisible}
        />
      )}
    </MainLayout>
  );
};

export default FoldDetail;
