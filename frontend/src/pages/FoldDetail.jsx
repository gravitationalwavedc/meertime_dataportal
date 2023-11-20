import { graphql, useLazyLoadQuery } from "react-relay";
import FoldDetailTable from "../components/FoldDetailTable";
import MainLayout from "../components/MainLayout";

const query = graphql`
  query FoldDetailQuery(
    $pulsar: String!
    $mainProject: String
    $dmCorrected: Boolean
    $minimumNsubs: Boolean
    $obsNchan: Int # Ensure this variable is defined
  ) {
    ...FoldDetailTableFragment
      @arguments(
        pulsar: $pulsar
        mainProject: $mainProject
        dmCorrected: $dmCorrected
        minimumNsubs: $minimumNsubs
        obsNchan: $obsNchan
      )
    ...FoldDetailFileDownloadFragment @arguments(jname: $pulsar)
  }
`;

const FoldDetail = ({ match }) => {
  const { jname, mainProject } = match.params;
  console.log("pulsar:", jname);
  console.log("mainProject:", mainProject);
  const tableData = useLazyLoadQuery(query, {
    pulsar: jname,
    mainProject: mainProject,
    dmCorrected: false,
    minimumNsubs: true,
    obsNchan: 1,
  });

  return (
    <MainLayout title={jname}>
      <FoldDetailTable
        query={query}
        tableData={tableData}
        jname={jname}
        mainProject={mainProject}
      />
    </MainLayout>
  );
};

export default FoldDetail;
