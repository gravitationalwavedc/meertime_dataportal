import { render, screen } from "@testing-library/react";
import { vi } from "vitest";

vi.mock("react-relay", async () => {
  const actual = await vi.importActual("react-relay");
  return {
    ...actual,
    useQueryLoader: () => [null, vi.fn()],
  };
});

import HeaderButtons from "./HeaderButtons";

describe("HeaderButtons", () => {
  describe("when authenticated and project is not MONSPSR", () => {
    it("renders all 3 direct-download buttons", () => {
      render(
        <HeaderButtons
          jname="J0125-2327"
          mainProject="meertime"
          isAuthenticated
        />
      );

      expect(
        screen.getByRole("button", { name: "Download Full Resolution Data" })
      ).toBeInTheDocument();
      expect(
        screen.getByRole("button", { name: "Download Decimated Data" })
      ).toBeInTheDocument();
      expect(
        screen.getByRole("button", { name: "Download ToAs" })
      ).toBeInTheDocument();
    });

    it("does NOT render the EmptyStateMessage", () => {
      render(
        <HeaderButtons
          jname="J0125-2327"
          mainProject="meertime"
          isAuthenticated
        />
      );

      expect(
        screen.queryByTestId("empty-state-message")
      ).not.toBeInTheDocument();
    });

    it("still renders the 2 modal-trigger buttons", () => {
      render(
        <HeaderButtons
          jname="J0125-2327"
          mainProject="meertime"
          isAuthenticated
        />
      );

      expect(
        screen.getByRole("button", { name: "View folding ephemeris" })
      ).toBeInTheDocument();
      expect(
        screen.getByRole("button", { name: "Download template" })
      ).toBeInTheDocument();
    });
  });

  describe("when anonymous and project is not MONSPSR", () => {
    it("does NOT render any of the 3 direct-download buttons", () => {
      render(
        <HeaderButtons
          jname="J0125-2327"
          mainProject="meertime"
          isAuthenticated={false}
        />
      );

      expect(
        screen.queryByRole("button", { name: "Download Full Resolution Data" })
      ).not.toBeInTheDocument();
      expect(
        screen.queryByRole("button", { name: "Download Decimated Data" })
      ).not.toBeInTheDocument();
      expect(
        screen.queryByRole("button", { name: "Download ToAs" })
      ).not.toBeInTheDocument();
    });

    it("renders an EmptyStateMessage with title and body", () => {
      render(
        <HeaderButtons
          jname="J0125-2327"
          mainProject="meertime"
          isAuthenticated={false}
        />
      );

      const emptyState = screen.getByTestId("empty-state-message");
      expect(emptyState).toBeInTheDocument();
      expect(
        screen.getByText("You must be logged in to download")
      ).toBeInTheDocument();
      expect(
        screen.getByText(
          "Sign in to access full resolution, decimated, and ToA data."
        )
      ).toBeInTheDocument();
    });

    it("renders a Log in link whose href points to /login/?next=<current-path>", () => {
      render(
        <HeaderButtons
          jname="J0125-2327"
          mainProject="meertime"
          isAuthenticated={false}
        />
      );

      const link = screen.getByRole("link", { name: "Log in" });
      expect(link).toBeInTheDocument();
      const href = link.getAttribute("href");
      expect(href).toMatch(/^\/login\/?\?next=/);
    });

    it("still renders the 2 modal-trigger buttons (MR-4 closes that gap)", () => {
      render(
        <HeaderButtons
          jname="J0125-2327"
          mainProject="meertime"
          isAuthenticated={false}
        />
      );

      expect(
        screen.getByRole("button", { name: "View folding ephemeris" })
      ).toBeInTheDocument();
      expect(
        screen.getByRole("button", { name: "Download template" })
      ).toBeInTheDocument();
    });
  });

  describe("when authenticated and project is MONSPSR", () => {
    it("does NOT render any of the 3 direct-download buttons (MONSPSR carve-out)", () => {
      render(
        <HeaderButtons
          jname="J0125-2327"
          mainProject="MONSPSR"
          isAuthenticated
        />
      );

      expect(
        screen.queryByRole("button", { name: "Download Full Resolution Data" })
      ).not.toBeInTheDocument();
      expect(
        screen.queryByRole("button", { name: "Download Decimated Data" })
      ).not.toBeInTheDocument();
      expect(
        screen.queryByRole("button", { name: "Download ToAs" })
      ).not.toBeInTheDocument();
    });

    it("does NOT render an EmptyStateMessage", () => {
      render(
        <HeaderButtons
          jname="J0125-2327"
          mainProject="MONSPSR"
          isAuthenticated
        />
      );

      expect(
        screen.queryByTestId("empty-state-message")
      ).not.toBeInTheDocument();
    });

    it("still renders the 2 modal-trigger buttons", () => {
      render(
        <HeaderButtons
          jname="J0125-2327"
          mainProject="MONSPSR"
          isAuthenticated
        />
      );

      expect(
        screen.getByRole("button", { name: "View folding ephemeris" })
      ).toBeInTheDocument();
      expect(
        screen.getByRole("button", { name: "Download template" })
      ).toBeInTheDocument();
    });
  });

  describe("when anonymous and project is MONSPSR", () => {
    it("does NOT render any of the 3 direct-download buttons", () => {
      render(
        <HeaderButtons
          jname="J0125-2327"
          mainProject="MONSPSR"
          isAuthenticated={false}
        />
      );

      expect(
        screen.queryByRole("button", { name: "Download Full Resolution Data" })
      ).not.toBeInTheDocument();
      expect(
        screen.queryByRole("button", { name: "Download Decimated Data" })
      ).not.toBeInTheDocument();
      expect(
        screen.queryByRole("button", { name: "Download ToAs" })
      ).not.toBeInTheDocument();
    });

    it("does NOT render an EmptyStateMessage (MONSPSR carve-out)", () => {
      render(
        <HeaderButtons
          jname="J0125-2327"
          mainProject="MONSPSR"
          isAuthenticated={false}
        />
      );

      expect(
        screen.queryByTestId("empty-state-message")
      ).not.toBeInTheDocument();
    });

    it("still renders the 2 modal-trigger buttons", () => {
      render(
        <HeaderButtons
          jname="J0125-2327"
          mainProject="MONSPSR"
          isAuthenticated={false}
        />
      );

      expect(
        screen.getByRole("button", { name: "View folding ephemeris" })
      ).toBeInTheDocument();
      expect(
        screen.getByRole("button", { name: "Download template" })
      ).toBeInTheDocument();
    });
  });
});
