import { Card, Col, Container, Row } from 'react-bootstrap';
import React, { useEffect, useState } from 'react';
import { commitMutation, graphql } from 'react-relay';
import { Link } from 'found';
import environment from '../relayEnvironment';

const mutation = graphql`
  mutation RegisterVerifyMutation($verification_code: String!) {
    verifyRegistration(verificationCode: $verification_code)
    {
      ok,
      registration {
        email,
        status,
      },
      errors,
    }
  }`;

const RegisterVerify = ({ match: { params: { code } } }) => {
    const [loadState, setLoadState] = useState('in-progress');
    const [errorMessage, setErrorMessage] = useState('');

    useEffect(() => {
        if (loadState !== 'in-progress') {
            return;
        }

        const variables = {
            verification_code: code,
        };

        commitMutation(
            environment,
            {
                mutation,
                variables,
                onCompleted: ({ verifyRegistration }) => {
                    if (verifyRegistration.errors) {
                        // uncomment the following line to see the errors
                        // console.log(verifyRegistration.errors); // eslint-disable-line no-console
                        setLoadState('error');
                        setErrorMessage(verifyRegistration.errors[0]);
                    } else if (verifyRegistration.registration) {
                        setLoadState('complete');
                    }
                },
                onError: errors => {
                    // this is RelayNetworkLayer Error
                    // console.log(errors); // eslint-disable-line no-console
                    setLoadState('error');
                    setErrorMessage('Something went wrong, please try later.');
                },
            }
        );
    });

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
                                {loadState === 'complete' &&
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
                                {loadState === 'in-progress' &&
                                    <div>
                                        <h5>Email verification in progress</h5>
                                        <div>We are verifying your email address. Please wait.</div>
                                        <Link
                                            className="shadow-md mt-2"
                                            to={`${process.env.REACT_APP_BASE_URL}/login/`}
                                        >Login</Link>
                                    </div>
                                }
                                {loadState === 'error' &&
                                    <div>
                                        <h5>Email verification failed</h5>
                                        <div>We cannot verify your email due the error
                                            : <strong>{ errorMessage }</strong>
                                        </div>
                                        <Link
                                            className="shadow-md mt-2"
                                            to={`${process.env.REACT_APP_BASE_URL}/login/`}
                                        >Login</Link>
                                    </div>
                                }
                            </Card.Body>
                        </Card>
                    </Col>
                </Row>
            </Col>
        </Container>
    );
};

export default RegisterVerify;
