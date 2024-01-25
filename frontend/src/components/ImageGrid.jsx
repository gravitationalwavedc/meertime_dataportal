import { useState } from "react";
import ComparisonImageGrid from "./ComparisonImageGrid";
import LightBox from "react-image-lightbox";
import PlotImage from "./PlotImage";
import ToaImages from "./ToaImages";
// import { getImageData } from "../pages/RefreshToken.jsx";

const ImageGrid = ({ images, project }) => {
  const [isLightBoxOpen, setIsLightBoxOpen] = useState(false);

  const rawImages = images.edges.filter(({ node }) => !node.cleaned);
  const processedImages = images.edges.filter(({ node }) => node.cleaned);

  const urls = [
    ...rawImages.map(({ node }) => node.url),
    ...processedImages.map(({ node }) => node.url),
  ];

  const [lightBoxImages, setLightBoxImages] = useState({
    // images: [],
    images: urls,
    imagesIndex: 0,
  });

  const openLightBox = (imageUrl) => {
    const images = lightBoxImages.images;
    const imageIndex = images.indexOf(imageUrl);
    setIsLightBoxOpen(true);
    setLightBoxImages({ images: images, imagesIndex: imageIndex });
  };

  // const openLightBox = async (imageUrl) => {
  //   const imagePromises = urls.map((url) => getImageData(url));
  //   const imageData = await Promise.all(imagePromises);
  //   const images = imageData
  //     .filter((data) => data !== null)
  //     .map((data) => data);
  //   const imageIndex = urls.indexOf(imageUrl);
  //
  //   setLightBoxImages({ images, imagesIndex: imageIndex });
  //   setIsLightBoxOpen(true);
  // };

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
          project={project}
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
