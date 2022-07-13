import { fireEvent, render, waitFor } from '@testing-library/react';

import PasswordReset from './PasswordReset';
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

describe('password reset page', () => {
    it('should have code, password and confirm password fields', () => {
        expect.hasAssertions();
        const { getByLabelText } = render(<PasswordReset router={{}} match={{}}/>);
        expect(getByLabelText('Verification Code (Sent to your email)')).toBeInTheDocument();
        expect(getByLabelText('New Password')).toBeInTheDocument();
        expect(getByLabelText('Confirm New Password')).toBeInTheDocument();
    });
});
