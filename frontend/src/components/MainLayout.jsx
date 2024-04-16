import { Suspense } from "react";
import { Col, Container, Row } from "react-bootstrap";
import Einstein from "../assets/images/einstein-coloured.png";
import Footer from "../components/Footer";
import GraphPattern from "../assets/images/graph-pattern.png";
import ReactMarkdown from "react-markdown";
import TopNav from "../components/TopNav";
import { useScreenSize } from "../context/screenSize-context";

const MainLayout = ({ title, subtitle, description, children }) => {
  const { screenSize } = useScreenSize();
  return (
    <>
      <TopNav />
      <img src={GraphPattern} className="graph-pattern-top" alt="" />
      <Container>
        <Row>
          <Col>
            {screenSize === "xs" ? (
              <>
                <h4 className="text-primary-600">{title}</h4>
                {subtitle && <h5>{subtitle}</h5>}
              </>
            ) : (
              <>
                <h2 className="text-primary-600">{title}</h2>
                {subtitle && <h5>{subtitle}</h5>}
              </>
            )}
          </Col>
        </Row>
        <img src={Einstein} alt="" className="einstein-image" />
        {description && (
          <Row className="mb-3">
            <Col md={5}>
              <ReactMarkdown>{description}</ReactMarkdown>
            </Col>
          </Row>
        )}
        <Suspense
          fallback={
            <div>
              <h3>Loading...</h3>
            </div>
          }
        >
          {children}
        </Suspense>
      </Container>
      <Footer />
    </>
  );
};

export default MainLayout;
