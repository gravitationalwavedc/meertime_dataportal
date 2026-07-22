import HeaderButtons from "../components/fold-detail/HeaderButtons";
import MainLayout from "../components/MainLayout";
import SummaryDataRow from "../components/SummaryDataRow";
import FoldDetailTable from "../components/fold-detail/FoldDetailTable";
import { graphql } from "relay-runtime";
import { useLazyLoadQuery } from "react-relay";
import PlotContainer from "../components/plots/PlotContainer";
import { useState } from "react";
import { selectCanonicalObservationSummaryNode, toApiFilter } from "../helpers";
import { useAuth } from "../auth/AuthContext";
import { useProjectConfig } from "../context/project-config-context";
import { mainProjectAllowsDownloads } from "../project-config";

const foldDetailQuery = graphql`
  query FoldDetailQuery(
    $pulsar: String!
    $mainProject: String
    $excludeBadges: [String]
    $minimumSNR: Float
    $first: Int = 5000
  ) {
    pulsarFoldResult(
      pulsar: $pulsar
      mainProject: $mainProject
      excludeBadges: $excludeBadges
      minimumSNR: $minimumSNR
      first: $first
    ) {
      description
      toasLink
      allProjects
      mostCommonProject
      allNchans
      edges {
        node {
          observation {
            restricted
            embargoEndDate
            project {
              short
              code
              mainProject {
                name
              }
            }
          }
        }
      }
    }
    observationSummary(
      pulsar_Name: $pulsar
      obsType: "fold"
      calibrationIsnull: true
      mainProject: $mainProject
      projectIsnull: true
      bandIsnull: true
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

    ...FoldDetailTableFragment
      @arguments(
        pulsar: $pulsar
        mainProject: $mainProject
        excludeBadges: $excludeBadges
        minimumSNR: $minimumSNR
        first: $first
      )
  }
`;

const FoldDetail = ({ match }) => {
  const { jname, mainProject, minSNR } = match.params;
  const { isAuthenticated } = useAuth();
  const { projects } = useProjectConfig();

  const [excludeBadges, setExcludeBadges] = useState([
    "Session Timing Jump",
    "RM Drift",
    "Bad online folding",
  ]);
  const [minimumSNR, setMinimumSNR] = useState(minSNR ? Number(minSNR) : 8);

  const data = useLazyLoadQuery(foldDetailQuery, {
    pulsar: toApiFilter(jname),
    mainProject: toApiFilter(mainProject),
    first: 5000,
  });

  const firstObservation = data.pulsarFoldResult?.edges?.[0]?.node?.observation;
  const restricted = firstObservation?.restricted ?? false;
  const embargoEndDate = firstObservation?.embargoEndDate ?? null;
  const projectShort = firstObservation?.project?.short ?? "";
  const selectedMainProject =
    firstObservation?.project?.mainProject?.name ?? mainProject;
  const allowDownloads = mainProjectAllowsDownloads(
    projects,
    selectedMainProject
  );

  const summaryNode =
    selectCanonicalObservationSummaryNode(data.observationSummary) || {};
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
    <MainLayout title={jname} description={data.pulsarFoldResult.description}>
      <HeaderButtons
        jname={jname}
        mainProject={mainProject}
        toasLink={data.pulsarFoldResult.toasLink}
        isAuthenticated={isAuthenticated}
        restricted={restricted}
        embargoEndDate={embargoEndDate}
        projectShort={projectShort}
        allowDownloads={allowDownloads}
      />
      <SummaryDataRow dataPoints={summaryData} />
      <PlotContainer
        queryData={data}
        jname={jname}
        mainProject={mainProject}
        match={match}
        minimumSNR={minimumSNR}
        setMinimumSNR={setMinimumSNR}
        excludeBadges={excludeBadges}
        setExcludeBadges={setExcludeBadges}
        allProjects={data?.pulsarFoldResult?.allProjects}
        mostCommonProject={data?.pulsarFoldResult?.mostCommonProject}
        allNchans={data?.pulsarFoldResult?.allNchans}
      />
      <FoldDetailTable
        tableData={data}
        jname={jname}
        mainProject={mainProject}
      />
    </MainLayout>
  );
};

export default FoldDetail;
