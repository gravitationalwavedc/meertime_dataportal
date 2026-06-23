import { Col, Row } from "react-bootstrap";
import ImageComparisonRow from "./ImageComparisonRow";
import PlotImage from "./PlotImage";

const ComparisonImageGrid = ({ rawImages, processedImages, openLightBox }) => {
  const comparisonImageTypes = [
    "profile",
    "profile_pol",
    "phase_time",
    "phase_freq",
    "bandpass",
    "dynamic_spectrum",
    "snr_cumul",
    "snr_single",
  ];

  const extraImageOrder = ["toa_single", "rmfit", "dmfit"];

  const hasRaw = rawImages && rawImages.length > 0;
  const hasCleaned = processedImages && processedImages.length > 0;

  return (
    <>
      {(hasRaw || hasCleaned) && (
        <Row>
          {hasRaw && (
            <Col>
              <h5>Raw</h5>
            </Col>
          )}
          {hasCleaned && (
            <Col>
              <h5>Cleaned</h5>
            </Col>
          )}
        </Row>
      )}
      {comparisonImageTypes.map((imageType) => (
        <ImageComparisonRow
          key={`${imageType}`}
          rawImage={rawImages.find(
            ({ node }) => node.imageType.toLowerCase() === imageType
          )}
          processedImage={processedImages.find(
            ({ node }) => node.imageType.toLowerCase() === imageType
          )}
          openLightBox={openLightBox}
        />
      ))}
      {processedImages.length > 0 && (
        <>
          <Row className="mt-5">
            <Col>
              <h5>Cleaned</h5>
            </Col>
          </Row>
          <Row>
            <Col>
              {extraImageOrder.map((imageType) => {
                const edge = processedImages.find(
                  ({ node }) => node.imageType.toLowerCase() === imageType
                );
                if (edge === undefined) return null;
                return (
                  <PlotImage
                    key={imageType}
                    imageData={edge.node}
                    handleClick={() => openLightBox(edge.node.url)}
                  />
                );
              })}
            </Col>
          </Row>
        </>
      )}
    </>
  );
};

export default ComparisonImageGrid;
