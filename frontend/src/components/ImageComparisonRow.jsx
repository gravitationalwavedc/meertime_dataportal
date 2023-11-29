import { Col, Row } from "react-bootstrap";
import PlotImage from "./PlotImage";

const ImageComparisonRow = ({
  sizes,
  rawImage,
  processedImage,
  openLightBox,
}) => (
  <Row>
    <Col {...sizes}>
      <PlotImage
        imageData={rawImage ? rawImage.node : null}
        handleClick={() => openLightBox(rawImage.node.image)}
      />
    </Col>
    <Col {...sizes}>
      <PlotImage
        imageData={processedImage ? processedImage.node : null}
        handleClick={() => openLightBox(processedImage.node.image)}
      />
    </Col>
  </Row>
);

export default ImageComparisonRow;
