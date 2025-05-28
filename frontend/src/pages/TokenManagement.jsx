import { useState, Suspense } from "react";
import environment from "../relayEnvironment";
import { Button, Col, Row, Card } from "react-bootstrap";
import { graphql, commitMutation, useLazyLoadQuery } from "react-relay";
import MainLayout from "../components/MainLayout";
import TokenList from "../components/TokenList";
import CreateTokenForm from "../components/CreateTokenForm";
import DeleteTokenModal from "../components/DeleteTokenModal";
import TokenSuccessAlert from "../components/TokenSuccessAlert";
import ErrorAlert from "../components/ErrorAlert";
import UsageInstructions from "../components/UsageInstructions";

const createTokenMutation = graphql`
  mutation TokenManagementCreateMutation($name: String!) {
    createApiToken(input: { name: $name }) {
      token {
        id
        name
        preview
        created
        lastUsed
        expiresAt
        isActive
      }
      tokenValue
      ok
      errors
    }
  }
`;

const tokenListQuery = graphql`
  query TokenManagementQuery {
    apiTokens {
      edges {
        node {
          id
          name
          preview
          created
          lastUsed
          expiresAt
          isActive
        }
      }
    }
  }
`;

const deleteTokenMutation = graphql`
  mutation TokenManagementDeleteMutation($tokenId: ID!) {
    deleteApiToken(input: { tokenId: $tokenId }) {
      ok
      errors
    }
  }
`;

// Component that displays the tokens using the query
const TokensDisplay = ({ onDeleteClick, refreshKey }) => {
  const data = useLazyLoadQuery(
    tokenListQuery,
    {},
    { fetchPolicy: "store-and-network", fetchKey: refreshKey }
  );

  const tokens = data.apiTokens?.edges?.map((edge) => edge.node) || [];

  return (
    <TokenList tokens={tokens} loading={false} onDeleteClick={onDeleteClick} />
  );
};

const TokenManagement = () => {
  const [formErrors, setFormErrors] = useState([]);
  const [success, setSuccess] = useState(false);
  const [token, setToken] = useState();
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [tokenToDelete, setTokenToDelete] = useState(null);
  const [refreshKey, setRefreshKey] = useState(0);

  const refreshTokens = () => {
    setRefreshKey((prev) => prev + 1);
  };

  const createApiToken = (name) => {
    const variables = {
      name: name || "Web Token",
    };

    commitMutation(environment, {
      mutation: createTokenMutation,
      variables,
      onCompleted: ({ createApiToken }) => {
        if (createApiToken.errors) {
          setFormErrors(createApiToken.errors);
        } else if (createApiToken.ok && createApiToken.token) {
          setSuccess(true);
          // Use the full token value returned on creation
          setToken(createApiToken.tokenValue);
          setShowCreateForm(false);
          refreshTokens(); // Refresh the token list
        }
      },
      onError: () => {
        setFormErrors(["Something went wrong, please try later."]);
      },
    });
  };

  const deleteToken = (tokenId) => {
    commitMutation(environment, {
      mutation: deleteTokenMutation,
      variables: { tokenId },
      onCompleted: ({ deleteApiToken }) => {
        if (deleteApiToken.errors) {
          setFormErrors(deleteApiToken.errors);
        } else if (deleteApiToken.ok) {
          refreshTokens(); // Refresh the token list
          setShowDeleteModal(false);
          setTokenToDelete(null);
        }
      },
      onError: () => {
        setFormErrors(["Failed to delete token"]);
      },
    });
  };

  const handleDeleteClick = (token) => {
    setTokenToDelete(token);
    setShowDeleteModal(true);
  };

  const handleDeleteConfirm = (tokenId) => {
    deleteToken(tokenId);
  };

  const handleDeleteCancel = () => {
    setShowDeleteModal(false);
    setTokenToDelete(null);
  };

  return (
    <MainLayout title="API Token Management">
      <Row>
        <Col xl={{ span: 10, offset: 1 }} md={{ span: 10, offset: 1 }}>
          <TokenSuccessAlert
            show={success}
            token={token}
            onClose={() => setSuccess(false)}
          />

          <ErrorAlert
            show={formErrors.length > 0}
            errors={formErrors}
            onClose={() => setFormErrors([])}
          />

          <Card className="mb-4">
            <Card.Header className="d-flex justify-content-between align-items-center">
              <h5 className="mb-0">Your API Tokens</h5>
              <Button
                variant="primary"
                onClick={() => setShowCreateForm(!showCreateForm)}
              >
                {showCreateForm ? "Cancel" : "Create New Token"}
              </Button>
            </Card.Header>

            {showCreateForm && (
              <CreateTokenForm
                onSubmit={createApiToken}
                onCancel={() => setShowCreateForm(false)}
              />
            )}

            <Suspense fallback={<div>Loading tokens...</div>}>
              <TokensDisplay
                onDeleteClick={handleDeleteClick}
                refreshKey={refreshKey}
              />
            </Suspense>
          </Card>

          <UsageInstructions />
        </Col>
      </Row>

      <DeleteTokenModal
        show={showDeleteModal}
        onHide={handleDeleteCancel}
        token={tokenToDelete}
        onConfirm={handleDeleteConfirm}
      />
    </MainLayout>
  );
};

export default TokenManagement;
