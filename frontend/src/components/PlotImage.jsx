import Image from "react-bootstrap/Image";
import image404 from "../assets/images/image404.png";
import { useEffect, useState } from "react";
// import { getImageData } from "../pages/RefreshToken.jsx";

const PlotImage = ({ imageData, handleClick }) => {
  if (!imageData) return null;

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

  //   const [image, setImage] = useState("");
  //
  //   useEffect(() => {
  //     if (imageData) {
  //       getImageData(imageData.url).then((data) => setImage(data));
  //     }
  //   });
  //
  //   return (
  //     <>
  //       {imageData ? (
  //         <Image
  //           rounded
  //           fluid
  //           className="mb-3"
  //           alt={`Plot ${imageData.plotType} using ${imageData.process} data.`}
  //           src={image}
  //           onError={({ currentTarget }) => {
  //             currentTarget.onError = null;
  //             currentTarget.src = image404;
  //           }}
  //           onClick={handleClick}
  //         />
  //       ) : (
  //         <Image
  //           rounded
  //           fluid
  //           className="mb-3"
  //           alt={`Image not found.`}
  //           src={image404}
  //           onError={({ currentTarget }) => {
  //             currentTarget.onError = null;
  //             currentTarget.src = image404;
  //           }}
  //           onClick={handleClick}
  //         />
  //       )}
  //     </>
  //   );
};

export default PlotImage;
