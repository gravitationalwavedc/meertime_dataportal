import React, { useEffect, useState } from 'react';
import ComparisonImageGrid from './ComparisonImageGrid';
import LightBox from 'react-image-lightbox';
import ToaImages from './ToaImages';

const ImageGrid = ({ images, project }) => {
    const [isLightBoxOpen, setIsLightBoxOpen] = useState(false);
    const [lightBoxImages, setLightBoxImages] = useState({ images: [], imagesIndex: 0 });
    const [rawImages, setRawImages] = useState([]);
    const [processedImages, setProcessedImages] = useState([]);

    useEffect(() => {
        const newRawImages = images.edges.filter(
            ({ node }) => node.process.toLowerCase() === 'raw' && node.resolution === 'hi'
        );

        const newProcessedImages = images.edges.filter(
            ({ node }) => node.process.toLowerCase() !== 'raw' && node.process.toLowerCase() === project.toLowerCase()
        );

        const newLightBoxImages = [
            ...newRawImages.map(({ node }) => node.url),
            ...newProcessedImages.map(({ node }) => node.url)
        ];

        setRawImages(newRawImages);
        setProcessedImages(newProcessedImages);
        setLightBoxImages({ images: newLightBoxImages, imagesIndex: 0 });
    }, [project, images.edges]);

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
        <ComparisonImageGrid 
            rawImages={rawImages}
            processedImages={processedImages}
            openLightBox={openLightBox}
            project={project}/>
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
