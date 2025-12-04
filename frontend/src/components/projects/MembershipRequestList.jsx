import { useState } from "react";
import { graphql, useRefetchableFragment, commitMutation } from "react-relay";
import environment from "../../relayEnvironment";
import { formatUTC } from "../../helpers";
import { Alert, Table, Row, Col, Button } from "react-bootstrap";
import JoinProjectForm from "./JoinProjectForm";

const fragment = graphql`
  fragment MembershipRequestListFragment on Query
  @refetchable(queryName: "MembershipRequestListRefetchQuery") {
    projectMembershipRequests {
      edges {
        node {
          id
          message
          status
          requestedAt
          project {
            short
            code
          }
        }
      }
    }
    ...JoinProjectFormFragment
  }
`;

const removeRequestMutation = graphql`
  mutation MembershipRequestListMutation(
    $input: RemoveProjectMembershipRequestInput!
  ) {
    removeProjectMembershipRequest(input: $input) {
      deletedProjectMembershipRequestId
      errors
    }
  }
`;

const MembershipRequestList = ({ data }) => {
  const [errors, setErrors] = useState([]);
  const [showErrors, setShowErrors] = useState(false);
  const [fragmentData, refetch] = useRefetchableFragment(fragment, data);

  const rows = fragmentData.projectMembershipRequests.edges
    .filter((edge) => edge?.node?.status !== "APPROVED" && edge?.node?.project)
    .map((edge) => {
      const node = edge.node;
      return {
        key: `${node.project.code}-${node.requestedAt}`,
        id: node.id,
        project: `${node.project.short} (${node.project.code})`,
        requestedAt: formatUTC(node.requestedAt),
        status: node.status,
      };
    });

  const handleRemoveRequest = (requestId) => {
    commitMutation(environment, {
      mutation: removeRequestMutation,
      variables: {
        input: {
          requestId: requestId,
        },
      },
      updater: (store) => {
        // Get the deleted ID from the mutation response
        const payload = store.getRootField("removeProjectMembershipRequest");
        const deletedId = payload?.getValue(
          "deletedProjectMembershipRequestId"
        );

        if (deletedId) {
          // Delete the node from the store
          store.delete(deletedId);

          // Update the parent record to remove references
          const root = store.getRoot();
          const membershipRequests = root.getLinkedRecord(
            "projectMembershipRequests"
          );

          if (membershipRequests) {
            const edges = membershipRequests.getLinkedRecords("edges");
            if (edges) {
              // Filter out the deleted edge
              const newEdges = edges.filter((edge) => {
                const node = edge?.getLinkedRecord("node");
                return node?.getDataID() !== deletedId;
              });
              membershipRequests.setLinkedRecords(newEdges, "edges");
            }
          }
        }
      },
      onCompleted: ({ removeProjectMembershipRequest }, errors) => {
        let newErrors = [];
        if (errors) {
          newErrors.push(...errors.map((e) => e.message));
        }

        if (removeProjectMembershipRequest?.errors) {
          newErrors.push(...removeProjectMembershipRequest.errors);
        }

        if (newErrors.length > 0) {
          setErrors(newErrors);
          setShowErrors(true);
        }
      },
      onError: () => {
        setErrors(["Something went wrong, please try later."]);
      },
    });
  };

  return (
    <>
      {rows.length > 0 && (
        <Row>
          <Col lg={8} md={6}>
            <h4 className="text-primary-600 mt-5">Membership requests</h4>
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
                  <th>Requested At</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((row) => (
                  <tr key={row.key}>
                    <td>{row.project}</td>
                    <td>{row.requestedAt}</td>
                    <td>{row.status}</td>
                    <td>
                      <Button
                        variant="outline-secondary"
                        onClick={() => handleRemoveRequest(row.id)}
                      >
                        Remove
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </Table>
          </Col>
        </Row>
      )}
      <JoinProjectForm
        relayData={fragmentData}
        onRequestSubmitted={() => refetch({}, { fetchPolicy: "network-only" })}
      />
    </>
  );
};

export default MembershipRequestList;
