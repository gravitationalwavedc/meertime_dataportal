import { Card, Col, Row } from "react-bootstrap";
import MainLayout from "../components/MainLayout";

const DataUsage = () => {
  return (
    <MainLayout>
      <Row>
        <Col xl={{ span: 10, offset: 1 }} md={{ span: 10, offset: 1 }}>
          <Card className="mb-4">
            <Card.Header>
              <h5 className="mb-0">Data Usage</h5>
            </Card.Header>
            <Card.Body>
              <p className="mb-3">
                If you make use of public data from the Pulsar portal, please
                first read our <a href="/data-disclaimer/">disclaimer</a>. In
                your publications, first, please cite the project from which the
                data is taken. Then, please acknowledge the Pulsar Portal,
                citing its URL and our publication (Bailes et al. 2026 in prep).
              </p>
              <div className="p-3 border rounded bg-light">
                <p className="mb-2">Links:</p>
                <ul className="mb-0">
                  <li>
                    <a
                      href="http://www.meertime.org/publications.html"
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      MeerTime publications
                    </a>{" "}
                    (Publication numbers: all MeerTime projects: 1 and 3, TPA:
                    2, GC: 9, RelBin: 8, PTA: 54.)
                  </li>
                  <li>
                    <a
                      href="https://mpta-gw.github.io/publications.html"
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      MeerKAT Pulsar Timing Array (PTA2, after 2025)
                      publications
                    </a>
                  </li>
                </ul>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </MainLayout>
  );
};

export default DataUsage;
