import { Button, Col, Form, Row, Card } from "react-bootstrap";
import { Field, Formik } from "formik";

const CreateTokenForm = ({ onSubmit, onCancel }) => {
  return (
    <Card className="mb-3">
      <Card.Body>
        <h6>Create New Token</h6>
        <Formik
          initialValues={{
            tokenName: "",
          }}
          onSubmit={(values) => onSubmit(values.tokenName)}
        >
          {({ handleSubmit }) => (
            <Form onSubmit={handleSubmit}>
              <Row>
                <Col md={8}>
                  <Field name="tokenName">
                    {({ field, meta }) => (
                      <Form.Group controlId="tokenName">
                        <Form.Label>Token Name</Form.Label>
                        <Form.Control
                          type="text"
                          {...field}
                          isInvalid={meta.touched && meta.error}
                          placeholder="Enter a descriptive name for your token"
                          required
                        />
                        <Form.Control.Feedback type="invalid">
                          {meta.error}
                        </Form.Control.Feedback>
                      </Form.Group>
                    )}
                  </Field>
                </Col>
                <Col md={4}>
                  <Form.Group>
                    <Form.Label>&nbsp;</Form.Label>
                    <Button
                      type="submit"
                      variant="success"
                      className="w-100 d-block"
                    >
                      Generate Token
                    </Button>
                  </Form.Group>
                </Col>
              </Row>
            </Form>
          )}
        </Formik>
      </Card.Body>
    </Card>
  );
};

export default CreateTokenForm;
