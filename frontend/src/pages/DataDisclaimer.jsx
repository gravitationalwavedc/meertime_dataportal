import { Card, Col, Row } from "react-bootstrap";
import MainLayout from "../components/MainLayout";

const DataDisclaimer = () => {
  return (
    <MainLayout title="Data Information & Disclaimer">
      <Row>
        <Col xl={{ span: 10, offset: 1 }} md={{ span: 10, offset: 1 }}>
          <Card className="mb-4">
            <Card.Body>
              <p className="mb-3">
                The details of how the data provided by the Pulsar Portal were
                produced are provided in Bailes et al. 2026 (in prep.) and{" "}
                <a href="https://ui.adsabs.harvard.edu/abs/2020PASA...37...28B/abstract">
                  Bailes et al. 2020
                </a>
                . Some of the data is reprocessed from time to time after the
                initial observation processing. We however note that the data
                may not have been produced using the latest or best ephemerides,
                pulse profile templates, clock files, or software versions. We
                emphasize that our Times of Arrivals and decimated data are
                affected by this. For reproducible, high precision scientific
                results, we suggest the users re-process the high-resolution
                archives we provide or use official data releases (see below).
                You can <a href="/contact-us/">contact us</a> for assistance in
                this matter. We provide below some helpful links which are also
                described in Bailes et al. 2026 (in prep).
              </p>
              <div className="p-3 border rounded bg-light mb-3">
                <p className="mb-2">Data Download Types:</p>
                <ul className="mb-0">
                  <li>
                    <strong>Folding Ephemeris:</strong> Each (processed,
                    fold-mode) observation of a pulsar has a matching PSRCHIVE
                    archive, with a single folding ephemeris. This button
                    displays the latest one the user has access to.
                  </li>
                  <li>
                    <strong>Template:</strong> Each (processed, fold-mode)
                    observation of a pulsar has a corresponding MeerPipe
                    processing, which uses a single template pulse profile for
                    tasks outside of ToA generation. This button displays the
                    latest one the user has access to.
                  </li>
                  <li>
                    <strong>Full Resolution Data:</strong> the cleaned and
                    calibrated PSRCHIVE archive for each (processed, fold-mode)
                    observation the user has access to.
                  </li>
                  <li>
                    <strong>Decimated Data:</strong> the same as above, reduced
                    to one time integration, one channel, and one polarisation
                    (also called profiles).
                  </li>
                  <li>
                    <strong>ToAs:</strong> for each observation of a pulsar the
                    user has access to, all the (32 channel, 1 polarisation, 1
                    subintegration) Times of Arrival produced by projects the
                    user has access to for that date.
                  </li>
                </ul>
              </div>
              <div className="p-3 border rounded bg-light">
                <p className="mb-2">Links:</p>
                <ul className="mb-0">
                  <li>
                    <a
                      href="http://www.meertime.org/data.html"
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      MeerTime data policies and data releases
                    </a>
                  </li>
                  <li>
                    <a
                      href="https://mpta-gw.github.io/data.html"
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      Official MeerKAT pulsar timing array data releases
                    </a>
                  </li>
                  <li>
                    <a
                      href="https://gitlab.com/CAS-eResearch/GWDC/meertime_dataportal"
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      Data Portal Source Code
                    </a>
                  </li>
                  <li>
                    <a
                      href="https://github.com/nf-core/meerpipe"
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      MeerPipe: our data processing pipeline
                    </a>
                  </li>
                  <li>
                    <a
                      href="https://github.com/OZGrav/psrdb"
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      PSRDB: a command-line tool to access the Pulsar Portal
                      database's <a href="/api-tokens/">API</a>
                    </a>
                  </li>
                  <li>
                    <a
                      href="https://github.com/OZGrav/pulsar_paragraph"
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      Pulsar summary paragraph generation tool
                    </a>
                  </li>
                  <li>
                    <a
                      href="https://github.com/danielreardon/MeerGuard"
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      MeerGuard: our RFI cleaning package
                    </a>
                  </li>
                  <li>
                    <a
                      href="https://github.com/danielreardon/scintools"
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      Scintools: used to produce dynamic spectra plots
                    </a>
                  </li>
                  <li>
                    <a
                      href="https://ozgrav.github.io/meerkat_pulsar_docs/meerkat_pulsar_summary/"
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      MeerKAT pulsar timing data processing summary
                    </a>
                  </li>
                  <li>
                    <a
                      href="https://archive-gw-1.kat.ac.za/public/tfr/mk2utc.clk"
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      MeerKAT clock correction files
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

export default DataDisclaimer;
