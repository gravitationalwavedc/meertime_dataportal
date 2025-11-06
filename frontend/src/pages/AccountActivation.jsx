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
  mutation AccountActivationMutation(
    $activation_code: String!
    $first_name: String!
    $last_name: String!
    $email: String!
    $password: String!
    $captcha: String!
  ) {
    accountActivation(
      activationCode: $activation_code
      userInput: {
        firstName: $first_name
        lastName: $last_name
        email: $email
        password: $password
        captcha: $captcha
      }
    ) {
      ok
      provisionalUser {
        id
        activated
        activatedOn
      }
      errors
    }
  }
`;

const validationSchema = Yup.object().shape({
  first_name: Yup.string().required("Please include a first name."),
  last_name: Yup.string().required("Please include a last name."),
  email: Yup.string()
    .email("Invalid email format.")
    .required("Please include an email."),
  password: Yup.string()
    .required("Please include a password.")
    .matches(
      /^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%^&*])/,
      "Must have uppercase, lowercase, number and special character"
    )
    .matches(/^(?=.{8,})/, "Must Contain 8 Characters"),
  confirm_password: Yup.string().oneOf(
    [Yup.ref("password"), null],
    "Passwords must match"
  ),
});

const AccountActivation = ({
  match: {
    params: { code },
  },
}) => {
  const [formErrors, setFormErrors] = useState([]);
  const [success, setSuccess] = useState(false);

  const accountActivation = (
    first_name,
    last_name,
    email,
    password,
    confirm_password,
    captcha
  ) => {
    const variables = {
      activation_code: code,
      first_name: first_name,
      last_name: last_name,
      email: email,
      password: password,
      confirm_password: confirm_password,
      captcha: captcha,
    };

    commitMutation(environment, {
      mutation,
      variables,
      onCompleted: ({ accountActivation }) => {
        if (accountActivation.errors) {
          setFormErrors(accountActivation.errors);
        } else if (accountActivation.provisionalUser) {
          setSuccess(true);
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
                <h4 className="text-primary-600 mb-4">Account Activation</h4>
                {success && (
                  <div>
                    <h5>Account Activation Successful</h5>
                    <div>
                      Your account has been activated successfully. You need to
                      login using your email/password via the login page.
                    </div>
                    <Row className="buttons-row">
                      <Col sm={{ span: 12 }}>&nbsp;</Col>
                      <Col xl={{ span: 12 }} md={{ span: 12 }}>
                        <span>
                          Have an account?
                          <Link to={"/login/"}> Login</Link>
                        </span>
                      </Col>
                    </Row>
                  </div>
                )}
                {!success && (
                  <Formik
                    initialValues={{
                      activation_code: code,
                      first_name: "",
                      last_name: "",
                      email: "",
                      password: "",
                      confirm_password: "",
                    }}
                    validationSchema={validationSchema}
                    onSubmit={(values) =>
                      accountActivation(
                        values.first_name,
                        values.last_name,
                        values.email,
                        values.password,
                        values.confirm_password
                      )
                    }
                  >
                    {({ handleSubmit }) => (
                      <Form onSubmit={handleSubmit}>
                        <Form.Row className="visible:None">
                          <Field name="activation_code">
                            {({ field, meta }) => (
                              <Form.Group
                                controlId="activation_code"
                                as={Col}
                                sm={12}
                                md={12}
                                xl={12}
                              >
                                <Form.Label>
                                  Code (will be matched against your email)
                                </Form.Label>
                                <Form.Control
                                  {...field}
                                  isInvalid={meta.touched && meta.error}
                                  disabled
                                />
                                <Form.Control.Feedback type="invalid">
                                  {meta.error}
                                </Form.Control.Feedback>
                              </Form.Group>
                            )}
                          </Field>
                        </Form.Row>
                        <Form.Row>
                          <Field name="first_name">
                            {({ field, meta }) => (
                              <Form.Group
                                controlId="first_name"
                                as={Col}
                                sm={6}
                                md={6}
                                xl={6}
                              >
                                <Form.Label>First Name</Form.Label>
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
                          <Field name="last_name">
                            {({ field, meta }) => (
                              <Form.Group
                                controlId="last_name"
                                as={Col}
                                sm={6}
                                md={6}
                                xl={6}
                              >
                                <Form.Label>Last Name</Form.Label>
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
                        </Form.Row>
                        <Form.Row>
                          <Field name="email">
                            {({ field, meta }) => (
                              <Form.Group
                                controlId="email"
                                as={Col}
                                sm={12}
                                md={12}
                                xl={12}
                              >
                                <Form.Label>
                                  Email (to which address the link was sent)
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
                        </Form.Row>
                        <Form.Row>
                          <Field name="password">
                            {({ field, meta }) => (
                              <Form.Group
                                controlId="password"
                                as={Col}
                                sm={6}
                                md={6}
                                xl={6}
                              >
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
                          <Field name="confirm_password">
                            {({ field, meta }) => (
                              <Form.Group
                                controlId="confirm_password"
                                as={Col}
                                sm={6}
                                md={6}
                                xl={6}
                              >
                                <Form.Label>Confirm Password</Form.Label>
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
                        </Form.Row>
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
                              Activate With Password
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

export default AccountActivation;
