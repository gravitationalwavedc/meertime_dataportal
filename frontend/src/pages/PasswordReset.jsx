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
import { HiOutlineLockClosed } from "react-icons/hi";
import { Link } from "found";
import environment from "../relayEnvironment";

const mutation = graphql`
  mutation PasswordResetMutation(
    $verification_code: String!
    $password: String!
  ) {
    passwordReset(verificationCode: $verification_code, password: $password) {
      ok
      passwordResetRequest {
        id
        status
      }
      errors
    }
  }
`;

const validationSchema = Yup.object().shape({
  password: Yup.string()
    .required("Please include a password.")
    .matches(
      /^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%^&*])/,
      "One Uppercase, One Lowercase, One Number and One Special Case Character"
    )
    .matches(/^(?=.{8,})/, "Must Contain 8 Characters"),
  confirm_password: Yup.string().oneOf(
    [Yup.ref("password"), null],
    "Passwords must match"
  ),
});

const PasswordReset = ({ router, match }) => {
  const [formErrors, setFormErrors] = useState([]);
  const [success, setSuccess] = useState(false);

  const passwordReset = (verification_code, password, confirm_password) => {
    const variables = {
      verification_code: verification_code,
      password: password,
      confirm_password: confirm_password,
    };

    commitMutation(environment, {
      mutation,
      variables,
      onCompleted: ({ passwordReset }) => {
        if (passwordReset.errors) {
          setFormErrors(passwordReset.errors);
        } else if (passwordReset.passwordResetRequest) {
          setSuccess(true);
        }
      },
      onError: (errors) => {
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
            The Pulsar Portal
          </h1>
          <h2
            className="text-gray-100 w-100 mt-5 text-center d-block d-sm-none"
            style={{ marginBottom: "-3rem" }}
          >
            The Pulsar Portal
          </h2>
          <Col
            xl={{ span: 8, offset: 2 }}
            md={{ span: 8, offset: 2 }}
            className="login-form"
          >
            <Card className="shadow-2xl text-left">
              <Card.Body className="m-4">
                <h4 className="text-primary-600 mb-4">Password Reset</h4>
                {success && (
                  <div>
                    <h5>Password Reset Successful</h5>
                    <div>
                      Your password has been reset successfully. You need to
                      login using your new password via the login page.
                    </div>
                    <Row className="buttons-row">
                      <Col sm={{ span: 12 }}>&nbsp;</Col>
                      <Col xl={{ span: 12 }} md={{ span: 12 }}>
                        <span>
                          Have an account?&nbsp;
                          <Link to={"/login/"}>Login</Link>
                        </span>
                      </Col>
                    </Row>
                  </div>
                )}
                {!success && (
                  <Formik
                    initialValues={{
                      verification_code: "",
                      password: "",
                      confirm_password: "",
                    }}
                    validationSchema={validationSchema}
                    onSubmit={(values) =>
                      passwordReset(
                        values.verification_code,
                        values.password,
                        values.confirm_password
                      )
                    }
                  >
                    {({ handleSubmit }) => (
                      <Form onSubmit={handleSubmit}>
                        <Field name="verification_code">
                          {({ field, meta }) => (
                            <Form.Group controlId="verification_code">
                              <Form.Label>
                                Verification Code (Sent to your email)
                              </Form.Label>
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
                        <Field name="password">
                          {({ field, meta }) => (
                            <Form.Group controlId="password">
                              <Form.Label>New Password</Form.Label>
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
                        <Field name="confirm_password">
                          {({ field, meta }) => (
                            <Form.Group controlId="confirm_password">
                              <Form.Label>Confirm New Password</Form.Label>
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
                              Password Reset
                            </Button>
                          </Col>
                        </Row>
                      </Form>
                    )}
                  </Formik>
                )}
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Col>
    </Container>
  );
};

export default PasswordReset;
