import { aliasQuery } from "../utils/graphql-test-utils";

describe("Single Observation Page", () => {
  beforeEach(() => {
    cy.intercept("http://localhost:5173/api/graphql/", (req) => {
      // Handle all possible GraphQL queries that might be made
      aliasQuery(req, "SingleObservationQuery", "singleObservationQuery.json");
      // Handle any other queries that might be made during navigation
      aliasQuery(req, "FoldQuery", "foldQuery.json");
      aliasQuery(req, "SessionQuery", "sessionQuery.json");
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

    // Mock image requests to prevent network calls
    cy.intercept("GET", "/media/**/*.png", {
      fixture: "example.json" // Using a small fixture file as placeholder
    }).as("plotImages");

    cy.intercept("GET", "/media/**/*.jpg", {
      fixture: "example.json"
    }).as("plotImagesJpg");

    // Mock any other session check requests
    cy.intercept("POST", "/api/auth/logout/", {
      statusCode: 200,
      body: { detail: "Successfully logged out." }
    }).as("logout");

    cy.visit("/meertime/J0125-2327/2023-04-29-06:47:34/2/");
  });

  it("displays loading then the data", () => {
    cy.contains("J0125-2327").should("be.visible");
    cy.wait("@SingleObservationQuery");

    cy.contains("Loading...").should("not.exist");
    cy.contains("Raw").should("be.visible");
    cy.location("pathname").should(
      "equal",
      "/meertime/J0125-2327/2023-04-29-06:47:34/2/"
    );
  });

  it("should display the download buttons where there are files", () => {
    cy.visit("/login/");
    cy.get("input[name=email]").type("buffy@sunnydale.com");
    cy.get("input[name=password]").type("slayer!#1");
    cy.contains("button", "Sign in").click();

    cy.wait("@getCSRF");
    cy.wait("@sessionLogin");

    cy.visit("/meertime/J0125-2327/2023-04-29-06:47:34/2/");
    cy.wait("@SingleObservationQuery");
    
    // Correct page loads
    cy.contains("J0125-2327").should("be.visible");

    // The download buttons are visible
    cy.contains("Download Full Resolution").should("be.visible");
    cy.contains("Download Decimated").should("be.visible");
    cy.contains("Download ToAs").should("be.visible");
  });

  it("should download files when download buttons are clicked", () => {
    cy.visit("/login/");
    cy.get("input[name=email]").type("buffy@sunnydale.com");
    cy.get("input[name=password]").type("slayer!#1");
    cy.contains("button", "Sign in").click();

    cy.wait("@getCSRF");
    cy.wait("@sessionLogin");

    cy.visit("/meertime/J0125-2327/2023-04-29-06:47:34/2/");
    cy.wait("@SingleObservationQuery");

    // Ensure the download buttons are visible and clickable
    cy.contains("Download Full Resolution").should("be.visible");
    cy.contains("Download Decimated").should("be.visible");

    // Click full resolution download button - this will open download in new tab
    cy.contains("Download Full Resolution").click();
    
    // Verify the button click worked by checking that the page is still functional
    cy.contains("J0125-2327").should("be.visible");

    // Click decimated download button - this will open download in new tab
    cy.contains("Download Decimated").click();
    
    // Verify the button click worked by checking that the page is still functional
    cy.contains("J0125-2327").should("be.visible");
  });

  it("should render the page with images", () => {
    cy.wait("@SingleObservationQuery");

    cy.get('img[alt="Plot PROFILE raw"').should("be.visible");
    cy.get('img[alt="Plot PROFILE cleaned').should("be.visible");
    cy.get('img[alt="Plot PROFILE_POL raw').should("be.visible");
    cy.get('img[alt="Plot PROFILE_POL cleaned').should("be.visible");
    cy.get('img[alt="Plot PHASE_TIME raw').should("be.visible");
    cy.get('img[alt="Plot PHASE_TIME cleaned').should("be.visible");
    cy.get('img[alt="Plot PHASE_FREQ raw').should("be.visible");
    cy.get('img[alt="Plot PHASE_FREQ cleaned').should("be.visible");
    cy.get('img[alt="Plot BANDPASS raw').should("be.visible");
    cy.get('img[alt="Plot BANDPASS cleaned').should("be.visible");
    cy.get('img[alt="Plot SNR_CUMUL raw').should("be.visible");
    cy.get('img[alt="Plot SNR_CUMUL cleaned').should("be.visible");
    cy.get('img[alt="Plot SNR_SINGLE raw').should("be.visible");
    cy.get('img[alt="Plot SNR_SINGLE cleaned').should("be.visible");
  });

  it("should render even without images", () => {
    cy.intercept("http://localhost:5173/api/graphql/", (req) => {
      aliasQuery(
        req,
        "SingleObservationQuery",
        "singleObservationQueryNoImages.json"
      );
    });
    cy.wait("@SingleObservationQuery");

    cy.contains("J0125-2327").should("be.visible");
  });

  it("should render only raw images and no empty columns/space when cleaned images are missing", () => {
    cy.intercept("http://localhost:5173/api/graphql/", (req) => {
      aliasQuery(
        req,
        "SingleObservationQuery",
        "singleObservationQueryOnlyRaw.json"
      );
    });

    cy.visit("/meertime/J0125-2327/2023-04-29-06:47:34/2/");
    cy.wait("@SingleObservationQuery");

    // The page loads successfully
    cy.contains("J0125-2327").should("be.visible");

    // "Raw" header is visible, but "Cleaned" header is NOT visible
    cy.contains("Raw").should("be.visible");
    cy.contains("Cleaned").should("not.exist");

    // Alt images for raw exist, but no cleaned images exist
    cy.get('img[alt="Plot PROFILE raw"]').should("be.visible");
    cy.get('img[alt="Plot PROFILE cleaned"]').should("not.exist");
    cy.get('img[alt="Plot PROFILE_POL raw"]').should("be.visible");
    cy.get('img[alt="Plot PROFILE_POL cleaned"]').should("not.exist");

    // Verify there are no empty columns or empty space
    // Every row within the ImageGrid should contain exactly 1 column
    cy.get(".single-observation .row")
      .first()
      .next()
      .within(() => {
        cy.get(".col")
          .first()
          .within(() => {
            cy.get(".row").each(($row) => {
              cy.wrap($row).find(".col").should("have.length", 1);
            });
          });
      });
  });
});

describe("Single Observation Page - Anonymous Access", () => {
  beforeEach(() => {
    cy.intercept("http://localhost:5173/api/graphql/", (req) => {
      aliasQuery(req, "SingleObservationQuery", "singleObservationQuery.json");
    });

    // Anonymous session
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

    cy.visit("/meertime/J0125-2327/2023-04-29-06:47:34/2/");
  });

  it("should NOT show the 3 direct-download buttons for anonymous users", () => {
    cy.wait("@SingleObservationQuery");
    cy.contains("Loading...").should("not.exist");

    // Anonymous users should not see direct-download buttons (which would 401)
    cy.contains("Download Full Resolution").should("not.exist");
    cy.contains("Download Decimated").should("not.exist");
    cy.contains("Download ToAs").should("not.exist");
  });

  it("should show EmptyStateMessage with Log in action for anonymous", () => {
    cy.wait("@SingleObservationQuery");
    cy.contains("Loading...").should("not.exist");

    // Anonymous users see an empty-state message with a "Log in" link
    cy.get('[data-testid="empty-state-message"]').should("be.visible");
    cy.contains("You must be logged in to download").should("be.visible");
    cy.contains("a", "Log in")
      .should("have.attr", "href")
      .and("match", /\/login\/?\?next=/)
      .and("include", "meertime");
  });
});
