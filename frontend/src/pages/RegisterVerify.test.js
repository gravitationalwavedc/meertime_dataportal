import RegisterVerify from './RegisterVerify';
import React from 'react';
import { render } from '@testing-library/react';

/* eslint-disable react/display-name */

jest.mock('found', () => ({
    Link: component => <div>{component.children}</div>,
    useRouter: () => ({
        router: {
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
        }
    })
}));

describe('register verify component', () => {

    it('should display the status verifying while waiting for data', () => {
        expect.hasAssertions();
        const { getByText } = render(<RegisterVerify match={{ params: { code: 'code' } }}/>);
        expect(getByText('Register')).toBeInTheDocument();
        expect(getByText('Email verification in progress')).toBeInTheDocument();
    });
});
