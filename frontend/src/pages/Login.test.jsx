import { render, waitFor, screen, act } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useRouter } from "found";
import { vi } from "vitest";

// Create mock functions using vi.hoisted to ensure they're available during hoisting
const { mockFetchCSRFToken, mockAuthenticatedFetch, mockCheckAuthStatus } =
  vi.hoisted(() => ({
    mockFetchCSRFToken: vi.fn().mockResolvedValue("mock-csrf-token"),
    mockAuthenticatedFetch: vi.fn(),
    mockCheckAuthStatus: vi.fn().mockResolvedValue({
      isAuthenticated: false,
      user: null,
    }),
  }));

// Mock the global fetch function to prevent any real network calls
global.fetch = vi.fn().mockResolvedValue({
  ok: true,
  json: vi.fn().mockResolvedValue({ csrfToken: "mock-csrf-token" }),
});

// Mock the csrfUtils module - this must be done before importing Login
vi.mock("../auth/csrfUtils", () => ({
  fetchCSRFToken: mockFetchCSRFToken,
  authenticatedFetch: mockAuthenticatedFetch,
  checkAuthStatus: mockCheckAuthStatus,
}));

// Import after mocking
import Login from "./Login";
import { AuthProvider } from "../auth/AuthContext";

// Helper function to render Login with AuthProvider and wait for auth initialization
const renderLoginWithProvider = async (props) => {
  let component;
  await act(async () => {
    component = render(
      <AuthProvider>
        <Login {...props} />
      </AuthProvider>
    );
    // Wait for AuthProvider's useEffect to complete
    await waitFor(() => {
      // The AuthProvider calls checkAuthStatus which resolves immediately in tests
      // This ensures the initial auth check is complete
    });
  });
  return component;
};

describe("login page", () => {
  beforeEach(() => {
    // Clear all mocks before each test
    vi.clearAllMocks();
  });

  it("should have a email and password field", async () => {
    expect.hasAssertions();
    const { getByLabelText } = await renderLoginWithProvider({
      router: {},
      match: {},
    });
    expect(getByLabelText("Email")).toBeInTheDocument();
    expect(getByLabelText("Password")).toBeInTheDocument();
  });

  it("should display errors from the server", async () => {
    expect.hasAssertions();
    const { router } = useRouter();
    const user = userEvent.setup();

    // Mock authenticatedFetch to return a failed response
    mockAuthenticatedFetch.mockResolvedValueOnce({
      ok: false,
      json: async () => ({
        detail: "Please enter valid credentials.",
      }),
    });

    await renderLoginWithProvider({
      router,
      match: { location: { query: {} } },
    });

    const emailField = screen.getByLabelText("Email");
    const passwordField = screen.getByLabelText("Password");

    await user.type(emailField, "asher@example.com");
    await user.type(passwordField, "password");

    await user.click(screen.getByRole("button", { name: "Sign in" }));

    await waitFor(() =>
      expect(
        screen.getByText("Please enter valid credentials.")
      ).toBeInTheDocument()
    );
  });
});
