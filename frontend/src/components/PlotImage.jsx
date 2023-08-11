import Image from "react-bootstrap/Image";
import image404 from "../assets/images/image404.png";
import { useEffect, useState } from "react";
import { getImageData } from "../pages/RefreshToken.jsx";

const PlotImage = ({ imageData, handleClick }) => {
  const [image, setImage] = useState("");

  useEffect(() => {
    if (imageData) {
      getImageData(imageData.url).then((data) => setImage(data));
    }
  });

  return (
    <Image
      rounded
      fluid
      className="mb-3"
      alt={`Plot ${imageData.imageType} `}
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
