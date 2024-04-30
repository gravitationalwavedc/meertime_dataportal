import { Image } from "react-bootstrap";
import image404 from "../../assets/images/image404.png";

const SessionImage = ({
  imageHi,
  imageLo,
  images,
  imageIndex,
  openLightBox,
}) => {
  if (imageHi && imageHi.url) {
    const thumbnail = `${import.meta.env.VITE_DJANGO_MEDIA_URL}${
      imageLo && imageLo.url ? imageLo.url : imageHi.url
    }`;
    return (
      <Image
        rounded
        onClick={() => openLightBox(images, imageIndex)}
        fluid
        src={images[imageIndex]}
      />
    );
  }

  return <Image rounded fluid src={image404} />;
};

export default SessionImage;
