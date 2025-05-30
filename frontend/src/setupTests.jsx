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

vi.mock("found", async () => {
  const actual = await vi.importActual("found");
  return {
    ...actual,
    createHref: vi.fn(),
    useRouter: () => ({
      router: {
        push: vi.fn(),
        replace: vi.fn(),
        go: vi.fn(),
        createHref: vi.fn(),
        createLocation: vi.fn(),
        isActive: vi.fn(),
        matcher: {
          match: vi.fn(),
          getRoutes: vi.fn(),
          isActive: vi.fn(),
          format: vi.fn(),
        },
        addTransitionHook: vi.fn(),
      },
    }),
    useLocation: () => ({
      pathname: "/",
    }),
    Link: ({ children, to, as: Component = "a", exact, ...props }) => {
      // Filter out router-specific props that shouldn't be passed to DOM elements
      const { exact: _, ...filteredProps } = props;

      if (Component && typeof Component !== "string") {
        // For React Bootstrap components, pass through props but filter out router-specific ones
        return (
          <Component href={to} {...filteredProps}>
            {children}
          </Component>
        );
      }
      return (
        <a href={to} {...filteredProps}>
          {children}
        </a>
      );
    },
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
