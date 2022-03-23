import * as Yup from 'yup';

import { Alert, Button, Card, Col, Container, Form, Row } from 'react-bootstrap';
import { Field, Formik } from 'formik';
import React, { useState } from 'react';
import { commitMutation, graphql } from 'react-relay';

import { HiOutlineLockClosed } from 'react-icons/hi';
import { Link } from 'found';
import environment from '../relayEnvironment';

const mutation = graphql`
  mutation RegisterMutation($first_name: String!, $last_name: String!, $email: String!, $password: String!) {
    createRegistration(input: {
      firstName: $first_name, 
      lastName: $last_name, 
      email: $email, 
      password: $password,
      })
    {
      ok,
      registration {
        id,
        verificationExpiry,
      },
      errors,
    }
  }`;

const validationSchema = Yup.object().shape({
    first_name: Yup.string().required('Please include a first name.'),
    last_name: Yup.string().required('Please include a last name.'),
    email: Yup.string().email('Invalid email format.').required('Please include an email.'),
    password: Yup.string()
        .required('Please include a password.')
        .matches(/^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%^&*])/,
            'One Uppercase, One Lowercase, One Number and One Special Case Character')
        .matches(/^(?=.{8,})/,
            'Must Contain 8 Characters'),
    confirm_password: Yup.string().oneOf([Yup.ref('password'), null], 'Passwords must match'),
});

const Register = ({ router, match }) => {
    const [formErrors, setFormErrors] = useState([]);
    const [success, setSuccess] = useState(true);

    const register = (first_name, last_name, email, password, confirm_password) => {
        const variables = {
            first_name: first_name,
            last_name: last_name,
            email: email,
            password: password,
            confirm_password: confirm_password,
        };

        commitMutation(
            environment,
            {
                mutation,
                variables,
                onCompleted: ({ createRegistration }) => {
                    if (createRegistration.errors) {
                        // uncomment the following line to see the errors
                        // console.log(createRegistration.errors); // eslint-disable-line no-console
                        setFormErrors(createRegistration.errors);
                    } else if (createRegistration.registration) {
                        setSuccess(true);
                    }
                },
                onError: errors => {
                    // this is RelayNetworkLayer Error
                    // console.log(errors); // eslint-disable-line no-console
                    setFormErrors(['Something went wrong, please try later.']);
                },
            }
        );
    };

    return (
        <Container fluid className="login-page h-100">
            <Col xl={{ span: 6, offset: 5 }} md={{ span: 10, offset: 1 }} className="login-col h-100">
                <Row>
                    <h1 className="text-gray-100 w-100 mt-5 text-center d-none d-sm-block"
                        style={{ marginBottom: '-3rem' }}>
                        MEERTIME</h1>
                    <h2 className="text-gray-100 w-100 mt-5 text-center d-block d-sm-none"
                        style={{ marginBottom: '-3rem' }}>
                        MEERTIME</h2>
                    <Col xl={{ span: 8, offset: 2 }} md={{ span: 8, offset: 2 }} className="login-form">
                        <Card className="shadow-2xl text-left">
                            <Card.Body className="m-4">
                                <h4 className="text-primary-600 mb-4">Register</h4>
                                { success &&
                                    <div>
                                        <h5>Registration Successful</h5>
                                        <div>You will receive an email with the verification link soon. You need to
                                        verify your email address within 48 hours.
                                        </div>
                                        <Link
                                            className="shadow-md mt-2"
                                            to={`${process.env.REACT_APP_BASE_URL}/login/`}
                                        >Login</Link>
                                    </div>
                                }
                                {!success &&
                                    <Formik
                                        initialValues={{
                                            first_name: '',
                                            last_name: '',
                                            password: '',
                                            confirm_password: '',
                                            email: '',

                                        }}
                                        validationSchema={validationSchema}
                                        onSubmit={(values) => register(
                                            values.first_name,
                                            values.last_name,
                                            values.email,
                                            values.password,
                                        )}
                                    >
                                        {({ handleSubmit }) =>
                                            <Form onSubmit={handleSubmit}>
                                                <Field name="first_name">
                                                    {({ field, meta }) =>
                                                        <Form.Group controlId="first_name">
                                                            <Form.Label>First Name</Form.Label>
                                                            <Form.Control
                                                                {...field}
                                                                isInvalid={meta.touched && meta.error}/>
                                                            <Form.Control.Feedback
                                                                type='invalid'>
                                                                {meta.error}
                                                            </Form.Control.Feedback>
                                                        </Form.Group>
                                                    }
                                                </Field>
                                                <Field name="last_name">
                                                    {({ field, meta }) =>
                                                        <Form.Group controlId="last_name">
                                                            <Form.Label>Last Name</Form.Label>
                                                            <Form.Control
                                                                {...field}
                                                                isInvalid={meta.touched && meta.error}/>
                                                            <Form.Control.Feedback
                                                                type='invalid'>
                                                                {meta.error}
                                                            </Form.Control.Feedback>
                                                        </Form.Group>
                                                    }
                                                </Field>
                                                <Field name="email">
                                                    {({ field, meta }) =>
                                                        <Form.Group controlId="email">
                                                            <Form.Label>Email</Form.Label>
                                                            <Form.Control
                                                                {...field}
                                                                isInvalid={meta.touched && meta.error}/>
                                                            <Form.Control.Feedback
                                                                type='invalid'>
                                                                {meta.error}
                                                            </Form.Control.Feedback>
                                                        </Form.Group>
                                                    }
                                                </Field>
                                                <Field name="password">
                                                    {({ field, meta }) =>
                                                        <Form.Group controlId="password">
                                                            <Form.Label>Password</Form.Label>
                                                            <Form.Control
                                                                type="password"
                                                                {...field}
                                                                isInvalid={meta.touched && meta.error}/>
                                                            {!meta.error
                                                                &&
                                                                <HiOutlineLockClosed
                                                                    className="form-control-icon-right"/>}
                                                            <Form.Control.Feedback
                                                                type='invalid'>{meta.error}</Form.Control.Feedback>
                                                        </Form.Group>}
                                                </Field>
                                                <Field name="confirm_password">
                                                    {({ field, meta }) =>
                                                        <Form.Group controlId="confirm_password">
                                                            <Form.Label>Confirm Password</Form.Label>
                                                            <Form.Control
                                                                type="password"
                                                                {...field}
                                                                isInvalid={meta.touched && meta.error}/>
                                                            {!meta.error
                                                                &&
                                                                <HiOutlineLockClosed
                                                                    className="form-control-icon-right"/>}
                                                            <Form.Control.Feedback
                                                                type='invalid'>{meta.error}</Form.Control.Feedback>
                                                        </Form.Group>}
                                                </Field>
                                                {formErrors &&
                                                    formErrors.map((e) => <Alert variant='danger' key={e}>{e}</Alert>)}
                                                <Button
                                                    className="text-uppercase shadow-md mt-2"
                                                    type="submit">Register</Button>
                                                <Link
                                                    className="shadow-md mt-2"
                                                    to={`${process.env.REACT_APP_BASE_URL}/login/`}
                                                >Already Have an Account (Login)</Link>
                                            </Form>}
                                    </Formik>}
                            </Card.Body>
                        </Card>
                    </Col>
                </Row>
            </Col>
        </Container>
    );
};

export default Register;
