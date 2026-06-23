import { Col, Row } from "react-bootstrap";
import PlotImage from "./PlotImage";
import EmptyStateMessage from "./EmptyStateMessage";

const ImageComparisonRow = ({
  sizes,
  rawImage,
  processedImage,
  openLightBox,
}) => {
  const hasRaw = !!(rawImage && rawImage.node);
  const hasProcessed = !!(processedImage && processedImage.node);

  if (!hasRaw && !hasProcessed) {
    return (
      <Row>
        <Col>
          <EmptyStateMessage message="No plot available" />
        </Col>
      </Row>
    );
  }

  return (
    <Row>
      {hasRaw && (
        <Col {...sizes}>
          <PlotImage
            imageData={rawImage.node}
            handleClick={() => openLightBox(rawImage.node.url)}
          />
        </Col>
      )}
      {hasProcessed && (
        <Col {...sizes}>
          <PlotImage
            imageData={processedImage.node}
            handleClick={() => openLightBox(processedImage.node.url)}
          />
        </Col>
      )}
    </Row>
  );
};

export default ImageComparisonRow;
