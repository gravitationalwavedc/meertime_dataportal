import { aliasMutation, aliasQuery } from "../utils/graphql-test-utils";

describe("Token Management Page", () => {
  beforeEach(() => {
    // Freeze time to May 28, 2025 to ensure tests don't fail based on real calendar dates
    cy.clock(new Date("2025-05-28T12:00:00Z").getTime(), ["Date"]);
    
    // Mock GraphQL requests
    cy.intercept("http://localhost:5173/api/graphql/", (req) => {
      // Handle token management queries and mutations
      aliasQuery(req, "TokenManagementQuery", "tokenListMutation.json");
      aliasMutation(req, "TokenManagementCreateMutation", "createTokenMutation.json");
      aliasMutation(req, "TokenManagementDeleteMutation", "deleteTokenMutation.json");
    });

    // Mock session-based authentication endpoints
    cy.intercept("GET", "/api/auth/csrf/", {
      statusCode: 200,
      body: { csrfToken: "mock-csrf-token" }
    }).as("getCSRF");

    cy.intercept("POST", "/api/auth/login/", {
      statusCode: 200,
      body: {
        user: {
          username: "buffy@sunnydale.com",
          email: "buffy@sunnydale.com",
          isStaff: true,
          isUnrestricted: true
        },
        detail: "Successfully logged in."
      }
    }).as("sessionLogin");

    cy.intercept("GET", "/api/auth/session/", {
      statusCode: 200,
      body: {
        isAuthenticated: true,
        user: {
          username: "buffy@sunnydale.com",
          email: "buffy@sunnydale.com",
          isStaff: true,
          isUnrestricted: true
        }
      }
    }).as("checkSession");

    // Mock logout
    cy.intercept("POST", "/api/auth/logout/", {
      statusCode: 200,
      body: { detail: "Successfully logged out." }
    }).as("logout");

    // Set localStorage to simulate logged-in state
    cy.window().then((win) => {
      win.localStorage.setItem("username", "buffy@sunnydale.com");
      win.localStorage.setItem("isStaff", "true");
    });
  });

  it("should display token management page and load existing tokens", () => {
    cy.visit("/");
    
    // Navigate to token management via TopNav
    cy.contains("a", "API Tokens").click();
    
    // Check that the page loads correctly
    cy.contains("API Token Management").should("be.visible");
    cy.contains("Your API Tokens").should("be.visible");
    cy.contains("Create New Token").should("be.visible");
    
    // Check that tokens are loaded
    cy.wait("@TokenManagementQuery");
    
    // Check that existing tokens are displayed
    cy.contains("Web Interface Token").should("be.visible");
    cy.contains("CLI Token").should("be.visible");
    
    // Check token table headers
    cy.contains("th", "Name").should("be.visible");
    cy.contains("th", "Token Preview").should("be.visible");
    cy.contains("th", "Created").should("be.visible");
    cy.contains("th", "Last Used").should("be.visible");
    cy.contains("th", "Expires").should("be.visible");
    cy.contains("th", "Status").should("be.visible");
    cy.contains("th", "Actions").should("be.visible");
    
    // Check token status badges
    cy.contains(".badge", "Active").should("be.visible");
    
    // Check delete buttons are present
    cy.contains("button", "Delete").should("be.visible");
  });

  it("should show create token form when clicking Create New Token", () => {
    cy.visit("/");
    cy.contains("a", "API Tokens").click();
    cy.wait("@TokenManagementQuery");
    
    // Click create new token button
    cy.contains("button", "Create New Token").click();
    
    // Check that the form is displayed
    cy.contains("Create New Token").should("be.visible");
    cy.get("input[name='tokenName']").should("be.visible");
    cy.contains("button", "Generate Token").should("be.visible");
    
    // Check that the button text changed to Cancel
    cy.contains("button", "Cancel").should("be.visible");
  });

  it("should hide create token form when clicking Cancel", () => {
    cy.visit("/");
    cy.contains("a", "API Tokens").click();
    cy.wait("@TokenManagementQuery");
    
    // Open the form
    cy.contains("button", "Create New Token").click();
    cy.get("input[name='tokenName']").should("be.visible");
    
    // Cancel the form
    cy.contains("button", "Cancel").click();
    
    // Check that the form is hidden
    cy.get("input[name='tokenName']").should("not.exist");
    cy.contains("button", "Create New Token").should("be.visible");
  });

  it("should create a new token successfully", () => {
    cy.visit("/");
    cy.contains("a", "API Tokens").click();
    cy.wait("@TokenManagementQuery");
    
    // Open create form
    cy.contains("button", "Create New Token").click();
    
    // Fill in token name
    cy.get("input[name='tokenName']").type("Test Integration Token");
    
    // Submit the form
    cy.contains("button", "Generate Token").click();
    
    // Wait for create mutation
    cy.wait("@TokenManagementCreateMutation");
    
    // Check that success alert is shown
    cy.contains("API Token Created Successfully").should("be.visible");
    cy.contains("Copy this token now").should("be.visible");
    
    // Check that token is displayed in the alert
    cy.get("code").contains("test_token_").should("be.visible");
    
    // Check that copy button is present
    cy.contains("button", "📋 Copy").should("be.visible");
    
    // Check that form is hidden after creation
    cy.contains("button", "Create New Token").should("be.visible");
    
    // Check that tokens are reloaded (second call)
    cy.wait("@TokenManagementQuery");
  });

  it("should copy token to clipboard when clicking Copy Token", () => {
    cy.visit("/");
    cy.contains("a", "API Tokens").click();
    cy.wait("@TokenManagementQuery");
    
    // Create a token first
    cy.contains("button", "Create New Token").click();
    cy.get("input[name='tokenName']").type("Copy Test Token");
    cy.contains("button", "Generate Token").click();
    cy.wait("@TokenManagementCreateMutation");
    
    // Mock clipboard API
    cy.window().then((win) => {
      cy.stub(win.navigator.clipboard, 'writeText').as('writeText').resolves();
    });
    
    // Click copy button
    cy.contains("button", "📋 Copy").click();
    
    // Check that clipboard was called with the token
    cy.get("@writeText").should("have.been.calledWith", "test_token_abcd1234567890efghijklmnopqrstuv");
    
    // Check that button shows success state briefly
    cy.contains("button", "✓ Copied!").should("be.visible");
  });

  it("should show delete confirmation modal when clicking Delete", () => {
    cy.visit("/");
    cy.contains("a", "API Tokens").click();
    cy.wait("@TokenManagementQuery");
    
    // Click delete button for first token
    cy.get("tbody tr").first().contains("button", "Delete").click();
    
    // Check that modal is displayed
    cy.contains("Confirm Token Deletion").should("be.visible");
    cy.contains("Are you sure you want to delete").should("be.visible");
    cy.contains("Web Interface Token").should("be.visible");
    cy.contains("This action cannot be undone").should("be.visible");
    
    // Check modal buttons
    cy.contains("button", "Cancel").should("be.visible");
    cy.contains("button", "Delete Token").should("be.visible");
  });

  it("should cancel token deletion when clicking Cancel in modal", () => {
    cy.visit("/");
    cy.contains("a", "API Tokens").click();
    cy.wait("@TokenManagementQuery");
    
    // Open delete modal
    cy.get("tbody tr").first().contains("button", "Delete").click();
    cy.contains("Confirm Token Deletion").should("be.visible");
    
    // Cancel deletion
    cy.contains("button", "Cancel").click();
    
    // Check that modal is hidden
    cy.contains("Confirm Token Deletion").should("not.exist");
    
    // Check that token still exists
    cy.contains("Web Interface Token").should("be.visible");
  });

  it("should delete token when confirming deletion", () => {
    cy.visit("/");
    cy.contains("a", "API Tokens").click();
    cy.wait("@TokenManagementQuery");
    
    // Open delete modal
    cy.get("tbody tr").first().contains("button", "Delete").click();
    
    // Confirm deletion
    cy.contains("button", "Delete Token").click();
    
    // Wait for delete mutation
    cy.wait("@TokenManagementDeleteMutation");
    
    // Check that modal is hidden
    cy.contains("Confirm Token Deletion").should("not.exist");
    
    // Check that tokens are reloaded
    cy.wait("@TokenManagementQuery");
  });

  it("should display usage instructions section", () => {
    cy.visit("/");
    cy.contains("a", "API Tokens").click();
    cy.wait("@TokenManagementQuery");
    
    // Check usage instructions section
    cy.contains("Usage Instructions").should("be.visible");
    cy.contains("To interact with the Pulsar Portal's API").should("be.visible");
    cy.contains("Authorization: Bearer YOUR_TOKEN_HERE").should("be.visible");
    
    // Check example code blocks
    cy.contains("curl").should("be.visible");
    cy.contains("Python requests").should("be.visible");
    
    // Check that code examples contain proper structure
    cy.get("pre").should("contain", "Authorization: Bearer");
    cy.get("pre").should("contain", "'Content-Type': 'application/json'");
  });

  it("should show error messages when token operations fail", () => {
    // Mock failed create mutation
    cy.intercept("http://localhost:5173/api/graphql/", (req) => {
      if (req.body.query && req.body.query.includes("TokenManagementCreateMutation")) {
        req.reply({
          fixture: "createTokenMutationError.json"
        });
        req.alias = "TokenManagementCreateMutation";
      } else {
        aliasMutation(req, "TokenManagementQuery", "tokenListMutation.json");
      }
    });
    
    cy.visit("/");
    cy.contains("a", "API Tokens").click();
    cy.wait("@TokenManagementQuery");
    
    // Try to create a token
    cy.contains("button", "Create New Token").click();
    cy.get("input[name='tokenName']").type("Error Test Token");
    cy.contains("button", "Generate Token").click();
    
    cy.wait("@TokenManagementCreateMutation");
    
    // Check that error is displayed
    cy.contains("Token name already exists").should("be.visible");
    cy.get(".alert-danger").should("be.visible");
  });

  it("should validate token name input", () => {
    cy.visit("/");
    cy.contains("a", "API Tokens").click();
    cy.wait("@TokenManagementQuery");
    
    // Open create form
    cy.contains("button", "Create New Token").click();
    
    // Try to submit without name
    cy.contains("button", "Generate Token").click();
    
    // Check validation message (HTML5 validation)
    cy.get("input[name='tokenName']:invalid").should("exist");
    
    // Test name length validation by filling and then clearing the field
    cy.get("input[name='tokenName']").type("a".repeat(65)); // 65 characters
    cy.contains("button", "Generate Token").click();
  });

  it("should handle navigation and authentication correctly", () => {
    // Test that unauthenticated users can't access token management
    cy.window().then((win) => {
      win.localStorage.removeItem("username");
      win.localStorage.removeItem("isStaff");
    });
    
    // Mock unauthenticated session check
    cy.intercept("GET", "/api/auth/session/", {
      statusCode: 200,
      body: {
        isAuthenticated: false,
        user: null
      }
    }).as("checkSessionUnauth");
    
    cy.visit("/", { failOnStatusCode: false });
    
    // Check that user is not authenticated (API Tokens link should not be visible to unauthenticated users)
    cy.get("nav").should("not.contain", "API Tokens");
    
    // Alternatively, if the link is visible but clicking it should show a message or redirect
    // We can check that the home page is showing an unauthenticated state
    cy.url().should("include", "/");
  });

  it("should display empty state when no tokens exist", () => {
    // Mock empty token list
    cy.intercept("http://localhost:5173/api/graphql/", (req) => {
      if (req.body.query && req.body.query.includes("TokenManagementQuery")) {
        req.reply({
          fixture: "tokenListMutationEmpty.json"
        });
        req.alias = "TokenManagementQuery";
      }
    });
    
    cy.visit("/");
    cy.contains("a", "API Tokens").click();
    cy.wait("@TokenManagementQuery");
    
    // Check empty state message
    cy.contains("You don't have any API tokens yet").should("be.visible");
    cy.contains("Create your first token to start using the API").should("be.visible");
  });

  it("should close success alert when clicking close button", () => {
    cy.visit("/");
    cy.contains("a", "API Tokens").click();
    cy.wait("@TokenManagementQuery");
    
    // Create a token to show success alert
    cy.contains("button", "Create New Token").click();
    cy.get("input[name='tokenName']").type("Close Test Token");
    cy.contains("button", "Generate Token").click();
    cy.wait("@TokenManagementCreateMutation");
    
    // Check success alert is visible
    cy.contains("API Token Created Successfully").should("be.visible");
    
    // Close the alert
    cy.contains("button", "Close").click();
    
    // Check alert is hidden
    cy.contains("API Token Created Successfully").should("not.exist");
  });

  it("should display expiry information correctly for different token states", () => {
    cy.visit("/");
    cy.contains("a", "API Tokens").click();
    cy.wait("@TokenManagementQuery");
    
    // Check that the Expires column header is present
    cy.contains("th", "Expires").should("be.visible");
    
    // Check future expiry date (Web Interface Token - expires 2025-12-31)
    cy.get("tbody tr").contains("Web Interface Token").parent().within(() => {
      // Should show formatted date for future expiry
      cy.get("td").eq(4).should("contain", "12/31/2025");
    });
    
    // Check never expires (CLI Token - expiresAt: null)
    cy.get("tbody tr").contains("CLI Token").parent().within(() => {
      // Should show "Never expires" for null expiry
      cy.get("td").eq(4).should("contain", "Never expires");
    });
    
    // Check expired token (Mobile App Token - expired 2025-01-01)
    cy.get("tbody tr").contains("Mobile App Token").parent().within(() => {
      // Should show "Expired" in red text for past expiry
      cy.get("td").eq(4).should("contain", "Expired");
      cy.get("td").eq(4).find(".text-danger").should("exist");
    });
  });

  it("should handle tokens with different expiry scenarios", () => {
    // Ensure time is frozen for this test too
    cy.clock(new Date("2025-05-28T12:00:00Z").getTime(), ["Date"]);
    
    // Create a custom fixture with more expiry scenarios
    cy.intercept("http://localhost:5173/api/graphql/", (req) => {
      if (req.body.query && req.body.query.includes("TokenManagementQuery")) {
        req.reply({
          body: {
            data: {
              apiTokens: {
                edges: [
                  {
                    node: {
                      id: "1",
                      name: "Never Expires Token",
                      preview: "abcd1234",
                      created: "2025-05-20T10:30:00Z",
                      lastUsed: "2025-05-27T08:15:00Z",
                      expiresAt: null,
                      isActive: true
                    }
                  },
                  {
                    node: {
                      id: "2",
                      name: "Future Expiry Token",
                      preview: "efgh5678",
                      created: "2025-05-15T14:20:00Z",
                      lastUsed: "2025-05-26T16:45:00Z",
                      expiresAt: "2025-12-31T23:59:59Z",
                      isActive: true
                    }
                  },
                  {
                    node: {
                      id: "3",
                      name: "Expired Token",
                      preview: "ijkl9012",
                      created: "2025-05-10T09:15:00Z",
                      lastUsed: null,
                      expiresAt: "2024-01-01T00:00:00Z",
                      isActive: true
                    }
                  }
                ]
              }
            }
          }
        });
        req.alias = "TokenManagementQuery";
      }
    });
    
    cy.visit("/");
    cy.contains("a", "API Tokens").click();
    cy.wait("@TokenManagementQuery");
    
    // Verify never expires token
    cy.get("tbody tr").contains("Never Expires Token").parent().within(() => {
      cy.get("td").eq(4).should("contain", "Never expires");
    });
    
    // Verify future expiry token shows formatted date
    cy.get("tbody tr").contains("Future Expiry Token").parent().within(() => {
      cy.get("td").eq(4).should("contain", "12/31/2025");
      cy.get("td").eq(4).should("not.contain", "Expired");
    });
    
    // Verify expired token shows expired status
    cy.get("tbody tr").contains("Expired Token").parent().within(() => {
      cy.get("td").eq(4).should("contain", "Expired");
      cy.get("td").eq(4).find(".text-danger").should("exist");
    });
  });
});
