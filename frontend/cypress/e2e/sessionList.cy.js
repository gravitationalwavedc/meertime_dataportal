import { aliasQuery } from "../utils/graphql-test-utils";

describe("The Session List Page", () => {
  beforeEach(() => {
    cy.intercept("http://localhost:5173/api/graphql/", (req) => {
      aliasQuery(req, "SessionListTableQuery", "sessionListQuery.json");
      aliasQuery(req, "SessionQuery", "sessionQuery.json");
    });

    // Mock session-based authentication endpoints to prevent leaking requests
    cy.intercept("GET", "/api/auth/session/", {
      statusCode: 200,
      body: {
        isAuthenticated: false,
        user: null
      }
    }).as("checkSession");

    cy.intercept("GET", "/api/auth/csrf/", {
      statusCode: 200,
      body: { csrfToken: "mock-csrf-token" }
    }).as("getCSRF");

    cy.visit("/sessions/");
  });

  it("displays loading then the data", () => {
    cy.contains("Sessions").should("be.visible");

    cy.wait("@SessionListTableQuery");

    cy.contains("Loading...").should("not.exist");
    cy.contains("Start").should("be.visible");
    cy.location("pathname").should("equal", "/sessions/");
  });

  it("check view all button", () => {
    cy.wait("@SessionListTableQuery");
    cy.contains("View all").click();
    cy.location("pathname").should("equal", "/session/64/");

    cy.wait("@SessionQuery");
    cy.contains("JName").should("be.visible");
  });
});
