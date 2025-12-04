import { useState } from "react";
import { Field, Formik } from "formik";
import { Row, Button, Col, Form, Alert } from "react-bootstrap";
import * as Yup from "yup";

import { commitMutation, graphql, useFragment } from "react-relay";
import environment from "../../relayEnvironment";

const query = graphql`
  fragment JoinProjectFormFragment on Query {
    project {
      edges {
        node {
          id
          short
          code
          description
          mainProject {
            name
            telescope {
              name
            }
          }
        }
      }
    }
  }
`;

const mutation = graphql`
  mutation JoinProjectFormMutation(
    $input: CreateProjectMembershipRequestInput!
  ) {
    createProjectMembershipRequest(input: $input) {
      ok
      errors
    }
  }
`;

const validationSchema = Yup.object().shape({
  project: Yup.string().required("Please select a project."),
  message: Yup.string()
    .required("Please include a message.")
    .min(10, "Message must be at least 10 characters long.")
    .max(500, "Message must be at most 500 characters long."),
});

const JoinProjectForm = ({ relayData, onRequestSubmitted }) => {
  const [errors, setErrors] = useState([]);
  const [showErrors, setShowErrors] = useState(false);

  const data = useFragment(query, relayData);
  const groupedProjects = data.project.edges.reduce(
    (acc, { node }) => ({
      ...acc,
      [node.mainProject.name]: [...(acc[node.mainProject.name] || []), node],
    }),
    {}
  );

  const handleJoinProjectRequest = (projectCode, message, resetForm) => {
    commitMutation(environment, {
      mutation: mutation,
      variables: {
        input: {
          projectCode: projectCode,
          message: message,
        },
      },
      onCompleted: ({ createProjectMembershipRequest }, errors) => {
        let formErrors = [];
        if (errors) {
          formErrors.push(...errors.map((e) => e.message));
        }

        if (createProjectMembershipRequest?.errors) {
          formErrors.push(...createProjectMembershipRequest.errors);
        }

        if (formErrors.length > 0) {
          setErrors(formErrors);
          setShowErrors(true);
        }

        if (createProjectMembershipRequest?.ok) {
          resetForm();
          if (onRequestSubmitted) {
            onRequestSubmitted();
          }
        }
      },
      onError: () => {
        setErrors(["Something went wrong, please try later."]);
      },
    });
  };

  return (
    <>
      <Row>
        <Col>
          <h4 className="text-primary-600 mt-5">Join a Project</h4>
        </Col>
      </Row>
      <Row>
        <Col xl={6} md={12}>
          {errors.map((error) => (
            <Alert
              show={showErrors}
              key={error}
              variant="danger"
              dismissible
              onClose={() => setShowErrors(false)}
            >
              {error}
            </Alert>
          ))}
        </Col>
      </Row>
      <Formik
        initialValues={{
          project: "",
          message: "",
        }}
        validationSchema={validationSchema}
        onSubmit={(values, { resetForm }) => {
          // Handle form submission
          handleJoinProjectRequest(values.project, values.message, resetForm);
        }}
      >
        {({ values, handleSubmit }) => (
          <Form onSubmit={handleSubmit} className="mt-4">
            <Form.Row>
              <Col xl={3} md={6}>
                <Field name="project">
                  {({ field, meta }) => (
                    <Form.Group controlId="project">
                      <Form.Label>Project</Form.Label>
                      <Form.Control
                        {...field}
                        as="select"
                        isInvalid={meta.touched && meta.error}
                      >
                        <option value="">Please select a project</option>
                        {Object.entries(groupedProjects).map(
                          ([mainProject, projects]) => (
                            <optgroup label={mainProject} key={mainProject}>
                              {projects.map((project) => (
                                <option value={project.code} key={project.code}>
                                  {`${project.short} - ${project.code}`}
                                </option>
                              ))}
                            </optgroup>
                          )
                        )}
                      </Form.Control>
                      <Form.Control.Feedback type="invalid">
                        {meta.error}
                      </Form.Control.Feedback>
                      {values.project &&
                        data.project.edges.find(
                          ({ node }) => node.code === values.project
                        )?.node.description && (
                          <Form.Text className="text-muted">
                            {
                              data.project.edges.find(
                                ({ node }) => node.code === values.project
                              ).node.description
                            }
                          </Form.Text>
                        )}
                    </Form.Group>
                  )}
                </Field>
              </Col>
            </Form.Row>
            <Form.Row>
              <Col xl={3} md={6}>
                <Field name="message">
                  {({ field, meta }) => (
                    <Form.Group controlId="message">
                      <Form.Label>Message</Form.Label>
                      <Form.Control
                        {...field}
                        as="textarea"
                        rows={8}
                        isInvalid={meta.touched && meta.error}
                      />
                      <Form.Control.Feedback type="invalid">
                        {meta.error}
                      </Form.Control.Feedback>
                    </Form.Group>
                  )}
                </Field>
              </Col>
            </Form.Row>
            <Form.Row>
              <Col className="mt-4">
                <Button type="submit">Send request</Button>
              </Col>
            </Form.Row>
          </Form>
        )}
      </Formik>
    </>
  );
};

export default JoinProjectForm;
