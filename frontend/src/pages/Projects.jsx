import { Suspense } from "react";
import MainLayout from "../components/MainLayout";
import MembershipRequestList from "../components/projects/MembershipRequestList";
import { graphql, useLazyLoadQuery } from "react-relay";
import ApproveMembership from "../components/projects/ApproveMembership";
import ProjectMembershipList from "../components/projects/ProjectMembershipList";

const query = graphql`
  query ProjectsQuery {
    ...MembershipRequestListFragment
    ...ApproveMembershipFragment
    ...ProjectMembershipListFragment
  }
`;

const Projects = () => {
  const data = useLazyLoadQuery(query, {});
  return (
    <MainLayout title="Projects">
      <ProjectMembershipList data={data} />
      <ApproveMembership data={data} />
      <Suspense fallback={<div>Refreshing membership requests...</div>}>
        <MembershipRequestList data={data} />
      </Suspense>
    </MainLayout>
  );
};

export default Projects;
