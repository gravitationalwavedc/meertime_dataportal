import { useState } from "react";
import LightBox from "react-image-lightbox";
import PlotImage from "./PlotImage";

const MolongloImageGrid = ({ images, project }) => {
  const [isLightBoxOpen, setIsLightBoxOpen] = useState(false);

  const gridImages = images.edges.filter(
    ({ node }) => node.process === project
  );

  const newlightBoxImages = [...gridImages.map(({ node }) => node.url)];

  const [lightBoxImages, setLightBoxImages] = useState({
    images: newlightBoxImages,
    imagesIndex: 0,
  });

  const openLightBox = (imageUrl) => {
    const images = lightBoxImages.images;
    const imageIndex = images.indexOf(imageUrl);
    setIsLightBoxOpen(true);
    setLightBoxImages({ images: images, imagesIndex: imageIndex });
  };

  return (
    <>
      {gridImages.map(({ node }) => (
        <PlotImage
          key={node.url}
          imageData={node}
          handleClick={() => openLightBox(node.url)}
        />
      ))}
      {isLightBoxOpen && (
        <LightBox
          mainSrc={`${import.meta.env.VITE_DJANGO_MEDIA_URL}${
            lightBoxImages.images[lightBoxImages.imagesIndex]
          }`}
          nextSrc={
            lightBoxImages.images[
              (lightBoxImages.imagesIndex + 1) % lightBoxImages.images.length
            ]
          }
          prevSrc={
            lightBoxImages.images[
              (lightBoxImages.imagesIndex + lightBoxImages.images.length - 1) %
                lightBoxImages.images.length
            ]
          }
          onCloseRequest={() => setIsLightBoxOpen(false)}
          onMovePrevRequest={() =>
            setLightBoxImages({
              images: lightBoxImages.images,
              imagesIndex:
                (lightBoxImages.imagesIndex +
                  lightBoxImages.images.length -
                  1) %
                lightBoxImages.images.length,
            })
          }
          onMoveNextRequest={() =>
            setLightBoxImages({
              images: lightBoxImages.images,
              imagesIndex:
                (lightBoxImages.imagesIndex + 1) % lightBoxImages.images.length,
            })
          }
        />
      )}
    </>
  );
};

export default MolongloImageGrid;
