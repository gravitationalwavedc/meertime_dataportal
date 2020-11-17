import React from 'react';
import { Container, Row, Col } from 'react-bootstrap';
import GraphPattern from '../assets/images/graph-pattern.png';
import TopNav from '../components/TopNav';

const MainLayout = ({ title, children }) => 
    <React.Fragment>
        <TopNav/>
        <Container>
            <Row>
                <Col>
                    <h4 className="mb-6 text-primary-600">{ title }</h4>
                </Col>
            </Row>
            <img src={GraphPattern} className="graph-pattern-top" alt=""/>
            { children }
        </Container>
    </React.Fragment>;

export default MainLayout;
