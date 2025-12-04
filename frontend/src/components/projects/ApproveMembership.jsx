import { useState } from "react";
import { Alert, Button, Col, Row, Table } from "react-bootstrap";
import { commitMutation, graphql, useRefetchableFragment } from "react-relay";
import { formatUTC } from "../../helpers";
import environment from "../../relayEnvironment";

const fragment = graphql`
  fragment ApproveMembershipFragment on Query
  @refetchable(queryName: "ApproveMembershipRefetchQuery") {
    projectMembershipRequestsForApproval {
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
          user {
            id
            email
            firstName
            lastName
          }
        }
      }
    }
  }
`;

const approveRequestMutation = graphql`
  mutation ApproveMembershipMutation(
    $input: ApproveProjectMembershipRequestInput!
  ) {
    approveProjectMembershipRequest(input: $input) {
      approvedProjectMembershipRequestId
      errors
    }
  }
`;

const ApproveMembership = ({ data }) => {
  const [errors, setErrors] = useState([]);
  const [showErrors, setShowErrors] = useState(false);
  const [fragmentData, refetch] = useRefetchableFragment(fragment, data);

  console.log(fragmentData);

  if (fragmentData.projectMembershipRequestsForApproval?.edges.length <= 0) {
    return <></>;
  }

  // Group requests by project
  const requestsByProject = {};
  fragmentData.projectMembershipRequestsForApproval.edges.forEach(
    ({ node }) => {
      if (!node?.project) {
        return;
      }
      const projectCode = node.project.code;
      if (!requestsByProject[projectCode]) {
        requestsByProject[projectCode] = {
          projectShort: node.project.short,
          requests: [],
        };
      }
      requestsByProject[projectCode].requests.push(node);
    }
  );

  const handleApprove = (requestId, userName) => {
    console.log(
      `Approve button clicked for request ID: ${requestId}, User: ${userName}`
    );

    commitMutation(environment, {
      mutation: approveRequestMutation,
      variables: {
        input: {
          requestId: requestId,
        },
      },
      updater: (store) => {
        // Get the approved ID from the mutation response
        const payload = store.getRootField("approveProjectMembershipRequest");
        const approvedId = payload?.getValue(
          "approvedProjectMembershipRequestId"
        );

        if (approvedId) {
          // Delete the node from the store
          store.delete(approvedId);

          // Update the parent record to remove references
          const root = store.getRoot();
          const membershipRequests = root.getLinkedRecord(
            "projectMembershipRequestsForApproval"
          );

          if (membershipRequests) {
            const edges = membershipRequests.getLinkedRecords("edges");
            if (edges) {
              // Filter out the approved edge
              const newEdges = edges.filter((edge) => {
                const node = edge?.getLinkedRecord("node");
                return node?.getDataID() !== approvedId;
              });
              membershipRequests.setLinkedRecords(newEdges, "edges");
            }
          }
        }
      },
      onCompleted: ({ approveProjectMembershipRequest }, errors) => {
        let newErrors = [];
        if (errors) {
          newErrors.push(...errors.map((e) => e.message));
        }

        if (approveProjectMembershipRequest?.errors) {
          newErrors.push(...approveProjectMembershipRequest.errors);
        }

        if (newErrors.length > 0) {
          setErrors(newErrors);
          setShowErrors(true);
        } else {
          console.log(
            `Successfully approved membership request for ${userName}`
          );
        }
      },
      onError: (error) => {
        console.error("Mutation error:", error);
        setErrors(["Something went wrong, please try later."]);
        setShowErrors(true);
      },
    });
  };

  const handleReject = (requestId, userName) => {
    console.log(
      `Reject button clicked for request ID: ${requestId}, User: ${userName}`
    );
  };

  return (
    <Row>
      <Col lg={8} md={6}>
        <h4 className="text-primary-600 mt-5">Approve Membership Requests</h4>
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
        {Object.entries(requestsByProject).map(
          ([projectCode, { projectShort, requests }]) => (
            <div key={projectCode}>
              <h5 className="mt-4">{projectShort}</h5>
              <Table responsive className="react-bootstrap-table mt-1">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Message</th>
                    <th>Requested Date</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {requests.map((request) => (
                    <tr key={request.id}>
                      <td>
                        {request.user.firstName} {request.user.lastName}
                      </td>
                      <td>{request.user.email}</td>
                      <td>{request.message}</td>
                      <td>{formatUTC(request.requestedAt)}</td>
                      <td>
                        <Button
                          variant="primary"
                          size="sm"
                          className="mr-2"
                          onClick={() =>
                            handleApprove(
                              request.id,
                              `${request.user.firstName} ${request.user.lastName}`
                            )
                          }
                        >
                          Approve
                        </Button>
                        <Button
                          variant="outline-danger"
                          size="sm"
                          onClick={() =>
                            handleReject(
                              request.id,
                              `${request.user.firstName} ${request.user.lastName}`
                            )
                          }
                        >
                          Reject
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </Table>
            </div>
          )
        )}
      </Col>
    </Row>
  );
};

export default ApproveMembership;
