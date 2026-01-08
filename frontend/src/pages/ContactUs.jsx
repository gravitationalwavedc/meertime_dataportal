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

import MainLayout from "../components/MainLayout";
import environment from "../relayEnvironment";
import { useAuth } from "../auth/AuthContext";

const mutation = graphql`
  mutation ContactUsMutation(
    $contactType: String!
    $message: String!
    $link: String
    $email: String
    $name: String
    $captcha: String!
  ) {
    submitContactForm(
      input: {
        contactType: $contactType
        message: $message
        link: $link
        email: $email
        name: $name
        captcha: $captcha
      }
    ) {
      ok
      errors
    }
  }
`;

const ContactUs = () => {
  const [formErrors, setFormErrors] = useState([]);
  const [success, setSuccess] = useState(false);
  const { user, isAuthenticated } = useAuth();

  const validationSchema = Yup.object().shape({
    contactType: Yup.string().required("Please select a contact type."),
    message: Yup.string()
      .required("Please include a message.")
      .max(2000, "Message must be at most 2000 characters long."),
    link: Yup.string().when("contactType", {
      is: "Report Issue",
      then: (schema) =>
        schema.required("Link is required when reporting an issue."),
      otherwise: (schema) => schema,
    }),
    email: Yup.string().when([], {
      is: () => !isAuthenticated,
      then: (schema) =>
        schema
          .email("Invalid email format.")
          .required("Please include an email."),
      otherwise: (schema) => schema,
    }),
    name: Yup.string().when([], {
      is: () => !isAuthenticated,
      then: (schema) => schema.required("Please include your name."),
      otherwise: (schema) => schema,
    }),
  });

  const submitContactForm = (values) => {
    const googleRecaptcha = grecaptcha; // eslint-disable-line no-undef
    googleRecaptcha.ready(function () {
      googleRecaptcha
        .execute(import.meta.env.VITE_CAPTCHA_SITE_KEY, { action: "submit" })
        .then(function (captcha) {
          submitForm(values, captcha);
        });
    });
  };

  const submitForm = (values, captcha) => {
    const variables = {
      contactType: values.contactType,
      message: values.message,
      link: values.link || null,
      captcha: captcha,
    };

    // Only include email and name for unauthenticated users
    if (!isAuthenticated) {
      variables.email = values.email;
      variables.name = values.name;
    }

    commitMutation(environment, {
      mutation,
      variables,
      onCompleted: ({ submitContactForm }) => {
        if (submitContactForm.errors && submitContactForm.errors.length > 0) {
          setFormErrors(submitContactForm.errors);
        } else if (submitContactForm.ok) {
          setSuccess(true);
          setFormErrors([]);
        }
      },
      onError: () => {
        setFormErrors(["Something went wrong, please try later."]);
      },
    });
  };

  return (
    <MainLayout>
      <Container className="mt-5">
        <Row>
          <Col xl={{ span: 8, offset: 2 }} md={{ span: 10, offset: 1 }}>
            <Card className="shadow">
              <Card.Body className="m-4">
                <h3 className="text-primary-600 mb-4">
                  Contact Us / Report Issue
                </h3>

                {success ? (
                  <Alert variant="success">
                    <h5>Thank you for contacting us!</h5>
                    <p>
                      Your message has been sent successfully. We will get back
                      to you as soon as possible.
                    </p>
                    <Button
                      variant="primary"
                      onClick={() => {
                        setSuccess(false);
                      }}
                    >
                      Send Another Message
                    </Button>
                  </Alert>
                ) : (
                  <Formik
                    initialValues={{
                      contactType: "Contact Us",
                      message: "",
                      link: "",
                      email: "",
                      name: "",
                    }}
                    validationSchema={validationSchema}
                    onSubmit={(values) => submitContactForm(values)}
                  >
                    {({ values, handleSubmit, handleChange }) => (
                      <Form onSubmit={handleSubmit}>
                        <Form.Row>
                          <Field name="contactType">
                            {({ field, meta }) => (
                              <Form.Group
                                controlId="contactType"
                                as={Col}
                                sm={12}
                                md={12}
                                xl={12}
                              >
                                <Form.Label>Type</Form.Label>
                                <Form.Control
                                  as="select"
                                  {...field}
                                  isInvalid={meta.touched && meta.error}
                                  onChange={(e) => {
                                    handleChange(e);
                                  }}
                                >
                                  <option value="Contact Us">Contact Us</option>
                                  <option value="Report Issue">
                                    Report Issue
                                  </option>
                                </Form.Control>
                                <Form.Control.Feedback type="invalid">
                                  {meta.error}
                                </Form.Control.Feedback>
                              </Form.Group>
                            )}
                          </Field>
                        </Form.Row>

                        {values.contactType === "Report Issue" && (
                          <>
                            <Form.Row>
                              <Col sm={12} md={12} xl={12}>
                                <Alert variant="info" className="small">
                                  <strong>
                                    Please describe the issue below:
                                  </strong>
                                  <ul className="mb-0 mt-2">
                                    <li>
                                      <strong>Data issues</strong> (e.g.,
                                      incorrect parameters, missing data,
                                      calibration problems, bad sessions)
                                    </li>
                                    <li>
                                      <strong>Website issues</strong> (e.g.,
                                      broken links, display errors,
                                      functionality problems)
                                    </li>
                                  </ul>
                                  <div className="mt-2">
                                    For technical/developer issues, you can also{" "}
                                    <a
                                      href="https://gitlab.com/CAS-eResearch/GWDC/meertime_dataportal/-/issues/new"
                                      target="_blank"
                                      rel="noopener noreferrer"
                                    >
                                      create a GitLab issue
                                    </a>
                                    .
                                  </div>
                                </Alert>
                              </Col>
                            </Form.Row>

                            <Form.Row>
                              <Field name="link">
                                {({ field, meta }) => (
                                  <Form.Group
                                    controlId="link"
                                    as={Col}
                                    sm={12}
                                    md={12}
                                    xl={12}
                                  >
                                    <Form.Label>Link to Issue *</Form.Label>
                                    <Form.Control
                                      {...field}
                                      type="url"
                                      placeholder="https://pulsars.org.au/..."
                                      isInvalid={meta.touched && meta.error}
                                    />
                                    <Form.Control.Feedback type="invalid">
                                      {meta.error}
                                    </Form.Control.Feedback>
                                    <Form.Text className="text-muted">
                                      Please provide a link to the page where
                                      the issue appears.
                                    </Form.Text>
                                  </Form.Group>
                                )}
                              </Field>
                            </Form.Row>
                          </>
                        )}

                        {!isAuthenticated && (
                          <>
                            <Form.Row>
                              <Field name="name">
                                {({ field, meta }) => (
                                  <Form.Group
                                    controlId="name"
                                    as={Col}
                                    sm={12}
                                    md={6}
                                    xl={6}
                                  >
                                    <Form.Label>Name *</Form.Label>
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

                              <Field name="email">
                                {({ field, meta }) => (
                                  <Form.Group
                                    controlId="email"
                                    as={Col}
                                    sm={12}
                                    md={6}
                                    xl={6}
                                  >
                                    <Form.Label>Email *</Form.Label>
                                    <Form.Control
                                      {...field}
                                      type="email"
                                      isInvalid={meta.touched && meta.error}
                                    />
                                    <Form.Control.Feedback type="invalid">
                                      {meta.error}
                                    </Form.Control.Feedback>
                                  </Form.Group>
                                )}
                              </Field>
                            </Form.Row>
                          </>
                        )}

                        <Form.Row>
                          <Field name="message">
                            {({ field, meta }) => (
                              <Form.Group
                                controlId="message"
                                as={Col}
                                sm={12}
                                md={12}
                                xl={12}
                              >
                                <Form.Label>Message *</Form.Label>
                                <Form.Control
                                  as="textarea"
                                  rows={6}
                                  {...field}
                                  isInvalid={meta.touched && meta.error}
                                  placeholder="Please describe your issue or question..."
                                />
                                <Form.Control.Feedback type="invalid">
                                  {meta.error}
                                </Form.Control.Feedback>
                                <Form.Text className="text-muted">
                                  Maximum 2000 characters.{" "}
                                  {values.message.length}/2000
                                </Form.Text>
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
                              className="text-uppercase shadow-md"
                              type="submit"
                            >
                              Submit
                            </Button>
                          </Col>
                          <Col sm={12} className="mt-3">
                            <small className="form-text text-muted">
                              This site is protected by reCAPTCHA and the Google
                              <a href="https://policies.google.com/privacy">
                                {" "}
                                Privacy Policy{" "}
                              </a>
                              and
                              <a href="https://policies.google.com/terms">
                                {" "}
                                Terms of Service{" "}
                              </a>
                              apply.
                            </small>
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
      </Container>
    </MainLayout>
  );
};

export default ContactUs;
