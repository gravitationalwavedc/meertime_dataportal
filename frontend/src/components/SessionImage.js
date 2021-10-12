import { Image } from 'react-bootstrap';
import React from 'react';
import image404 from '../assets/images/image404.png';

const SessionImage = ({ imageHi, imageLo, images, imageIndex, openLightBox }) => {
    if(imageHi) { 
        const thumbnail = `${process.env.REACT_APP_MEDIA_URL}${imageLo ? imageLo : imageHi}`;
        return <Image 
            rounded 
            onClick={() => openLightBox(images, imageIndex)} 
            fluid 
            src={thumbnail}/>;
    }
         
    return  <Image rounded fluid src={image404}/>;
};

export default SessionImage;
