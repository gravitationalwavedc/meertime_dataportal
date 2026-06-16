import { fireEvent, render, screen } from "@testing-library/react";
import { vi } from "vitest";

import EmptyStateMessage from "./EmptyStateMessage";

describe("EmptyStateMessage", () => {
  it("renders with default title and no body when no props are given", () => {
    render(<EmptyStateMessage />);

    expect(screen.getByText("No data")).toBeInTheDocument();
    expect(screen.queryByTestId("empty-state-body")).not.toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: /.*/ })
    ).not.toBeInTheDocument();
  });

  it("renders all optional props when supplied", () => {
    render(
      <EmptyStateMessage
        title="Nothing here yet"
        body="Check back later."
        actionLabel="Refresh"
        onAction={() => {}}
      />
    );

    expect(screen.getByText("Nothing here yet")).toBeInTheDocument();
    expect(screen.getByText("Check back later.")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Refresh" })).toBeInTheDocument();
  });

  it("applies border-danger class when variant is 'danger'", () => {
    render(<EmptyStateMessage variant="danger" title="Error" />);

    const card = screen.getByTestId("empty-state-message");
    expect(card).toHaveClass("border-danger");
  });

  it("applies border-warning class when variant is 'warning'", () => {
    render(<EmptyStateMessage variant="warning" title="Heads up" />);

    const card = screen.getByTestId("empty-state-message");
    expect(card).toHaveClass("border-warning");
  });

  it("omits any border-* class when variant is 'info' (default)", () => {
    const { rerender } = render(<EmptyStateMessage title="Plain" />);
    let card = screen.getByTestId("empty-state-message");
    expect(card).not.toHaveClass("border-info");
    expect(card).not.toHaveClass("border-warning");
    expect(card).not.toHaveClass("border-danger");

    rerender(<EmptyStateMessage variant="info" title="Plain info" />);
    card = screen.getByTestId("empty-state-message");
    expect(card).not.toHaveClass("border-info");
    expect(card).not.toHaveClass("border-warning");
    expect(card).not.toHaveClass("border-danger");
  });

  it("invokes onAction when the action button is clicked", () => {
    const handleAction = vi.fn();

    render(
      <EmptyStateMessage
        title="Empty"
        actionLabel="Try again"
        onAction={handleAction}
      />
    );

    fireEvent.click(screen.getByRole("button", { name: "Try again" }));

    expect(handleAction).toHaveBeenCalledTimes(1);
  });

  it("renders a link with the given actionHref when actionHref is set", () => {
    render(
      <EmptyStateMessage
        title="Empty"
        actionLabel="Go home"
        actionHref="/home/"
      />
    );

    const link = screen.getByRole("link", { name: "Go home" });
    expect(link).toHaveAttribute("href", "/home/");
  });
});
