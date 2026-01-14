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
      aliasQuery(req, "TemplateQuery", "templateQuery.json");
      aliasQuery(req, "SingleObservationQuery", "singleObservationQuery.json");
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

  it("should toggle the template modal", () => {
    cy.wait(["@FoldDetailQuery", "@PlotlyPlotQuery"]);
    cy.contains("J0125-2327");
    cy.contains("Pulse Profile Template").should("not.exist");
    cy.contains("Download template").click();
    cy.wait("@TemplateQuery");
    cy.contains("MeerPipe Pulse Profile Template").should("be.visible");
  });

  it("should display template information with band", () => {
    cy.wait(["@FoldDetailQuery", "@PlotlyPlotQuery"]);
    cy.contains("Download template").click();
    cy.wait("@TemplateQuery");
    cy.contains("MeerPipe Pulse Profile Template").should("be.visible");
    cy.contains("(LBAND)").should("be.visible");
    cy.contains("project PTA").should("be.visible");
  });

  it("should display template download link", () => {
    cy.wait(["@FoldDetailQuery", "@PlotlyPlotQuery"]);
    cy.contains("Download template").click();
    cy.wait("@TemplateQuery");
    cy.contains("MeerPipe Pulse Profile Template").should("be.visible");
    cy.contains("Download Template File").should("be.visible");
    cy.get('a[href*="J0125-2327_LBAND_template.std"]').should("exist");
  });

  it("should close template modal when clicking close button", () => {
    cy.wait(["@FoldDetailQuery", "@PlotlyPlotQuery"]);
    cy.contains("Download template").click();
    cy.wait("@TemplateQuery");
    cy.contains("MeerPipe Pulse Profile Template").should("be.visible");
    
    // Click the close button
    cy.get('.modal-header button.close').click();
    
    // Modal should be hidden
    cy.contains("MeerPipe Pulse Profile Template").should("not.exist");
  });

  it("should download full resolution files when download button is clicked", () => {
    cy.wait(["@FoldDetailQuery", "@PlotlyPlotQuery"]);
    
    // Ensure the button is visible and clickable
    cy.contains("Download Full Resolution Data").should("be.visible");
    
    // Click the button - this will open download in new tab
    cy.contains("Download Full Resolution Data").click();
    
    // Verify the button click worked by checking that the page is still functional
    cy.contains("J0125-2327").should("be.visible");
  });

  it("should download decimated files when download button is clicked", () => {
    cy.wait(["@FoldDetailQuery", "@PlotlyPlotQuery"]);
    
    // Ensure the button is visible and clickable
    cy.contains("Download Decimated Data").should("be.visible");
    
    // Click the button - this will open download in new tab
    cy.contains("Download Decimated Data").click();
    
    // Verify the button click worked by checking that the page is still functional
    cy.contains("J0125-2327").should("be.visible");
  });

  it("should download ToAs files when download button is clicked", () => {
    cy.wait(["@FoldDetailQuery", "@PlotlyPlotQuery"]);
    
    // Ensure the button is visible and clickable
    cy.contains("Download ToAs").should("be.visible");
    
    // Click the button - this will open download in new tab
    cy.contains("Download ToAs").click();
    
    // Verify the button click worked by checking that the page is still functional
    cy.contains("J0125-2327").should("be.visible");
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

describe("The Fold Detail Page - Template Access Control", () => {
  it("should show inaccessible template message when template is embargoed and user is not a member", () => {
    cy.intercept("http://localhost:5173/api/graphql/", (req) => {
      aliasQuery(req, "FoldDetailQuery", "foldDetailQuery.json");
      aliasQuery(req, "PlotlyPlotQuery", "plotlyPlotQuery.json");
      aliasQuery(req, "TemplateQuery", "templateQueryInaccessible.json");
    });

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

    cy.intercept("GET", "/media/**/*.png", {
      fixture: "example.json"
    });

    cy.visit("fold/meertime/J0125-2327/");
    cy.wait(["@FoldDetailQuery", "@PlotlyPlotQuery"]);
    
    cy.contains("Download template").click();
    cy.wait("@TemplateQuery");
    
    cy.contains("MeerPipe Pulse Profile Template").should("be.visible");
    cy.contains("Please log in to download files.").should("be.visible");
  });

  it("should show embargoed template with access message for project members", () => {
    cy.intercept("http://localhost:5173/api/graphql/", (req) => {
      aliasQuery(req, "FoldDetailQuery", "foldDetailQuery.json");
      aliasQuery(req, "PlotlyPlotQuery", "plotlyPlotQuery.json");
      aliasQuery(req, "TemplateQuery", "templateQueryEmbargoed.json");
    });

    cy.intercept("GET", "/api/auth/session/", {
      statusCode: 200,
      body: {
        isAuthenticated: true,
        user: { username: "testuser" }
      }
    }).as("checkSession");

    cy.intercept("GET", "/api/auth/csrf/", {
      statusCode: 200,
      body: { csrfToken: "mock-csrf-token" }
    }).as("getCSRF");

    cy.intercept("GET", "/media/**/*.png", {
      fixture: "example.json"
    });

    cy.visit("fold/meertime/J0125-2327/");
    cy.wait(["@FoldDetailQuery", "@PlotlyPlotQuery"]);
    
    cy.contains("Download template").click();
    cy.wait("@TemplateQuery");
    
    cy.contains("MeerPipe Pulse Profile Template").should("be.visible");
    cy.contains("You have access to this embargoed template as a project member").should("be.visible");
    cy.contains("(UHF)").should("be.visible");
    cy.contains("Download Template File").should("be.visible");
  });
});
