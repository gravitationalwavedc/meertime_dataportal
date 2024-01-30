import { useRef, useState } from "react";
import environment from "../relayEnvironment";
import { Alert, Button, Col, Form, Row } from "react-bootstrap";
import { Field, Formik } from "formik";
import { HiOutlineLockClosed } from "react-icons/hi";
import { graphql, commitMutation } from "react-relay";
import MainLayout from "../components/MainLayout";
import CopyToClipboard from "../components/CopyToClipboard";

const mutation = graphql`
  mutation GenerateTokenMutation($username: String!, $password: String!) {
    tokenAuth(input: { username: $username, password: $password }) {
      token
    }
  }
`;

const GenerateToken = () => {
  const [formErrors, setFormErrors] = useState([]);
  const [success, setSuccess] = useState(false);
  const [token, setToken] = useState();

  const tokenAuth = (username, password) => {
    const variables = {
      username: username,
      password: password,
    };

    commitMutation(environment, {
      mutation,
      variables,
      onCompleted: ({ tokenAuth }) => {
        console.log(tokenAuth);
        if (tokenAuth.errors) {
          setFormErrors(tokenAuth.errors);
        } else if (tokenAuth.token) {
          setSuccess(true);
          setToken(tokenAuth.token);
        }
      },
      onError: () => {
        setFormErrors(["Something went wrong, please try later."]);
      },
    });
  };

  const textAreaRef = useRef(null);

  const handleCopyToClipboard = () => {
    // Select the text in the textarea
    textAreaRef.current.select();
    // Execute the copy command
    document.execCommand("copy");
    // Deselect the text
    window.getSelection().removeAllRanges();
  };

  return (
    <MainLayout title="Generate Token">
      <Row>
        <Col
          xl={{ span: 4, offset: 1 }}
          md={{ span: 6, offset: 1 }}
          sm={{ span: 10, offset: 1 }}
        >
          {success && (
            <div>
              <h5>Token Generation Successful</h5>
              <CopyToClipboard textToCopy={token} />
            </div>
          )}
          {
            <Formik
              initialValues={{
                password: "",
              }}
              onSubmit={(values) =>
                tokenAuth(localStorage.username, values.password)
              }
            >
              {({ handleSubmit }) => (
                <Form onSubmit={handleSubmit}>
                  <Field name="password">
                    {({ field, meta }) => (
                      <Form.Group controlId="password">
                        <Form.Label>Password</Form.Label>
                        <Form.Control
                          type="password"
                          {...field}
                          isInvalid={meta.touched && meta.error}
                        />
                        {!meta.error && (
                          <HiOutlineLockClosed className="form-control-icon-right" />
                        )}
                        <Form.Control.Feedback type="invalid">
                          {meta.error}
                        </Form.Control.Feedback>
                      </Form.Group>
                    )}
                  </Field>
                  {formErrors &&
                    formErrors.map((e) => (
                      <Alert variant="danger" key={e}>
                        {e}
                      </Alert>
                    ))}
                  <Row className="buttons-row">
                    <Col xl={{ span: 12 }} md={{ span: 12 }}>
                      <Button
                        className="text-uppercase shadow-md mt-2 float-right"
                        type="submit"
                      >
                        Generate Token
                      </Button>
                    </Col>
                  </Row>
                </Form>
              )}
            </Formik>
          }
        </Col>
      </Row>
    </MainLayout>
  );
};

export default GenerateToken;
