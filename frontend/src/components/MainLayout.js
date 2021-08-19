import { Col, Container, Row } from 'react-bootstrap';

import Einstein from '../assets/images/einstein-coloured.png';
import Footer from '../components/Footer';
import GraphPattern from '../assets/images/graph-pattern.png';
import React from 'react';
import TopNav from '../components/TopNav';
import { useScreenSize } from '../context/screenSize-context';

const MainLayout = ({ title, subtitle, children }) => {
    const { screenSize } = useScreenSize();
    return (
        <React.Fragment>
            <TopNav/>
            <img src={GraphPattern} className="graph-pattern-top" alt=""/>
            <Container>
                <Row>
                    <Col>
                        { screenSize === 'xs' ? 
                            <React.Fragment>
                                <h4 className="text-primary-600">{ title }</h4>
                                { subtitle && <h5>{subtitle}</h5> }
                            </React.Fragment> :
                            <React.Fragment>
                                <h2 className="text-primary-600">{ title }</h2>
                                { subtitle && <h5>{subtitle}</h5> }
                            </React.Fragment>
                        }
                    </Col>
                    <img src={Einstein} alt="" className="d-none d-md-block"/>
                </Row>
                { children }
            </Container>
            <Footer/>
        </React.Fragment>
    );
};

export default MainLayout;
