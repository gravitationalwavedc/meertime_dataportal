import { aliasQuery } from "../utils/graphql-test-utils";

describe("The Session Page", () => {
  beforeEach(() => {
    cy.intercept("http://localhost:8000/graphql/", (req) => {
      aliasQuery(req, "SessionQuery", "sessionQuery.json");
      aliasQuery(req, "FoldDetailQuery", "foldDetailQuery.json");
      aliasQuery(req, "PlotlyPlotQuery", "plotlyPlotQuery.json");
      aliasQuery(
        req,
        "FoldDetailFileDownloadQuery",
        "foldDetailFileDownloadQuery.json"
      );
      aliasQuery(req, "SingleObservationQuery", "singleObservationQuery.json");
      aliasQuery(
        req,
        "SingleObservationFileDownloadQuery",
        "singleObservationFileDownloadQuery.json"
      );
    });
    cy.visit("/session/2419/");
  });

  it("displays the data", () => {
    cy.contains("Sessions").should("be.visible");
    cy.wait("@SessionQuery");
    cy.contains("JName").should("be.visible");
    cy.location("pathname").should("equal", "/session/2419/");
  });

  it("check view all button", () => {
    cy.wait("@SessionQuery");
    cy.contains("View all").click();
    cy.location("pathname").should("equal", "/FOLD/meertime/J0125-2327/");

    cy.wait(["@FoldDetailQuery", "@PlotlyPlotQuery"]);
    cy.contains("Loading...").should("not.exist");
    cy.contains("PSR J0125-2327 is a millisecond pulsar").should("be.visible");
  });

  it("check view this button", () => {
    cy.wait("@SessionQuery");
    cy.contains("View this").click();
    cy.location("pathname").should(
      "equal",
      "/meertime/J0125-2327/2019-04-23-06:11:30/1/"
    );

    cy.wait("@SingleObservationQuery");
    cy.contains("Loading...").should("not.exist");
    cy.contains("Raw").should("be.visible");
  });
});
