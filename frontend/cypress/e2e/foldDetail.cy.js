import { aliasQuery } from "../utils/graphql-test-utils";

describe("The Fold Detail Page", () => {
  beforeEach(() => {
    cy.intercept("http://localhost:5173/api/graphql/", (req) => {
      aliasQuery(req, "FoldDetailQuery", "foldDetailQuery.json");
      aliasQuery(req, "PlotlyPlotQuery", "plotlyPlotQuery.json");
      aliasQuery(
        req,
        "FoldDetailFileDownloadQuery",
        "foldDetailFileDownloadQuery.json"
      );
      aliasQuery(req, "EphemerisQuery", "ephemerisQuery.json");
      aliasQuery(req, "SingleObservationQuery", "singleObservationQuery.json");
      aliasQuery(
        req,
        "SingleObservationFileDownloadQuery",
        "singleObservationFileDownloadQuery.json"
      );
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

    // Mock image requests to prevent network calls
    cy.intercept("GET", "/media/**/*.png", {
      fixture: "example.json"
    }).as("plotImages");

    cy.intercept("GET", "/media/**/*.jpg", {
      fixture: "example.json"
    }).as("plotImagesJpg");

    cy.visit("fold/meertime/J0125-2327/");
  });

  it("should toggle the ephemeris modal", () => {
    cy.wait(["@FoldDetailQuery", "@PlotlyPlotQuery"]);
    cy.contains("J0125-2327");
    cy.contains("Folding Ephemeris").should("not.exist");
    cy.contains("View folding ephemeris").click();
    cy.wait("@EphemerisQuery");
    cy.contains("Folding Ephemeris").should("be.visible");
  });

  it("should go to single observation when view button is clicked", () => {
    cy.wait(["@FoldDetailQuery", "@PlotlyPlotQuery"]);
    const observationTimestamp = "2023-12-13-16:07:10";
    cy.contains("table tr", observationTimestamp).as("targetRow");
    cy.get("@targetRow").contains("View").click({ force: true });
    cy.location("pathname").should(
      "equal",
      `/meertime/J0125-2327/${observationTimestamp}/1/`
    );

    cy.wait("@SingleObservationQuery");

    cy.contains("Loading...").should("not.exist");
    cy.contains(observationTimestamp).should("be.visible");
  });

  it("should go to sessions table when view session button is clicked", () => {
    cy.wait(["@FoldDetailQuery", "@PlotlyPlotQuery"]);
    cy.contains("View session").click({ force: true });
    cy.location("pathname").should("equal", "/session/28/");

    cy.wait("@SessionQuery");
    cy.contains("Loading...").should("not.exist");
    cy.contains("JName").should("be.visible");
  });
});
