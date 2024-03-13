import { aliasMutation, aliasQuery } from "../utils/graphql-test-utils";

describe("The Fold Detail Page", () => {
  beforeEach(() => {
    cy.intercept("http://localhost:8000/graphql/", (req) => {
      aliasMutation(req, "LoginMutation", "loginMutation.json");
      aliasQuery(req, "FoldDetailQuery", "foldDetailQuery.json");
      aliasQuery(
        req,
        "FoldDetailFileDownloadQuery",
        "foldDetailFileDownloadQuery.json"
      );
      aliasQuery(req, "PlotContainerQuery", "plotContainerQuery.json");
      aliasQuery(req, "SingleObservationQuery", "singleObservationQuery.json");
      aliasQuery(
        req,
        "SingleObservationFileDownloadQuery",
        "singleObservationFileDownloadQuery.json"
      );
      aliasQuery(req, "SessionQuery", "sessionQuery.json");
    });
    cy.visit("fold/meertime/J0125-2327/");
    cy.location("pathname").should("equal", "/login");

    cy.get("input[name=username]").type("buffy@sunnydale.com");
    cy.get("input[name=password]").type("slayer!#1");
    cy.contains("button", "Sign in").click();

    cy.wait("@LoginMutation")
      .its("response.body.data.tokenAuth")
      .should("have.property", "token");
  });

  it("displays loading then the data", () => {
    cy.contains("J0125-2327").should("be.visible");
    cy.contains("Loading...").should("be.visible");

    cy.wait("@FoldDetailQuery");

    cy.contains("Loading...").should("not.exist");
    cy.contains("PSR J0125-2327 is a millisecond pulsar").should("be.visible");
  });

  it("should toggle the ephemeris modal", () => {
    cy.wait("@FoldDetailQuery");
    cy.contains("View folding ephemeris").should("be.visible");
    cy.contains("Folding Ephemeris").should("not.exist");
    cy.contains("View folding ephemeris").click();
    cy.contains("Folding Ephemeris").should("be.visible");
  });

  it("should go to single observation when view button is clicked", () => {
    cy.wait("@FoldDetailQuery");
    cy.contains("table tr", "2020-07-10-05:07:28").as("targetRow");
    cy.get("@targetRow").contains("View").click();
    cy.location("pathname").should(
      "equal",
      "/meertime/J0125-2327/2020-07-10-05:07:28/2/"
    );

    cy.wait("@SingleObservationQuery");

    cy.contains("Loading...").should("not.exist");
    cy.contains("2020-07-10-05:07:28").should("be.visible");
  });

  it("should go to sessions table when view session button is clicked", () => {
    cy.wait("@FoldDetailQuery");
    cy.contains("View session").click();
    cy.location("pathname").should("equal", "/session/26/");

    cy.wait("@SessionQuery");
    cy.contains("Loading...").should("not.exist");
    cy.contains("JName").should("be.visible");
  });

  it("should display in list mode", () => {
    cy.wait("@FoldDetailQuery");
    cy.contains("List view").click();

    cy.contains("Loading...").should("not.exist");
    cy.contains("PSR J0125-2327 is a millisecond pulsar").should("be.visible");
    cy.contains("2019-04-23-06:11:30").should("be.visible");
    // 4 objects are used to display the data so we're checking 1 value from each.
    cy.contains("264.00 [s]").should("be.visible");
    cy.contains("S/N").should("be.visible");
    cy.contains("100.0").should("be.visible");
    cy.contains("9.59").should("be.visible");
  });
});
