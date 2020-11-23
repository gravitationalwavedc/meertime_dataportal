import App from './App';
import React from 'react';
import { render } from '@testing-library/react';

describe('the app', () => {
    it('should render the App', () => {
        expect.hasAssertions();
        const { getByTestId } = render(<App />);
        expect(getByTestId('mainApp')).toBeInTheDocument();
    });
});
