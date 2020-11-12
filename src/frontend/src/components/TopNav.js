import React from 'react';
import { Container, Navbar, Nav } from 'react-bootstrap';
import { Link, useRouter } from 'found';

const TopNav = () => {
    const { router } = useRouter();

    const logout = () => {
        sessionStorage.removeItem('jwt');
        router.replace('/');
    };

    return (
        <Navbar bg="dark" variant="dark" className="mb-6">
            <Container>
                <Navbar.Brand href="#home">MEERTIME</Navbar.Brand>
                <Nav className="mr-auto">
                    <Link to='/' exact as={Nav.Link}>Fold</Link>
                    <Nav.Link>Search</Nav.Link>
                </Nav>
                <Nav>
                    <Nav.Link onClick={logout}>Log out</Nav.Link>
                </Nav>
            </Container>
        </Navbar>
    );
};

export default TopNav;
