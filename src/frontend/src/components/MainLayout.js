import { Col, Container, Row } from 'react-bootstrap';

import Footer from '../components/Footer';
import GraphPattern from '../assets/images/graph-pattern.png';
import React from 'react';
import TopNav from '../components/TopNav';

const MainLayout = ({ title, subtitle, children }) => 
    <React.Fragment>
        <TopNav/>
        <Container>
            <Row>
                <Col>
                    <h2 className="mb-6 text-primary-600">{ title }</h2>
                </Col>
            </Row>
            <img src={GraphPattern} className="graph-pattern-top" alt=""/>
            { children }
        </Container>
        <Footer/>
    </React.Fragment>;

export default MainLayout;
