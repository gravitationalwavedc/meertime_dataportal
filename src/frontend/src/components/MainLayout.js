import { Col, Container, Row } from 'react-bootstrap';

import Einstein from '../assets/images/einstein-coloured.png';
import Footer from '../components/Footer';
import GraphPattern from '../assets/images/graph-pattern.png';
import React from 'react';
import TopNav from '../components/TopNav';

const MainLayout = ({ title, subtitle, children }) => 
    <React.Fragment>
        <TopNav/>
        <img src={GraphPattern} className="graph-pattern-top" alt=""/>
        <Container>
            <Row>
                <Col>
                    <h2 className="text-primary-600">{ title }</h2>
                    {subtitle && <h5>{subtitle}</h5>}
                </Col>
                <img src={Einstein} alt=""/>
            </Row>
            { children }
        </Container>
        <Footer/>
    </React.Fragment>;

export default MainLayout;
