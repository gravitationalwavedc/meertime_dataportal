import { Col, Image } from 'react-bootstrap';
import React, { useState } from 'react';
import LightBox from 'react-image-lightbox';
import image404 from '../assets/images/image404.png';

const ImageGrid = ({ images }) => {
    const [isLightBoxOpen, setIsLightBoxOpen] = useState(false);

    const rawImages = images.edges.filter(
        ({ node }) => node.process.toLowerCase() === 'raw' && node.resolution === 'hi'
    );

    const processedImages = images.edges.filter(
        ({ node }) => node.process.toLowerCase() !== 'raw' 
    );

    const [lightBoxImages, setLightBoxImages] = useState({ images: [
        ...rawImages.map(({ node }) => node.url), 
        ...processedImages.map(({ node }) => node.url)
    ], imagesIndex: 0 });

    const sizes = processedImages.length > 0 ? { sm:6, md:2, xl:3 } : { sm:12, md:4, xl:6 };

    const openLightBox = (images, imageIndex) => {
        console.log(images, imageIndex);
        console.log(lightBoxImages.images[lightBoxImages.imagesIndex]);
        setIsLightBoxOpen(true);
        setLightBoxImages({ images: images, imagesIndex: imageIndex });
    };

    return <React.Fragment>
        <Col {...sizes}>
            {rawImages.map(({ node }, index) => 
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
                    onClick={() => openLightBox(lightBoxImages.images, index)}
                />
            )}
        </Col>
        {processedImages.length > 0 && <Col sm={6} md={2} xl={3}>
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
