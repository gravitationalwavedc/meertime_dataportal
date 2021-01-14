import React from 'react';
import SearchmodeDetail from './SearchmodeDetail';
import { render } from '@testing-library/react';

/* global mockRouter */
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

describe('searchmode detail component', () => {

    it('should render with the correct title', () => {
        expect.hasAssertions();
        const { getByText } = render(
            <SearchmodeDetail match={{ params: { jname: 'J111-222', project: 'meertime' } }} router={ mockRouter }/>
        );
        expect(getByText('J111-222')).toBeInTheDocument();
    });

});
