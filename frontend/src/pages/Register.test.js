import { fireEvent, render, waitFor } from '@testing-library/react';

import Register from './Register';
import { MockPayloadGenerator } from 'relay-test-utils';
import React from 'react';
import environment from '../relayEnvironment';

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

describe('register page', () => {
    it('should have first name, last name, email, password and confirm password fields', () => {
        expect.hasAssertions();
        const { getByLabelText } = render(<Register router={{}} match={{}}/>);
        expect(getByLabelText('First Name')).toBeInTheDocument();
        expect(getByLabelText('Last Name')).toBeInTheDocument();
        expect(getByLabelText('Email')).toBeInTheDocument();
        expect(getByLabelText('Password')).toBeInTheDocument();
        expect(getByLabelText('Confirm Password')).toBeInTheDocument();
    });
});
