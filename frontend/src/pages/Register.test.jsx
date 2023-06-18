import React from "react";
import Register from "./Register";
import { render, screen } from "@testing-library/react";

describe("register page", () => {
  it("should have first name, last name, email, and password fields", () => {
    expect.hasAssertions();
    const { getByLabelText } = render(<Register router={{}} match={{}} />);
    expect(getByLabelText("First Name")).toBeInTheDocument();
    expect(getByLabelText("Last Name")).toBeInTheDocument();
    expect(getByLabelText("Email")).toBeInTheDocument();
    expect(getByLabelText("Password")).toBeInTheDocument();
  });
});
