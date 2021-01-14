import { fireEvent, render } from '@testing-library/react';

import React from 'react';
import TopNav from './TopNav';

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

describe('top navigation bar', () => {

    it('should clear the session token on logout', () => {
        expect.hasAssertions();
        const { getByText } = render(<TopNav />);
        const logoutButton = getByText('Log out');
        fireEvent.click(logoutButton);
        expect(sessionStorage.clear).toHaveBeenCalledTimes(1);
        expect(sessionStorage).toHaveLength(0); 
    });

});
