import React from 'react';
import { Navbar, Nav } from 'react-bootstrap';

const TopNav = () => 
    <Navbar>
        <Navbar.Brand href="#home">MEERTIME</Navbar.Brand>
        <Nav className="mr-auto">
            <Nav.Link>Fold</Nav.Link>
            <Nav.Link>Search</Nav.Link>
        </Nav>
        <Nav>
            <Nav.Link>Log out</Nav.Link>
        </Nav>
    </Navbar>;

export default TopNav;
