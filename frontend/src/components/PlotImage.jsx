import Image from "react-bootstrap/Image";
import image404 from "../assets/images/image404.png";

const PlotImage = ({ imageData, handleClick }) => {
  if (!imageData) {
    return null;
  }

  const cleaned_str = imageData.cleaned ? "cleaned" : "raw";

  return (
    <Image
      rounded
      fluid
      className="mb-3"
      alt={`Plot ${imageData.imageType} ${cleaned_str}`}
      src={imageData.url}
      onError={({ currentTarget }) => {
        currentTarget.onError = null;
        currentTarget.src = image404;
      }}
      onClick={handleClick}
    />
  );
};

export default PlotImage;
