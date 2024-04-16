import { useState, Suspense } from "react";
import { graphql, useLazyLoadQuery } from "react-relay";
import SummaryDataRow from "../components/SummaryDataRow";
import FoldDetailFileDownload from "../components/FoldDetailFileDownload";
import ObservationFlags from "../components/fold-detail/ObservationFlags";
import FoldDetailTable from "../components/fold-detail/FoldDetailTable";
import HeaderButtons from "../components/fold-detail/HeaderButtons";
import MainLayout from "../components/MainLayout";
import PlotContainer from "../components/plots/PlotContainer";
import { getNsubTypeBools } from "../components/plots/plotData";

const FoldDetailQuery = graphql`
  query FoldDetailQuery(
    $pulsar: String!
    $mainProject: String!
    $projectShort: String!
    $minimumNsubs: Boolean
    $maximumNsubs: Boolean
    $obsNchan: Int
    $obsNpol: Int
    $excludeBadges: [String]
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

    pulsarFoldResult(
      pulsar: $pulsar
      mainProject: $mainProject
      excludeBadges: $excludeBadges
    ) {
      description
      residualEphemeris {
        ephemerisData
        createdAt
      }
      totalBadgeExcludedObservations
    }

    ...FoldDetailTableFragment
      @arguments(
        pulsar: $pulsar
        mainProject: $mainProject
        excludeBadges: $excludeBadges
      )

    ...PlotContainerFragment
      @arguments(
        pulsar: $pulsar
        mainProject: $mainProject
        projectShort: $projectShort
        minimumNsubs: $minimumNsubs
        maximumNsubs: $maximumNsubs
        obsNchan: $obsNchan
        obsNpol: $obsNpol
        excludeBadges: $excludeBadges
      )
  }
`;

const FoldDetail = ({ match }) => {
  const [downloadModalVisible, setDownloadModalVisible] = useState(false);
  const [filesLoaded, setFilesLoaded] = useState(false);
  const [observationBadges, setObservationBadges] = useState({
    "Strong RFI": false,
    "RM Drift": false,
    "DM Drift": false,
  });
  const excludeBadges = Object.keys(observationBadges).filter(
    (observationBadge) => observationBadges[observationBadge]
  );

  const handleObservationFlagToggle = (observationBadge) => {
    const newObservationBadges = {
      ...observationBadges,
      [observationBadge]: !observationBadges[observationBadge],
    };
    setObservationBadges(newObservationBadges);
  };

  const { jname, mainProject } = match.params;
  const urlQuery = match.location.query;
  const nsubTypeBools = getNsubTypeBools(urlQuery.nsubType);

  const tableData = useLazyLoadQuery(FoldDetailQuery, {
    pulsar: jname,
    mainProject: mainProject,
    projectShort: urlQuery.timingProject || "All",
    minimumNsubs: nsubTypeBools.minimumNsubs,
    maximumNsubs: nsubTypeBools.maximumNsubs,
    modeNsubs: nsubTypeBools.modeNsubs,
    obsNchan: urlQuery.obsNchan || 1,
    obsNpol: urlQuery.obsNpol || 1,
    excludeBadges: excludeBadges,
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

  const totalBadgeExcludedObservations =
    tableData.pulsarFoldResult.totalBadgeExcludedObservations;

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
      <ObservationFlags
        observationBadges={observationBadges}
        handleObservationFlagToggle={handleObservationFlagToggle}
        totalBadgeExcludedObservations={totalBadgeExcludedObservations}
      />
      <Suspense
        fallback={
          <div>
            <h3>Loading...</h3>
          </div>
        }
      >
        <PlotContainer
          toaData={tableData}
          urlQuery={urlQuery}
          jname={jname}
          mainProject={mainProject}
        />
      </Suspense>
      <Suspense
        fallback={
          <div>
            <h3>Loading...</h3>
          </div>
        }
      >
        <FoldDetailTable
          tableData={tableData}
          mainProject={mainProject}
          jname={jname}
          excludeBadges={excludeBadges}
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
