import React from 'react';
import { render } from '@testing-library/react';
import Fold from './Fold';


describe('fold component', () => {
    it('renders Fold', () => {
        expect.hasAssertions();
        const { getByText } = render(<Fold />);
        expect(getByText('Fold Observations')).toBeInTheDocument();
    });
});
