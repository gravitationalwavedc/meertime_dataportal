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
                        setLoadState('error');
                        setErrorMessage(verifyRegistration.errors[0]);
                    } else if (verifyRegistration.registration) {
                        setLoadState('complete');
                    }
                },
                onError: errors => {
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
                                        <div>Your email address has been verified successfully. You should be able to
                                            login to the system using the login page. Please follow the login link
                                            below to access it.
                                        </div>
                                        <Row className="buttons-row">
                                            <Col sm={{ span: 12 }} xl={{ span: 12 }} md={{ span: 12 }}>
                                                &nbsp;
                                            </Col>
                                            <Col xl={{ span: 12 }} md={{ span: 12 }}>
                                                <span>
                                                    Have an account?&nbsp;
                                                    <Link
                                                        to={`${process.env.REACT_APP_BASE_URL}/login/`}
                                                    >Login</Link>
                                                </span>
                                            </Col>
                                        </Row>
                                    </div>
                                }
                                {loadState === 'in-progress' &&
                                    <div>
                                        <h5>Email verification in progress</h5>
                                        <div>We are verifying your email address. Please wait.</div>
                                        <Row className="buttons-row">
                                            <Col sm={{ span: 12 }} xl={{ span: 12 }} md={{ span: 12 }}>
                                                &nbsp;
                                            </Col>
                                            <Col xl={{ span: 12 }} md={{ span: 12 }}>
                                                <span>
                                                    Have an account?&nbsp;
                                                    <Link
                                                        to={`${process.env.REACT_APP_BASE_URL}/login/`}
                                                    >Login</Link>
                                                </span>
                                            </Col>
                                        </Row>
                                    </div>
                                }
                                {loadState === 'error' &&
                                    <div>
                                        <h5>Email verification failed</h5>
                                        <div>We cannot verify your email due the error:
                                            <br /><strong>{ errorMessage }</strong>
                                        </div>
                                        <Row className="buttons-row">
                                            <Col sm={{ span: 12 }} xl={{ span: 12 }} md={{ span: 12 }}>
                                                &nbsp;
                                            </Col>
                                            <Col xl={{ span: 12 }} md={{ span: 12 }}>
                                                <span>
                                                    Have an account?&nbsp;
                                                    <Link
                                                        to={`${process.env.REACT_APP_BASE_URL}/login/`}
                                                    >Login</Link>
                                                </span>
                                            </Col>
                                        </Row>
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
