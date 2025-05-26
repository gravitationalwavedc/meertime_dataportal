import { render, screen } from "@testing-library/react";
import { vi } from "vitest";

// Mock the useAuth hook to avoid complex AuthProvider setup
vi.mock("../auth/AuthContext.jsx", () => ({
  useAuth: () => ({
    user: { username: "testuser" },
    isAuthenticated: true,
    loading: false,
    refreshAuth: vi.fn(),
    logout: vi.fn(),
  }),
}));

// Mock the react-relay module
vi.mock("react-relay", () => ({
  commitMutation: vi.fn(),
  graphql: vi.fn(() => "mocked-graphql-query"),
}));

// Import after mocking
import PasswordChange from "./PasswordChange";

describe("password change page", () => {
  beforeEach(() => {
    // Clear all mocks before each test
    vi.clearAllMocks();
  });

  it("should have current, new and confirm new password fields", () => {
    render(<PasswordChange />);

    expect(screen.getByLabelText("Current Password")).toBeInTheDocument();
    expect(screen.getByLabelText("New Password")).toBeInTheDocument();
    expect(screen.getByLabelText("Confirm New Password")).toBeInTheDocument();
  });
});
