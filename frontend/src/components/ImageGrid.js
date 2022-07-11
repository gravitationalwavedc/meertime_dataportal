import { Col, Image } from 'react-bootstrap';
import React, { useEffect, useState } from 'react';
import LightBox from 'react-image-lightbox';
import { formatProjectName } from '../helpers';
import image404 from '../assets/images/image404.png';

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

    const sizes = processedImages.length > 0 ? { sm: 6, md: 2, xl: 3 } : { sm: 12, md: 4, xl: 6 };

    const openLightBox = (images, imageUrl) => {
        const imageIndex = images.indexOf(imageUrl);
        setIsLightBoxOpen(true);
        setLightBoxImages({ images: images, imagesIndex: imageIndex });
    };

    return <React.Fragment>
        <Col {...sizes}>
            <h4>Raw</h4>
            {rawImages.map(({ node }) =>
                <Image
                    rounded
                    fluid
                    className="mb-3"
                    alt={`Plot ${node.plotType} using ${node.process} data.`}
                    key={node.url}
                    src={`${process.env.REACT_APP_MEDIA_URL}${node.url}`}
                    onError={({ currentTarget }) => {
                        currentTarget.onError = null;
                        currentTarget.src = image404;
                    }}
                    onClick={() => openLightBox(lightBoxImages.images, node.url)}
                />
            )}
        </Col>
        {processedImages.length > 0 && <Col sm={6} md={2} xl={3}>
            <h4>Cleaned by {formatProjectName(project)}</h4>
            {processedImages.map(({ node }) =>
                <Image
                    rounded
                    fluid
                    className="mb-3"
                    alt={`Plot ${node.plotType} using ${node.process} data.`}
                    key={node.url}
                    src={`${process.env.REACT_APP_MEDIA_URL}${node.url}`}
                    onError={({ currentTarget }) => {
                        currentTarget.onError = null;
                        currentTarget.src = image404;
                    }}
                    onClick={() => openLightBox(lightBoxImages.images, node.url)}
                />
            )}
        </Col>}
        {isLightBoxOpen &&
            <LightBox
                mainSrc={`${process.env.REACT_APP_MEDIA_URL}${lightBoxImages.images[lightBoxImages.imagesIndex]}`}
                nextSrc={lightBoxImages.images[(lightBoxImages.imagesIndex + 1) % lightBoxImages.images.length]}
                prevSrc={
                    lightBoxImages.images[(
                        lightBoxImages.imagesIndex + lightBoxImages.images.length - 1) % lightBoxImages.images.length]}
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
