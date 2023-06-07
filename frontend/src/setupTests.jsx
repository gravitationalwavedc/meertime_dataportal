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
    Link: (component) => <div>{component.children}</div>,
  };
});

global.jest = vi;
global.environment = createMockEnvironment();
