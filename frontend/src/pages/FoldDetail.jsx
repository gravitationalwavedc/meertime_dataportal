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
  query FoldDetailQuery($pulsar: String!, $mainProject: String!) {
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
      edges {
        node {
          pipelineRun {
            sn
            badges {
              edges {
                node {
                  name
                }
              }
            }
            observation {
              calibration {
                badges {
                  edges {
                    node {
                      name
                    }
                  }
                }
              }
            }
          }
        }
      }
    }

    toa(
      pulsar: $pulsar
      mainProject: $mainProject
      minimumNsubs: true
      obsNchan: 1
      obsNpol: 1
    ) {
      allProjects
    }

    badge {
      edges {
        node {
          name
          description
        }
      }
    }

    ...FoldDetailTableFragment
      @arguments(pulsar: $pulsar, mainProject: $mainProject)
  }
`;

const FoldDetailPlotQuery = graphql`
  query FoldDetailPlotQuery(
    $pulsar: String!
    $mainProject: String!
    $projectShort: String!
    $minimumNsubs: Boolean
    $maximumNsubs: Boolean
    $obsNchan: Int
    $obsNpol: Int
    $excludeBadges: [String]
    $minimumSNR: Float
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
        excludeBadges: $excludeBadges
        minimumSNR: $minimumSNR
      )
  }
`;

const FoldDetail = ({ match }) => {
  const urlQuery = match.location.query;
  const [downloadModalVisible, setDownloadModalVisible] = useState(false);
  const [filesLoaded, setFilesLoaded] = useState(false);
  const [minimumSNR, setMinimumSNR] = useState(urlQuery.minSNR || 8);
  const [observationBadges, setObservationBadges] = useState({
    "Session Timing Jump": true,
    "Session Sensitivity Reduction": true,
    "Strong RFI": true,
    "RM Drift": false,
    "DM Drift": true,
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

  const handleMinimumSNRToggle = (e) => {
    const minimumSNR = e.target.value;
    const url = new URL(window.location);
    url.searchParams.set("minSNR", minimumSNR);
    window.history.pushState({}, "", url);
    setMinimumSNR(minimumSNR);
  };

  const { jname, mainProject } = match.params;

  const tableData = useLazyLoadQuery(FoldDetailQuery, {
    pulsar: jname,
    mainProject: mainProject,
  });

  const timingProjects = tableData.toa.allProjects;

  const [projectShort, setProjectShort] = useState(
    urlQuery.timingProject || timingProjects[0]
  );
  const [obsNchan, setObsNchan] = useState(urlQuery.obsNchan || 1);
  const [obsNpol, setObsNpol] = useState(urlQuery.obsNpol || 1);
  const [nsubType, setNsubType] = useState(urlQuery.nsubType || "1");
  const nsubTypeBools = getNsubTypeBools(nsubType);

  const plotData = useLazyLoadQuery(FoldDetailPlotQuery, {
    pulsar: jname,
    mainProject: mainProject,
    projectShort: projectShort,
    minimumNsubs: nsubTypeBools.minimumNsubs,
    maximumNsubs: nsubTypeBools.maximumNsubs,
    modeNsubs: nsubTypeBools.modeNsubs,
    obsNchan: obsNchan,
    obsNpol: obsNpol,
    excludeBadges: excludeBadges,
    minimumSNR: minimumSNR,
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

  let totalBadgeExcludedObservations = 0;
  for (const pfrNode of tableData.pulsarFoldResult.edges) {
    for (const badgeNode of pfrNode.node.pipelineRun.badges.edges) {
      if (excludeBadges.includes(badgeNode.node.name)) {
        totalBadgeExcludedObservations += 1;
      }
    }
    for (const sessionNode of pfrNode.node.pipelineRun.observation.calibration
      .badges.edges) {
      if (excludeBadges.includes(sessionNode.node.name)) {
        totalBadgeExcludedObservations += 1;
      }
    }
    if (pfrNode.node.pipelineRun.sn < minimumSNR) {
      totalBadgeExcludedObservations += 1;
    }
  }

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
        minimumSNR={minimumSNR}
        handleMinimumSNRToggle={handleMinimumSNRToggle}
        totalBadgeExcludedObservations={totalBadgeExcludedObservations}
        badgeData={tableData.badge.edges}
      />
      <Suspense
        fallback={
          <div>
            <h3>Loading...</h3>
          </div>
        }
      >
        <PlotContainer
          toaData={plotData}
          jname={jname}
          mainProject={mainProject}
          timingProjects={timingProjects}
          projectShort={projectShort}
          setProjectShort={setProjectShort}
          obsNchan={obsNchan}
          setObsNchan={setObsNchan}
          obsNpol={obsNpol}
          setObsNpol={setObsNpol}
          nsubType={nsubType}
          setNsubType={setNsubType}
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
          minimumSNR={minimumSNR}
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
