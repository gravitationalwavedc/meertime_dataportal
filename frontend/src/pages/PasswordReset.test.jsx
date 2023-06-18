import { fireEvent, render, waitFor } from "@testing-library/react";

import PasswordReset from "./PasswordReset";
import { MockPayloadGenerator } from "relay-test-utils";
import React from "react";
import environment from "../relayEnvironment";

/* global mockRouter */
/* eslint-disable react/display-name */

vi.mock("found", () => ({
  Link: (component) => <div>{component.children}</div>,
  useRouter: () => ({
    router: {
      push: vi.fn(),
      replace: vi.fn(),
      go: vi.fn(),
      createHref: vi.fn(),
      createLocation: vi.fn(),
      isActive: vi.fn(),
      matcher: {
        match: vi.fn(),
        getRoutes: vi.fn(),
        isActive: vi.fn(),
        format: vi.fn(),
      },
      addTransitionHook: vi.fn(),
    },
  }),
}));

describe("password reset page", () => {
  it("should have code, password and confirm password fields", () => {
    expect.hasAssertions();
    const { getByLabelText } = render(<PasswordReset router={{}} match={{}} />);
    expect(
      getByLabelText("Verification Code (Sent to your email)")
    ).toBeInTheDocument();
    expect(getByLabelText("New Password")).toBeInTheDocument();
    expect(getByLabelText("Confirm New Password")).toBeInTheDocument();
  });
});
