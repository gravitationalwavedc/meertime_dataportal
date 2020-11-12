import React from 'react';
import { render } from '@testing-library/react';
import Fold from './Fold';

/* eslint-disable react/display-name */

jest.mock('found', () => ({
    Link: component => <div>{component.children}</div>,
    useRouter: () => ({ router: {
        push: jest.fn(),
        replace: jest.fn(),
        go: jest.fn(),
        createHref: jest.fn(),
        createLocation: jest.fn(),
        isActive: jest.fn(),
        matcher: {
            match: jest.fn(),
            getRoutes: jest.fn(),
            isActive: jest.fn(),
            format: jest.fn()
        },
        addTransitionHook: jest.fn()
    } }) 
}));

describe('fold component', () => {

    it('should display a loading message while waiting for data', () => {
        expect.hasAssertions();
        const { getByText } = render(<Fold />);
        expect(getByText('Fold Observations')).toBeInTheDocument();
        expect(getByText('Loading...')).toBeInTheDocument();
    });
});
