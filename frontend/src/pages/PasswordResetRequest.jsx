import * as Yup from "yup";
import {
  Alert,
  Button,
  Card,
  Col,
  Container,
  Form,
  Row,
} from "react-bootstrap";
import { Field, Formik } from "formik";
import { useState } from "react";
import { commitMutation, graphql } from "react-relay";
import { Link } from "found";
import environment from "../relayEnvironment";

const mutation = graphql`
  mutation PasswordResetRequestMutation($email: String!) {
    createPasswordResetRequest(email: $email) {
      ok
      passwordResetRequest {
        id
        verificationExpiry
      }
      errors
    }
  }
`;

const validationSchema = Yup.object().shape({
  email: Yup.string()
    .email("Invalid email format.")
    .required("Please include an email."),
});

const PasswordResetRequest = ({ router, match }) => {
  const [formErrors, setFormErrors] = useState([]);

  const passwordResetRequest = (email) => {
    const variables = {
      email: email,
    };

    commitMutation(environment, {
      mutation,
      variables,
      onCompleted: ({ createPasswordResetRequest }) => {
        if (createPasswordResetRequest.errors) {
          setFormErrors(createPasswordResetRequest.errors);
        } else if (createPasswordResetRequest.passwordResetRequest) {
          router.replace("/password_reset/");
        }
      },
      onError: () => {
        setFormErrors(["Something went wrong, please try later."]);
      },
    });
  };

  return (
    <Container fluid className="login-page h-100">
      <Col
        xl={{ span: 6, offset: 5 }}
        md={{ span: 10, offset: 1 }}
        className="login-col h-100"
      >
        <Row>
          <h1
            className="text-gray-100 w-100 mt-5 text-center d-none d-sm-block"
            style={{ marginBottom: "-3rem" }}
          >
            MEERTIME
          </h1>
          <h2
            className="text-gray-100 w-100 mt-5 text-center d-block d-sm-none"
            style={{ marginBottom: "-3rem" }}
          >
            MEERTIME
          </h2>
          <Col
            xl={{ span: 8, offset: 2 }}
            md={{ span: 8, offset: 2 }}
            className="login-form"
          >
            <Card className="shadow-2xl text-left">
              <Card.Body className="m-4">
                <h4 className="text-primary-600 mb-4">
                  Password Reset Request
                </h4>
                <Formik
                  initialValues={{
                    email: "",
                  }}
                  validationSchema={validationSchema}
                  onSubmit={(values) => passwordResetRequest(values.email)}
                >
                  {({ handleSubmit }) => (
                    <Form onSubmit={handleSubmit}>
                      <Field name="email">
                        {({ field, meta }) => (
                          <Form.Group controlId="email">
                            <Form.Label>Email</Form.Label>
                            <Form.Control
                              {...field}
                              isInvalid={meta.touched && meta.error}
                            />
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
                            data-testid="password-reset-button"
                            className="text-uppercase shadow-md mt-2"
                            type="submit"
                          >
                            Password Reset Request
                          </Button>
                        </Col>
                        <Col sm={{ span: 12 }}>&nbsp;</Col>
                        <Col xl={{ span: 12 }} md={{ span: 12 }}>
                          <span className="float-right">
                            Have an account?&nbsp;
                            <Link to={"/login/"}>Login</Link>
                          </span>
                        </Col>
                      </Row>
                    </Form>
                  )}
                </Formik>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Col>
    </Container>
  );
};

export default PasswordResetRequest;
