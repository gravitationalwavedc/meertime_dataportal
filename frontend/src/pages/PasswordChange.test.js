import { fireEvent, render, waitFor } from '@testing-library/react';

import PasswordChange from './PasswordChange';
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

describe('password change page', () => {
    it('should have current, new and confirm new password fields', () => {
        expect.hasAssertions();
        const { getByLabelText } = render(<PasswordChange router={{}} match={{}}/>);
        expect(getByLabelText('Current Password')).toBeInTheDocument();
        expect(getByLabelText('New Password')).toBeInTheDocument();
        expect(getByLabelText('Confirm New Password')).toBeInTheDocument();
    });
});
