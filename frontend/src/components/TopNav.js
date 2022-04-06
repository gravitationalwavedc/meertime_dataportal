import { Container, Nav, Navbar } from 'react-bootstrap';
import { Link, useRouter } from 'found';

import React from 'react';

const TopNav = () => {
    const { router } = useRouter();

    const logout = () => {
        sessionStorage.clear();
        localStorage.clear();
        router.replace(process.env.REACT_APP_BASE_URL);
    };

    return (
        <Navbar bg="dark" variant="dark" className="mb-5" expand="md">
            <Container>
                <Link to={`${process.env.REACT_APP_BASE_URL}/`} exact as ={Navbar.Brand}>MEERTIME</Link>
                <Navbar.Toggle aria-controls="top-navbar"/>
                <Navbar.Collapse id="top-navbar">
                    <Nav className="mr-auto">
                        <Link to={`${process.env.REACT_APP_BASE_URL}/`} exact as={Nav.Link}>Folded</Link>
                        <Link to={`${process.env.REACT_APP_BASE_URL}/search/`} exact as={Nav.Link}>Search mode</Link>
                        <Link 
                            to={`${process.env.REACT_APP_BASE_URL}/last-session/`} 
                            exact 
                            as={Nav.Link}>
                                Last session
                        </Link>
                        <Link to={`${process.env.REACT_APP_BASE_URL}/sessions/`} exact as={Nav.Link}>Sessions</Link>
                    </Nav>
                    <Nav>
                        <Link to={`${process.env.REACT_APP_BASE_URL}/password_change/`} exact as={Nav.Link}>Change Password</Link>
                        <Nav.Link onClick={logout}>Log out</Nav.Link>
                    </Nav>
                </Navbar.Collapse>
            </Container>
        </Navbar>
    );
};

export default TopNav;
