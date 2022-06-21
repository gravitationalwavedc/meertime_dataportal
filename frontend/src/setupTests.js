import 'regenerator-runtime/runtime';
import '@testing-library/jest-dom/extend-expect';
import React from 'react';

// jest-dom adds custom jest matchers for asserting on DOM nodes.
// allows you to do things like:
// expect(element).toHaveTextContent(/react/i)
// learn more: https://github.com/testing-library/jest-dom

// JSDOM hasn't implemented matchMedia yet so we need to mock it. 
// This is the official workaround mock from 
// https://jestjs.io/docs/manual-mocks#mocking-methods-which-are-not-implemented-in-jsdom
Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: jest.fn().mockImplementation(query => ({
        matches: false,
        media: query,
        onchange: null,
        addListener: jest.fn(), // deprecated
        removeListener: jest.fn(), // deprecated
        addEventListener: jest.fn(),
        removeEventListener: jest.fn(),
        dispatchEvent: jest.fn(),
    })),
});

global.mockRouter = {
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

// Jest doesn't support ESM yet apparently, which ReactMarkdown relies on. We don't actually care about testing 
// the markdown render so mocking it works for now.
jest.mock('react-markdown', () => {
    const ReactMarkdown = ({ children }) => <>{children}</>;
    return ReactMarkdown;
});
