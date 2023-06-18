import Image from "react-bootstrap/Image";
import image404 from "../assets/images/image404.png";

const PlotImage = ({ imageData, handleClick }) => {
  if (!imageData) return null;

  return (
    <Image
      rounded
      fluid
      className="mb-3"
      alt={`Plot ${imageData.plotType} using ${imageData.process} data.`}
      src={`${import.meta.env.VITE_DJANGO_MEDIA_URL}${imageData.url}`}
      onError={({ currentTarget }) => {
        currentTarget.onError = null;
        currentTarget.src = image404;
      }}
      onClick={handleClick}
    />
  );
};

export default PlotImage;
