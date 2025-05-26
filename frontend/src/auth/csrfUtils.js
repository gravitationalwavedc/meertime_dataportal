// CSRF token management for Django's session authentication
// This module handles fetching and storing CSRF tokens for use with API requests

const CSRF_URL = "/api/auth/csrf/";

// Function to get CSRF token from the API
export const fetchCSRFToken = async () => {
  try {
    const response = await fetch(CSRF_URL, {
      credentials: "include", // Include cookies
    });

    if (!response.ok) {
      throw new Error("Failed to fetch CSRF token");
    }

    const data = await response.json();
    return data.csrfToken;
  } catch (error) {
    console.error("Error fetching CSRF token:", error);
    return null;
  }
};

// Helper for making authenticated fetch requests with CSRF token
export const authenticatedFetch = async (url, options = {}) => {
  // Get CSRF token
  const csrfToken = await fetchCSRFToken();

  // Merge headers with CSRF token
  const headers = {
    ...options.headers,
    "X-CSRFToken": csrfToken,
    "Content-Type": "application/json",
  };

  // Return fetch with CSRF and credentials
  return fetch(url, {
    ...options,
    headers,
    credentials: "include",
  });
};

// Helper for checking if user is authenticated
export const checkAuthStatus = async () => {
  try {
    const response = await fetch("/api/auth/session/", {
      credentials: "include",
    });

    if (!response.ok) {
      return { isAuthenticated: false };
    }

    return await response.json();
  } catch (error) {
    console.error("Error checking authentication status:", error);
    return { isAuthenticated: false };
  }
};
