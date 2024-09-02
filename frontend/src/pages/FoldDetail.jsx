import HeaderButtons from "../components/fold-detail/HeaderButtons";
import MainLayout from "../components/MainLayout";
import SummaryDataRow from "../components/SummaryDataRow";
import FoldDetailTable from "../components/fold-detail/FoldDetailTable";
import { graphql } from "relay-runtime";
import { useLazyLoadQuery } from "react-relay";
import PlotContainer from "../components/plots/PlotContainer";
import { Suspense } from "react";
import { useState } from "react";

const foldDetailQuery = graphql`
  query FoldDetailQuery(
    $pulsar: String!
    $mainProject: String
    $projectShort: String
    $nsubType: String
    $obsNchan: Int
    $excludeBadges: [String]
    $minimumSNR: Float
  ) {
    pulsarFoldResult(
      pulsar: $pulsar
      mainProject: $mainProject
      excludeBadges: $excludeBadges
      minimumSNR: $minimumSNR
    ) {
      description
      toasLink
    }
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

    ...FoldDetailTableFragment
      @arguments(
        pulsar: $pulsar
        mainProject: $mainProject
        excludeBadges: $excludeBadges
        minimumSNR: $minimumSNR
      )

    ...PlotContainerFragment
      @arguments(
        pulsar: $pulsar
        mainProject: $mainProject
        projectShort: $projectShort
        nsubType: $nsubType
        obsNchan: $obsNchan
        excludeBadges: $excludeBadges
        minimumSNR: $minimumSNR
      )
  }
`;

const FoldDetail = ({ match }) => {
  const { jname, mainProject, minSNR } = match.params;

  const [excludeBadges, setExcludeBadges] = useState([]);
  const [minimumSNR, setMinimumSNR] = useState(minSNR || 8);

  const data = useLazyLoadQuery(foldDetailQuery, {
    pulsar: jname,
    mainProject: mainProject,
  });

  const summaryNode = data.observationSummary?.edges[0]?.node;
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
      />
      <SummaryDataRow dataPoints={summaryData} />
      <Suspense fallback="<h1>Loading</h1>">
        <PlotContainer
          queryData={data}
          jname={jname}
          mainProject={mainProject}
          match={match}
          minimumSNR={minimumSNR}
          setMinimumSNR={setMinimumSNR}
          excludeBadges={excludeBadges}
          setExcludeBadges={setExcludeBadges}
        />
      </Suspense>
      <FoldDetailTable
        tableData={data}
        jname={jname}
        mainProject={mainProject}
      />
    </MainLayout>
  );
};

export default FoldDetail;
