import React, { useState } from 'react';
import { commitMutation, graphql } from 'react-relay';
import { Alert, Container, Form, Button, Card } from 'react-bootstrap';
import environment from '../relayEnvironment';

const mutation = graphql`
  mutation LoginMutation($username: String!, $password: String!) {
    tokenAuth (input: {username: $username, password: $password})
    {
      token
    }
  }`;


const Login = ({router}) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [formErrors, setFormErrors] = useState([]);
  
  const login = () => {
    const variables = {
      username: username,
      password: password
    };
    
    commitMutation(
      environment,
      {
        mutation,
        variables,
        onCompleted: ({tokenAuth}, errors) => {
          if(errors){
            setFormErrors(errors.map(e => e.message));
          } else if(tokenAuth){
            sessionStorage.jwt = tokenAuth.token;
            router.replace('/');
          };
        }
      }
    );
  };

  return (
    <Container>
      <h1>MEERTIME</h1>
      <Card>
        <Card.Body>
          <h2>Sign in</h2>
          <Form>
            <Form.Row>
              <Form.Group controlId="userName">
                <Form.Label>Username</Form.Label>
                <Form.Control onChange={(e) => setUsername(e.target.value)} />
              </Form.Group>
            </Form.Row>
            <Form.Row>
              <Form.Group controlId="password">
                <Form.Label>Password</Form.Label>
                <Form.Control type="password" onChange={(e) => setPassword(e.target.value)} />
              </Form.Group>
            </Form.Row>
            { formErrors && formErrors.map((e) => <Alert key={e}>{e}</Alert>)}
            <Button onClick={() => login()}>Sign in</Button>
          </Form>
        </Card.Body>
      </Card>
    </Container>
  );
}

export default Login;
