import Image from 'react-bootstrap/Image';
import React from 'react';
import image404 from '../assets/images/image404.png';

const PlotImage = ({ imageData, handleClick }) => {
    if (!imageData) return null;

    return <Image
        rounded
        fluid
        className='mb-3'
        alt={`Plot ${imageData.plotType} using ${imageData.process} data.`}
        src={`${process.env.REACT_APP_MEDIA_URL}${imageData.url}`}
        onError={({ currentTarget }) => {
            currentTarget.onError = null;
            currentTarget.src = image404;
        }}
        onClick={handleClick} />;
};
        

export default PlotImage;