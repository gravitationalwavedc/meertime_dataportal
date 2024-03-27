import { useState, Suspense } from "react";
import { graphql, useLazyLoadQuery } from "react-relay";
import SummaryDataRow from "../components/SummaryDataRow";
import FoldDetailFileDownload from "../components/FoldDetailFileDownload";
import FoldDetailTable from "../components/fold-detail-table/FoldDetailTable";
import HeaderButtons from "../components/fold-detail-table/HeaderButtons";
import MainLayout from "../components/MainLayout";
import PlotContainer from "../components/plots/PlotContainer";
import LoadingState from "../components/LoadingState";

const FoldDetailQuery = graphql`
  query FoldDetailQuery(
    $pulsar: String!
    $mainProject: String!
    $projectShort: String!
    $minimumNsubs: Boolean
    $maximumNsubs: Boolean
    $obsNchan: Int
    $obsNpol: Int
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
      description
      residualEphemeris {
        ephemerisData
        createdAt
      }
    }

    ...FoldDetailTableFragment
      @arguments(pulsar: $pulsar, mainProject: $mainProject)

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

const FoldDetail = ({ match }) => {
  const [downloadModalVisible, setDownloadModalVisible] = useState(false);
  const [filesLoaded, setFilesLoaded] = useState(false);

  const { jname, mainProject } = match.params;
  const urlQuery = match.location.query;

  const tableData = useLazyLoadQuery(FoldDetailQuery, {
    pulsar: jname,
    mainProject: mainProject,
    projectShort: match.location.query.timingProject || "All",
    minimumNsubs: true,
    maximumNsubs: false,
    obsNchan: 1,
    obsNpol: 1,
  });

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
      <HeaderButtons
        mainProject={mainProject}
        jname={jname}
        tableData={tableData}
        setDownloadModalVisible={setDownloadModalVisible}
        filesLoaded={filesLoaded}
      />
      <SummaryDataRow dataPoints={summaryData} />
      <Suspense fallback={<LoadingState />}>
        <PlotContainer
          toaData={tableData}
          urlQuery={urlQuery}
          jname={jname}
          mainProject={mainProject}
        />
      </Suspense>
      <Suspense fallback={<LoadingState />}>
        <FoldDetailTable
          tableData={tableData}
          mainProject={mainProject}
          jname={jname}
        />
      </Suspense>
      {localStorage.isStaff === "true" && (
        <Suspense>
          <FoldDetailFileDownload
            mainProject={mainProject}
            jname={jname}
            visible={downloadModalVisible}
            setShow={setDownloadModalVisible}
            setFilesLoaded={setFilesLoaded}
          />
        </Suspense>
      )}
    </MainLayout>
  );
};

export default FoldDetail;
