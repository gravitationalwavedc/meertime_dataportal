import { useState } from "react";
import { Alert, Button, Col, Form, Modal, Row, Table } from "react-bootstrap";
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

const rejectRequestMutation = graphql`
  mutation ApproveMembershipRejectMutation(
    $input: RejectProjectMembershipRequestInput!
  ) {
    rejectProjectMembershipRequest(input: $input) {
      rejectedProjectMembershipRequestId
      errors
    }
  }
`;

const ApproveMembership = ({ data }) => {
  const [errors, setErrors] = useState([]);
  const [showErrors, setShowErrors] = useState(false);
  const [fragmentData, refetch] = useRefetchableFragment(fragment, data);

  // Modal state for rejection confirmation
  const [showRejectModal, setShowRejectModal] = useState(false);
  const [rejectNote, setRejectNote] = useState("");
  const [pendingReject, setPendingReject] = useState(null); // { requestId, userName }

  if (
    !fragmentData.projectMembershipRequestsForApproval ||
    fragmentData.projectMembershipRequestsForApproval.edges.length <= 0
  ) {
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
    setPendingReject({ requestId, userName });
    setRejectNote("");
    setShowRejectModal(true);
  };

  const handleCloseRejectModal = () => {
    setShowRejectModal(false);
    setPendingReject(null);
    setRejectNote("");
  };

  const handleConfirmReject = () => {
    if (!pendingReject) return;

    const { requestId, userName } = pendingReject;

    commitMutation(environment, {
      mutation: rejectRequestMutation,
      variables: {
        input: {
          projectMembershipRequestId: requestId,
          note: rejectNote || null,
        },
      },
      updater: (store) => {
        // Get the rejected ID from the mutation response
        const payload = store.getRootField("rejectProjectMembershipRequest");
        const rejectedId = payload?.getValue(
          "rejectedProjectMembershipRequestId"
        );

        if (rejectedId) {
          // Delete the node from the store
          store.delete(rejectedId);

          // Update the parent record to remove references
          const root = store.getRoot();
          const membershipRequests = root.getLinkedRecord(
            "projectMembershipRequestsForApproval"
          );

          if (membershipRequests) {
            const edges = membershipRequests.getLinkedRecords("edges");
            if (edges) {
              // Filter out the rejected edge
              const newEdges = edges.filter((edge) => {
                const node = edge?.getLinkedRecord("node");
                return node?.getDataID() !== rejectedId;
              });
              membershipRequests.setLinkedRecords(newEdges, "edges");
            }
          }
        }
      },
      onCompleted: ({ rejectProjectMembershipRequest }, errors) => {
        let newErrors = [];
        if (errors) {
          newErrors.push(...errors.map((e) => e.message));
        }

        if (rejectProjectMembershipRequest?.errors) {
          newErrors.push(...rejectProjectMembershipRequest.errors);
        }

        if (newErrors.length > 0) {
          setErrors(newErrors);
          setShowErrors(true);
        } else {
          console.log(
            `Successfully rejected membership request for ${userName}`
          );
        }

        handleCloseRejectModal();
      },
      onError: (error) => {
        console.error("Mutation error:", error);
        setErrors(["Something went wrong, please try later."]);
        setShowErrors(true);
        handleCloseRejectModal();
      },
    });
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

      {/* Reject Confirmation Modal */}
      <Modal
        size="lg"
        show={showRejectModal}
        onHide={handleCloseRejectModal}
        centered
      >
        <Modal.Header closeButton>
          <Modal.Title className="text-primary">
            Reject Membership Request
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <p>
            Are you sure you want to reject the membership request from{" "}
            <strong>{pendingReject?.userName}</strong>?
          </p>
          <p className="text-muted small">
            The user will be notified by email. You may include an optional
            message below.
          </p>
          <Form.Group>
            <Form.Label>Message (optional)</Form.Label>
            <Form.Control
              as="textarea"
              rows={3}
              placeholder="Enter a reason or message for the applicant..."
              value={rejectNote}
              onChange={(e) => setRejectNote(e.target.value)}
            />
          </Form.Group>
        </Modal.Body>
        <Modal.Footer className="justify-content-between">
          <Button variant="outline-primary" onClick={handleCloseRejectModal}>
            Cancel
          </Button>
          <Button variant="danger" onClick={handleConfirmReject}>
            Reject Request
          </Button>
        </Modal.Footer>
      </Modal>
    </Row>
  );
};

export default ApproveMembership;
