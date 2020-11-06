import React from 'react';
import { render } from '@testing-library/react';
import Fold from './Fold';


describe('fold component', () => {
    it('should display a loading message while waiting for data', () => {
        expect.hasAssertions();
        const { getByText } = render(<Fold />);
        expect(getByText('Fold Observations')).toBeInTheDocument();
        expect(getByText('Loading...')).toBeInTheDocument();
    });
});
