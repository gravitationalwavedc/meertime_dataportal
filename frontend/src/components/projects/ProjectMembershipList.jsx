import { useState } from "react";
import { useFragment, commitMutation } from "react-relay";
import { graphql } from "relay-runtime";
import environment from "../../relayEnvironment";
import { Table, Button, Col, Row, Alert } from "react-bootstrap";

const fragment = graphql`
  fragment ProjectMembershipListFragment on Query {
    projectMemberships {
      edges {
        node {
          id
          user {
            id
            firstName
            lastName
            email
          }
          project {
            id
            short
            code
          }
          role
          joinedAt
          approvedBy {
            firstName
            lastName
            email
          }
        }
      }
    }
  }
`;

const leaveProjectMutation = graphql`
  mutation ProjectMembershipListMutation($input: LeaveProjectInput!) {
    leaveProject(input: $input) {
      projectId
      userId
      errors
    }
  }
`;

const ProjectMembershipList = ({ data }) => {
  const [errors, setErrors] = useState([]);
  const [showErrors, setShowErrors] = useState(false);
  const fragmentData = useFragment(fragment, data);

  const rows = fragmentData.projectMemberships.edges
    .filter((edge) => edge?.node?.project && edge?.node?.user)
    .map((edge) => {
      const node = edge.node;
      return {
        id: node.id,
        projectId: node.project.id,
        userId: node.user.id,
        key: `${node.project.code}-${node.joinedAt}`,
        project: `${node.project.short} (${node.project.code})`,
        role: node.role,
        joinedAt: node.joinedAt,
      };
    });

  const handleLeaveProject = (membershipId, projectId, userId) => {
    commitMutation(environment, {
      mutation: leaveProjectMutation,
      variables: {
        input: {
          projectId: projectId,
          userId: userId,
        },
      },
      updater: (store) => {
        // Get the response from the mutation
        const payload = store.getRootField("leaveProject");
        const returnedProjectId = payload?.getValue("projectId");
        const returnedUserId = payload?.getValue("userId");

        if (returnedProjectId && returnedUserId) {
          // Delete the membership node from the store
          store.delete(membershipId);

          // Update the parent record to remove references
          const root = store.getRoot();
          const memberships = root.getLinkedRecord("projectMemberships");

          if (memberships) {
            const edges = memberships.getLinkedRecords("edges");
            if (edges) {
              // Filter out the deleted edge
              const newEdges = edges.filter((edge) => {
                const node = edge?.getLinkedRecord("node");
                return node?.getDataID() !== membershipId;
              });
              memberships.setLinkedRecords(newEdges, "edges");
            }
          }
        }
      },
      onCompleted: ({ leaveProject }, errors) => {
        let newErrors = [];
        if (errors) {
          newErrors.push(...errors.map((e) => e.message));
        }

        if (leaveProject?.errors) {
          newErrors.push(...leaveProject.errors);
        }

        if (newErrors.length > 0) {
          setErrors(newErrors);
          setShowErrors(true);
        }
      },
      onError: () => {
        setErrors(["Something went wrong, please try later."]);
        setShowErrors(true);
      },
    });
  };

  if (rows.length === 0) {
    return (
      <div>
        <h4 className="text-primary-600 mt-5">Current Memberships</h4>
        <p className="text-muted">You are not a member of any projects yet.</p>
      </div>
    );
  }

  return (
    <Row>
      <Col md={6} lg={8}>
        <h4 className="text-primary-600 mt-5">Current Memberships</h4>
        <Row>
          <Col xl={6} md={12}>
            {errors.map((error) => (
              <Alert
                show={showErrors}
                key={error}
                variant="danger"
                dismissible
                onClose={() => setShowErrors(false)}
              >
                {error}
              </Alert>
            ))}
          </Col>
        </Row>
        <Table responsive className="react-bootstrap-table mt-1">
          <thead>
            <tr>
              <th>Project</th>
              <th>Role</th>
              <th>Joined At</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.key}>
                <td>{row.project}</td>
                <td>{row.role}</td>
                <td>{row.joinedAt}</td>
                <td>
                  {row.role.toUpperCase() !== "OWNER" && (
                    <Button
                      variant="outline-secondary"
                      onClick={() =>
                        handleLeaveProject(row.id, row.projectId, row.userId)
                      }
                    >
                      Leave
                    </Button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </Table>
      </Col>
    </Row>
  );
};

export default ProjectMembershipList;
