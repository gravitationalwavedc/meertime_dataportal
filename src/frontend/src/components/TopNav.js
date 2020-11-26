import { Container, Nav, Navbar } from 'react-bootstrap';
import { Link, useRouter } from 'found';

import React from 'react';

const TopNav = () => {
    const { router } = useRouter();

    const logout = () => {
        sessionStorage.removeItem('jwt');
        router.replace('/');
    };

    return (
        <Navbar bg="dark" variant="dark" className="mb-5">
            <Container>
                <Navbar.Brand href="#home">MEERTIME</Navbar.Brand>
                <Nav className="mr-auto">
                    <Link to='/' exact as={Nav.Link}>Fold</Link>
                    <Link to='/search/' exact as={Nav.Link}>Search</Link>
                </Nav>
                <Nav>
                    <Nav.Link onClick={logout}>Log out</Nav.Link>
                </Nav>
            </Container>
        </Navbar>
    );
};

export default TopNav;
