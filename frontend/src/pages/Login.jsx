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

import { HiOutlineLockClosed } from "react-icons/hi";
import { Link } from "found";
import { fetchCSRFToken, authenticatedFetch } from "../auth/csrfUtils";
import { useAuth } from "../auth/AuthContext";

// API endpoint for login
const LOGIN_URL = "/api/auth/login/";

const validationSchema = Yup.object().shape({
  email: Yup.string().required("Please include an email."),
  password: Yup.string().required("Please include a password."),
});

const Login = ({ router, match }) => {
  const [formErrors, setFormErrors] = useState([]);
  const { refreshAuth } = useAuth();

  const login = async (email, password) => {
    try {
      // First get CSRF token
      await fetchCSRFToken();

      // Then attempt login
      const response = await authenticatedFetch(LOGIN_URL, {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        setFormErrors([errorData.detail || "Login failed"]);
        return;
      }

      const data = await response.json();

      // Store user info in localStorage (only non-sensitive info)
      localStorage.username = data.user.username;
      localStorage.isStaff = data.user.isStaff;

      // Update AuthContext state
      await refreshAuth();

      // Navigate to next page
      const nextPath =
        match.location.query.next === undefined
          ? "/"
          : match.location.query.next;
      router.replace(nextPath);
    } catch (error) {
      console.error("Login error:", error);
      setFormErrors(["An error occurred during login. Please try again."]);
    }
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
                <h4 className="text-primary-600 mb-4">Sign in</h4>
                <Formik
                  initialValues={{
                    email: "",
                    password: "",
                  }}
                  validationSchema={validationSchema}
                  onSubmit={(values) => login(values.email, values.password)}
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
                            className="text-uppercase shadow-md mt-2"
                            type="submit"
                          >
                            Sign in
                          </Button>
                        </Col>
                        <Col xl={{ span: 12 }} md={{ span: 12 }}>
                          &nbsp;
                        </Col>
                        <Col xl={{ span: 12 }} md={{ span: 12 }}>
                          <span className="float-right">
                            Do not have an account with us?&nbsp;
                            <Link to={"/register/"}>Register</Link>
                          </span>
                        </Col>
                        <Col xl={{ span: 12 }} md={{ span: 12 }}>
                          <span className="float-right">
                            Forgot your account password?&nbsp;
                            <Link to={"/password_reset_request/"}>
                              Reset Password
                            </Link>
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

export default Login;
