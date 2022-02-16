import { Col, Image } from 'react-bootstrap';
import React from 'react';
import image404 from '../assets/images/image404.png';

const ImageGrid = ({ images }) => {
    const rawImages = images.edges.filter(
        ({ node }) => node.process.toLowerCase() === 'raw' && node.resolution === 'hi'
    );

    const processedImages = images.edges.filter(
        ({ node }) => node.process.toLowerCase() !== 'raw' 
    );

    const sizes = processedImages.length > 0 ? { sm:6, md:2, xl:3 } : { sm:12, md:4, xl:6 };

    return <React.Fragment>
        <Col {...sizes}>
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
    </React.Fragment>;
};

export default ImageGrid;
