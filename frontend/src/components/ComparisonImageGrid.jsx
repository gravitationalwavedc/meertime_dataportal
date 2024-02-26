import { Col, Row } from "react-bootstrap";
import ImageComparisonRow from "./ImageComparisonRow";
import PlotImage from "./PlotImage";
import { formatProjectName } from "../helpers";

const ComparisonImageGrid = ({
  rawImages,
  processedImages,
  openLightBox,
}) => {
  const comparisonImageTypes = [
    "profile",
    "profile_pol",
    "phase_time",
    "phase_freq",
    "bandpass",
    "snr_cumul",
    "snr_single",
  ];

  const extraImageOrder = [];

  return (
    <>
      <Row>
        <Col>
          <h5>Raw</h5>
        </Col>
        <Col>
          <h5>Cleaned</h5>
        </Col>
      </Row>
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
