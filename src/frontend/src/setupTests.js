// jest-dom adds custom jest matchers for asserting on DOM nodes.
// allows you to do things like:
// expect(element).toHaveTextContent(/react/i)
// learn more: https://github.com/testing-library/jest-dom
import 'regenerator-runtime/runtime';
import '@testing-library/jest-dom/extend-expect';

global.router = {
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
};

jest.mock('./relayEnvironment', () => {
    const { createMockEnvironment } = require('relay-test-utils');
    return createMockEnvironment();
});
