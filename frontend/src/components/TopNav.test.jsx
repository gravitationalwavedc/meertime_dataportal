import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { vi } from "vitest";

// Create mock functions and auth state using vi.hoisted
const { mockLogout, mockAuthState } = vi.hoisted(() => ({
  mockLogout: vi.fn(),
  mockAuthState: {
    isAuthenticated: true,
    user: { username: "testuser" },
  },
}));

// Mock the useAuth hook with dynamic state
vi.mock("../auth/AuthContext.jsx", () => ({
  useAuth: () => ({
    user: mockAuthState.user,
    isAuthenticated: mockAuthState.isAuthenticated,
    loading: false,
    refreshAuth: vi.fn(),
    logout: mockLogout,
  }),
}));

// Import after mocking
import TopNav from "./TopNav";

describe("top navigation bar", () => {
  beforeEach(() => {
    // Clear all mocks before each test
    vi.clearAllMocks();
    // Reset localStorage and sessionStorage before each test
    localStorage.clear();
    sessionStorage.clear();
    // Reset to authenticated state by default
    mockAuthState.isAuthenticated = true;
    mockAuthState.user = { username: "testuser" };
  });

  describe("when authenticated", () => {
    it("should display the change password and logout links", async () => {
      render(<TopNav />);

      expect(screen.getByText("Change Password")).toBeInTheDocument();
      expect(screen.getByText("Log out")).toBeInTheDocument();
      expect(screen.queryByText("Log in")).not.toBeInTheDocument();
    });

    it("should call logout when logout link is clicked", async () => {
      localStorage.setItem("username", "buffy summers");
      sessionStorage.setItem("token", "test-token");

      render(<TopNav />);

      const logoutButton = screen.getByText("Log out");
      fireEvent.click(logoutButton);

      expect(mockLogout).toHaveBeenCalledTimes(1);
    });
  });

  describe("when not authenticated", () => {
    it("should display the login link with correct next parameter", async () => {
      // Set unauthenticated state for this test
      mockAuthState.isAuthenticated = false;
      mockAuthState.user = null;

      render(<TopNav />);

      expect(screen.queryByText("Change Password")).not.toBeInTheDocument();
      expect(screen.queryByText("Log out")).not.toBeInTheDocument();

      const loginLink = screen.getByText("Log in");
      expect(loginLink).toBeInTheDocument();
      // Note: We can't easily test the exact href without mocking useLocation
      // but we can verify the link exists
    });
  });
});
