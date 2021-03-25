import { Container, Nav, Navbar } from 'react-bootstrap';
import { Link, useRouter } from 'found';

import React from 'react';

const TopNav = () => {
    const { router } = useRouter();

    const logout = () => {
        sessionStorage.clear();
        localStorage.clear();
        router.replace('/');
    };

    return (
        <Navbar bg="dark" variant="dark" className="mb-5" expand="md">
            <Container>
                <Navbar.Brand href="#home">MEERTIME</Navbar.Brand>
                <Navbar.Toggle aria-controls="top-navbar"/>
                <Navbar.Collapse id="top-navbar">
                    <Nav className="mr-auto">
                        <Link to='/' exact as={Nav.Link}>Folded</Link>
                        <Link to='/search/' exact as={Nav.Link}>Searchmode</Link>
                        <Link to='/last-session/' exact as={Nav.Link}>Last session</Link>
                    </Nav>
                    <Nav>
                        <Nav.Link onClick={logout}>Log out</Nav.Link>
                    </Nav>
                </Navbar.Collapse>
            </Container>
        </Navbar>
    );
};

export default TopNav;
