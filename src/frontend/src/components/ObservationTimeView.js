import MainLayout from './MainLayout';
import React from 'react';

const ObservationTimeView = ({ data }) => {
    console.log(data);
    const title = `${data.relayObservationModel.jname}`;  
    return (
        <MainLayout title={title}>
            <p>Things</p>
        </MainLayout>
    );
};

export default ObservationTimeView;
