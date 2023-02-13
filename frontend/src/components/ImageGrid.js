import React, { useState } from 'react';
import ComparisonImageGrid from './ComparisonImageGrid';
import LightBox from 'react-image-lightbox';
import PlotImage from './PlotImage';
import ToaImages from './ToaImages';

const ImageGrid = ({ images, project }) => {
    const [isLightBoxOpen, setIsLightBoxOpen] = useState(false);

    const rawImages = images.edges.filter(
        ({ node }) => node.process.toLowerCase() === 'raw' && node.resolution === 'hi'
    );

    const processedImages = images.edges.filter(
        ({ node }) => node.process.toLowerCase() !== 'raw' && node.process.toLowerCase() === project.toLowerCase()
    );

    const newlightBoxImages = [
        ...rawImages.map(({ node }) => node.url),
        ...processedImages.map(({ node }) => node.url)
    ];

    const [lightBoxImages, setLightBoxImages] = useState({ images: newlightBoxImages, imagesIndex: 0 });

    const openLightBox = (imageUrl) => {
        const images = lightBoxImages.images;
        const imageIndex = images.indexOf(imageUrl);
        setIsLightBoxOpen(true);
        setLightBoxImages({ images: images, imagesIndex: imageIndex });
    };

    return <React.Fragment>
        <ToaImages
            processedImages={processedImages}
            handleLightBox={openLightBox}
        />
        {processedImages.length > 0 ? <ComparisonImageGrid
            rawImages={rawImages}
            processedImages={processedImages}
            openLightBox={openLightBox}
            project={project} /> :
            rawImages.map(({ node }) =>
                <PlotImage
                    key={node.url}
                    imageData={node}
                    handleClick={() => openLightBox(node.url)}
                />
            )
        }
        {isLightBoxOpen &&
            <LightBox
                mainSrc={`${process.env.REACT_APP_MEDIA_URL}${lightBoxImages.images[lightBoxImages.imagesIndex]}`}
                nextSrc={lightBoxImages.images[(lightBoxImages.imagesIndex + 1) % lightBoxImages.images.length]}
                prevSrc={
                    lightBoxImages.images[(lightBoxImages.imagesIndex + lightBoxImages.images.length - 1)
                    % lightBoxImages.images.length
                    ]}
                onCloseRequest={() => setIsLightBoxOpen(false)}
                onMovePrevRequest={() =>
                    setLightBoxImages({
                        images: lightBoxImages.images,
                        imagesIndex: (
                            lightBoxImages.imagesIndex + lightBoxImages.images.length - 1
                        ) % lightBoxImages.images.length,
                    })
                }
                onMoveNextRequest={() =>
                    setLightBoxImages({
                        images: lightBoxImages.images,
                        imagesIndex: (lightBoxImages.imagesIndex + 1) % lightBoxImages.images.length,
                    })
                }
            />
        }
    </React.Fragment>;
};

export default ImageGrid;
