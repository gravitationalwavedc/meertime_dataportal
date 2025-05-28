import { Table, Button, Card } from "react-bootstrap";

const TokenList = ({ tokens, loading, onDeleteClick }) => {
  const formatDate = (dateString) => {
    if (!dateString) return "Never";
    return (
      new Date(dateString).toLocaleDateString() +
      " " +
      new Date(dateString).toLocaleTimeString()
    );
  };

  const formatExpiry = (expiresAt) => {
    if (!expiresAt) return "Never expires";

    const expiryDate = new Date(expiresAt);
    const now = new Date();

    if (expiryDate < now) {
      return <span className="text-danger">Expired</span>;
    }

    return formatDate(expiresAt);
  };

  if (loading) {
    return (
      <Card.Body>
        <div className="text-center">Loading tokens...</div>
      </Card.Body>
    );
  }

  if (tokens.length === 0) {
    return (
      <Card.Body>
        <div className="text-center text-muted">
          <p>You don't have any API tokens yet.</p>
          <p>Create your first token to start using the API.</p>
        </div>
      </Card.Body>
    );
  }

  return (
    <Card.Body>
      <Table responsive className="react-bootstrap-table mt-1">
        <thead>
          <tr>
            <th>Name</th>
            <th>Token Preview</th>
            <th>Created</th>
            <th>Last Used</th>
            <th>Expires</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {tokens.map((token) => (
            <tr key={token.id}>
              <td>{token.name}</td>
              <td>
                <code>{token.preview}...</code>
              </td>
              <td>{formatDate(token.created)}</td>
              <td>{formatDate(token.lastUsed)}</td>
              <td>{formatExpiry(token.expiresAt)}</td>
              <td>
                <span
                  className={`badge ${
                    token.isActive ? "bg-success" : "bg-secondary"
                  }`}
                >
                  {token.isActive ? "Active" : "Inactive"}
                </span>
              </td>
              <td>
                <Button
                  variant="outline-danger"
                  size="sm"
                  onClick={() => onDeleteClick(token)}
                >
                  Delete
                </Button>
              </td>
            </tr>
          ))}
        </tbody>
      </Table>
    </Card.Body>
  );
};

export default TokenList;
