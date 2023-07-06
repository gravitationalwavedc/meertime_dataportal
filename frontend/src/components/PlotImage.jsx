import Image from "react-bootstrap/Image";
import image404 from "../assets/images/image404.png";
import { useEffect, useState } from 'react';

const PlotImage = ({ imageData, handleClick }) => {

    const token = localStorage.jwt;
    const [image, setImage] = useState('');
    const imageUrl = import.meta.env.VITE_DJANGO_MEDIA_URL + imageData.url;

    useEffect(() => {
        if (!imageData) {
            return <Image
                rounded
                fluid
                className="mb-3"
                alt={`Plot ${imageData.plotType} using ${imageData.process} data.`}
                src={image404}
                onError={({ currentTarget }) => {
                    currentTarget.onError = null;
                    currentTarget.src = image404;
                }}
                onClick={handleClick}
            />
        } else {
            fetch(imageUrl, {
                headers: {
                    'Authorization': 'Bearer ' + token,
                },
            }).then(function (response) {
                return response.text();
            }).then((response) => {
                setImage(response);
            }).catch((error) => {
                // eslint-disable-next-line no-console
                console.log(error);
            });
        }
    });

    return (
        <Image
            rounded
            fluid
            className="mb-3"
            alt={`Plot ${imageData.plotType} using ${imageData.process} data.`}
            // src={`${import.meta.env.VITE_DJANGO_MEDIA_URL}${imageData.url}`}
            src={`data:image;base64,${image}`}
            onError={({ currentTarget }) => {
                currentTarget.onError = null;
                currentTarget.src = image404;
            }}
            onClick={handleClick}
        />
    );
};

export default PlotImage;
