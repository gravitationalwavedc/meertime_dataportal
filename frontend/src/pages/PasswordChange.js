import * as Yup from 'yup';
//
import { Alert, Button, Col, Form, Row } from 'react-bootstrap';
import { Field, Formik } from 'formik';
import React, { useState } from 'react';
import { commitMutation, graphql } from 'react-relay';
import { HiOutlineLockClosed } from 'react-icons/hi';
import MainLayout from '../components/MainLayout';
import environment from '../relayEnvironment';


const mutation = graphql`
  mutation PasswordChangeMutation($username: String!, $old_password: String!, $password: String!) {
    passwordChange(username: $username, oldPassword: $old_password, password: $password)
    {
      ok,
      user {
        id,
        username,
        email,
      },
      errors,
    }
  }`;

const validationSchema = Yup.object().shape({
    password: Yup.string()
        .required('Please include a password.')
        .matches(/^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%^&*])/,
            'Uppercase, Lowercase, Number and Special Character')
        .matches(/^(?=.{8,})/,
            'Must Contain 8 Characters')
        .notOneOf([Yup.ref('old_password'), null], 'New password is same as current.')
    ,
    confirm_password: Yup.string().oneOf([Yup.ref('password'), null], 'Passwords must match'),
});

const PasswordChange = ({ router, match }) => {
    const [formErrors, setFormErrors] = useState([]);
    const [success, setSuccess] = useState(false);

    const passwordChange = (username, old_password, password) => {
        const variables = {
            username: username,
            old_password: old_password,
            password: password,
        };

        commitMutation(
            environment,
            {
                mutation,
                variables,
                onCompleted: ({ passwordChange }) => {
                    if (passwordChange.errors) {
                        // uncomment the following line to see the errors
                        // console.log(createPasswordChange.errors); // eslint-disable-line no-console
                        setFormErrors(passwordChange.errors);
                    } else if (passwordChange.user) {
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
        <MainLayout title='Change Password'>
            <Row>
                <Col xl={{ span: 4, offset: 1 }} md={{ span: 6, offset: 1 }} sm={{ span: 10, offset: 1 }}>
                    {success &&
                        <div>
                            <h5>Password Change Successful</h5>
                            <div>You can logout and then login using your new password via the login page.</div>
                            <div>&nbsp;</div>
                        </div>
                    }
                    {
                        <Formik
                            initialValues={{
                                old_password: '',
                                password: '',
                                confirm_password: '',
                            }}
                            validationSchema={validationSchema}
                            onSubmit={(values) => passwordChange(
                                localStorage.username,
                                values.old_password,
                                values.password,
                            )}
                        >
                            {({ handleSubmit }) =>
                                <Form onSubmit={handleSubmit}>
                                    <Field name="old_password">
                                        {({ field, meta }) =>
                                            <Form.Group controlId="old_password">
                                                <Form.Label>Current Password</Form.Label>
                                                <Form.Control
                                                    type="password"
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
                                                <Form.Label>New Password</Form.Label>
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
                                                <Form.Label>Confirm New Password</Form.Label>
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
                                    <Row className="buttons-row">
                                        <Col xl={{ span: 12 }} md={{ span: 12 }}>
                                            <Button
                                                className="text-uppercase shadow-md mt-2 float-right"
                                                type="submit">Change Password</Button>
                                        </Col>
                                    </Row>
                                </Form>}
                        </Formik>}
                </Col>
            </Row>

        </MainLayout>

    );
};

export default PasswordChange;
