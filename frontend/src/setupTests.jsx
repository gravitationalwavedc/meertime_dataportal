import { expect, afterEach, vi } from "vitest";
import { cleanup } from "@testing-library/react";
import { createMockEnvironment } from "relay-test-utils";
import matchers from "@testing-library/jest-dom/matchers";

// extends Vitest's expect method with methods from react-testing-library
expect.extend(matchers);

// runs a cleanup after each test case (e.g. clearing jsdom)
afterEach(() => {
  cleanup();
});

vi.mock("found/link", () => {
  return {
    default: (component) => <>{component.children}</>,
  };
});

vi.mock("found", () => {
  const actual = vi.importActual("found");
  return {
    ...actual,
    createHref: vi.fn(),
    useRouter: () => ({
      router: () => ({
        createHref: vi.fn(),
      }),
    }),
    Link: (component) => <>{component.children}</>,
  };
});

// This must come before createMockEnvironment because we're switching out jest for vitest
// in the relay-test-utils package.
global.jest = vi;

const mockEnvironment = createMockEnvironment();
global.environment = mockEnvironment;

vi.mock("./relayEnvironment.js", () => {
  return {
    default: mockEnvironment,
  };
});
