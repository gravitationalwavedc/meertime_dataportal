import { useState } from "react";
import ComparisonImageGrid from "./ComparisonImageGrid";
import LightBox from "react-image-lightbox";
import PlotImage from "./PlotImage";
import ToaImages from "./ToaImages";

const ImageGrid = ({ images }) => {
  const [isLightBoxOpen, setIsLightBoxOpen] = useState(false);

  const rawImages = images.edges.filter(({ node }) => !node.cleaned);
  const processedImages = images.edges.filter(({ node }) => node.cleaned);

  const urls = [
    ...rawImages.map(({ node }) => node.url),
    ...processedImages.map(({ node }) => node.url),
  ];

  const [lightBoxImages, setLightBoxImages] = useState({
    images: urls,
    imagesIndex: 0,
  });

  const openLightBox = (imageUrl) => {
    const { images } = lightBoxImages;
    const imageIndex = images.indexOf(imageUrl);
    setIsLightBoxOpen(true);
    setLightBoxImages({ images: images, imagesIndex: imageIndex });
  };

  return (
    <>
      <ToaImages
        processedImages={processedImages}
        handleLightBox={openLightBox}
      />
      {processedImages.length > 0 ? (
        <ComparisonImageGrid
          rawImages={rawImages}
          processedImages={processedImages}
          openLightBox={openLightBox}
        />
      ) : (
        rawImages.map(({ node }) => (
          <PlotImage
            key={node.image}
            imageData={node}
            handleClick={() => openLightBox(node.url)}
          />
        ))
      )}
      {isLightBoxOpen && (
        <LightBox
          mainSrc={lightBoxImages.images[lightBoxImages.imagesIndex]}
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
          onImageLoad={() => {
            window.dispatchEvent(new Event("resize"));
          }}
        />
      )}
    </>
  );
};

export default ImageGrid;
