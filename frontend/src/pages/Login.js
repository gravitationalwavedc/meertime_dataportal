import * as Yup from 'yup';

import { Alert, Button, Card, Col, Container, Form, Row } from 'react-bootstrap';
import { Field, Formik } from 'formik';
import React, { useState } from 'react';
import { commitMutation, graphql } from 'react-relay';

import { HiOutlineLockClosed } from 'react-icons/hi';
import { Link } from 'found';
import environment from '../relayEnvironment';

const mutation = graphql`
  mutation LoginMutation($username: String!, $password: String!) {
    tokenAuth (input: {username: $username, password: $password})
    {
      token
      meerWatchKey
      payload
    }
  }`;

const validationSchema = Yup.object().shape({
    username: Yup.string().required('Please include a username.'),
    password: Yup.string().required('Please include a password.')
});

const Login = ({ router, match }) => {
    const [formErrors, setFormErrors] = useState([]);

    const login = (username, password) => {
        const variables = {
            username: username,
            password: password
        };

        commitMutation(
            environment,
            {
                mutation,
                variables,
                onCompleted: ({ tokenAuth }, errors) => {
                    if (errors) {
                        setFormErrors(errors.map(e => e.message));
                    } else if (tokenAuth) {
                        localStorage.jwt = tokenAuth.token;
                        localStorage.meerWatchKey = tokenAuth.meerWatchKey;
                        localStorage.username = tokenAuth.payload['username'];
                        const nextPath = match.params['next'] === undefined ?
                            process.env.REACT_APP_BASE_URL : `${process.env.REACT_APP_BASE_URL}/${match.params['next']}/`;
                        router.replace(nextPath);
                    }
                },
                onError: () => {
                    setFormErrors(['Please enter valid credentials.']);
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
                                <h4 className="text-primary-600 mb-4">Sign in</h4>
                                <Formik
                                    initialValues={{
                                        username: '',
                                        password: ''
                                    }}
                                    validationSchema={validationSchema}
                                    onSubmit={(values) => login(values.username, values.password)}
                                >
                                    {({ handleSubmit }) =>
                                        <Form onSubmit={handleSubmit}>
                                            <Field name="username">
                                                {({ field, meta }) =>
                                                    <Form.Group controlId="username">
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
                                                            <HiOutlineLockClosed className="form-control-icon-right"/>}
                                                        <Form.Control.Feedback
                                                            type='invalid'>{meta.error}</Form.Control.Feedback>
                                                    </Form.Group>}
                                            </Field>
                                            {formErrors &&
                                                formErrors.map((e) => <Alert variant='danger' key={e}>{e}</Alert>)}
                                            <Row className="buttons-row">
                                                <Col xl={{ span: 12 }} md={{ span: 12 }}>
                                                    <Button
                                                        className="text-uppercase shadow-md mt-2"
                                                        type="submit">Sign in</Button>
                                                </Col>
                                                <Col xl={{ span: 12 }} md={{ span: 12 }}>
                                                    &nbsp;
                                                </Col>
                                                <Col xl={{ span: 12 }} md={{ span: 12 }}>
                                                    <span className="float-right">
                                                        Do not have an account with us?&nbsp;
                                                        <Link
                                                            to={`${process.env.REACT_APP_BASE_URL}/register/`}
                                                        >Register</Link>
                                                    </span>
                                                </Col>
                                                <Col xl={{ span: 12 }} md={{ span: 12 }}>
                                                    <span className="float-right">
                                                        Forgot your account password?&nbsp;
                                                        <Link
                                                            to={`${process.env.REACT_APP_BASE_URL}/password_reset_request/`}
                                                        >Reset Password</Link>
                                                    </span>
                                                </Col>
                                            </Row>
                                        </Form>}
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
