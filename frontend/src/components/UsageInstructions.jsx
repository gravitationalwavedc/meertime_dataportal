import { Alert, Card } from "react-bootstrap";

const UsageInstructions = () => {
  return (
    <Card>
      <Card.Header>
        <h6 className="mb-0">Usage Instructions</h6>
      </Card.Header>
      <Card.Body>
        <p>
          To interact with the Pulsar Portal's API via a command line tool in
          your terminal, you can use{" "}
          <a href="https://psrdb.readthedocs.io/en/latest/index.html">PSRDB</a>{" "}
          with a token. Otherwise, you can manually make requests to the API
          with your token:
        </p>
        <pre className="bg-light p-3 rounded">
          {`# Using curl
curl -H "Authorization: Bearer YOUR_TOKEN_HERE" \\
     https://your-domain.com/api/graphql/

# Using Python requests
import requests

headers = {
    'Authorization': 'Bearer YOUR_TOKEN_HERE',
    'Content-Type': 'application/json',
}

response = requests.post(
    'https://your-domain.com/api/graphql/',
    headers=headers,
    json={'query': 'your GraphQL query'}
)`}
        </pre>
        <Alert variant="warning" className="mt-3">
          <strong>Security Note:</strong> Keep your tokens secure and never
          share them. If a token is compromised, delete it immediately and
          create a new one.
        </Alert>
      </Card.Body>
    </Card>
  );
};

export default UsageInstructions;
