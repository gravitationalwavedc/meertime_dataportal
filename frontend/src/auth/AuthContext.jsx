import { createContext, useContext, useState, useEffect } from "react";
import {
  checkAuthStatus,
  fetchCSRFToken,
  authenticatedFetch,
} from "./csrfUtils";

// Create the authentication context
const AuthContext = createContext(null);

// Provider component that wraps the app
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Check authentication status on component mount
  useEffect(() => {
    const checkAuth = async () => {
      const authData = await checkAuthStatus();
      if (authData.isAuthenticated) {
        setUser(authData.user);
      } else {
        setUser(null);
      }
      setLoading(false);
    };

    checkAuth();
  }, []);

  // Refresh auth status
  const refreshAuth = async () => {
    setLoading(true);
    const authData = await checkAuthStatus();
    if (authData.isAuthenticated) {
      setUser(authData.user);
    } else {
      setUser(null);
    }
    setLoading(false);
  };

  // Handle logout
  const logout = async () => {
    try {
      // First get CSRF token
      await fetchCSRFToken();

      // Then attempt logout
      const response = await authenticatedFetch("/api/auth/logout/", {
        method: "POST",
      });

      if (response.ok) {
        // Clear user data from state and localStorage
        setUser(null);
        localStorage.removeItem("username");
        localStorage.removeItem("isStaff");

        // Force reload to clear any cached data
        window.location.href = "/";
      } else {
        console.error("Logout failed");
      }
    } catch (error) {
      console.error("Logout error:", error);
    }
  };

  // Context value
  const value = {
    user,
    isAuthenticated: !!user,
    loading,
    refreshAuth,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// Custom hook for using the auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
