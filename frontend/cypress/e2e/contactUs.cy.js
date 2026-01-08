import { aliasMutation } from "../utils/graphql-test-utils";

describe("Contact Us Page", () => {
  beforeEach(() => {
    // Mock grecaptcha globally
    cy.window().then((win) => {
      win.grecaptcha = {
        ready: (callback) => callback(),
        execute: () => Promise.resolve("mock_captcha_token"),
      };
    });

    // Mock GraphQL requests
    cy.intercept("http://localhost:5173/api/graphql/", (req) => {
      aliasMutation(req, "ContactUsMutation", "contactFormSuccess.json");
    });

    // Mock session-based authentication endpoints
    cy.intercept("GET", "/api/auth/csrf/", {
      statusCode: 200,
      body: { csrfToken: "mock-csrf-token" }
    }).as("getCSRF");

    cy.intercept("GET", "/api/auth/session/", {
      statusCode: 200,
      body: {
        isAuthenticated: false,
        user: null
      }
    }).as("checkSession");
  });

  it("should display contact form correctly", () => {
    cy.visit("/contact-us/");
    
    // Check page elements
    cy.contains("Contact Us / Report Issue").should("be.visible");
    cy.get("select#contactType").should("be.visible");
    cy.get("textarea#message").should("be.visible");
    cy.get("button[type='submit']").should("be.visible");
    
    // Check default contact type
    cy.get("select#contactType").should("have.value", "Contact Us");
  });

  it("should display reCAPTCHA notice", () => {
    cy.visit("/contact-us/");
    
    cy.contains("This site is protected by reCAPTCHA").should("be.visible");
    cy.contains("Privacy Policy").should("be.visible");
    cy.contains("Terms of Service").should("be.visible");
  });

  it("should show name and email fields for unauthenticated users", () => {
    cy.visit("/contact-us/");
    
    cy.get("input#name").should("be.visible");
    cy.get("input#email").should("be.visible");
  });

  it("should submit Contact Us form successfully (unauthenticated)", () => {
    cy.visit("/contact-us/");
    
    // Fill out form
    cy.get("select#contactType").select("Contact Us");
    cy.get("input#name").type("Test User");
    cy.get("input#email").type("test@example.com");
    cy.get("textarea#message").type("This is a test message for the contact form.");
    
    // Submit
    cy.get("button[type='submit']").click();
    
    // Wait for mutation
    cy.wait("@ContactUsMutation");
    
    // Check success message
    cy.contains("Thank you for contacting us!").should("be.visible");
    cy.contains("Your message has been sent successfully").should("be.visible");
  });

  it("should show link field when Report Issue is selected", () => {
    cy.visit("/contact-us/");
    
    // Initially link field should not be visible
    cy.get("input#link").should("not.exist");
    
    // Select Report Issue
    cy.get("select#contactType").select("Report Issue");
    
    // Link field should now be visible
    cy.get("input#link").should("be.visible");
  });

  it("should show helper text when Report Issue is selected", () => {
    cy.visit("/contact-us/");
    
    // Select Report Issue
    cy.get("select#contactType").select("Report Issue");
    
    // Check helper text
    cy.contains("Please describe the issue below").should("be.visible");
    cy.contains("Data issues").should("be.visible");
    cy.contains("Website issues").should("be.visible");
    cy.contains("create a GitLab issue").should("be.visible");
  });

  it("should require link field for Report Issue", () => {
    cy.visit("/contact-us/");
    
    // Select Report Issue
    cy.get("select#contactType").select("Report Issue");
    
    // Fill out form without link
    cy.get("input#name").type("Test User");
    cy.get("input#email").type("test@example.com");
    cy.get("textarea#message").type("There is an issue");
    
    // Try to submit
    cy.get("button[type='submit']").click();
    
    // Should show validation error message from Yup
    cy.contains("Link is required when reporting an issue").should("be.visible");
  });

  it("should submit Report Issue form with link successfully", () => {
    cy.visit("/contact-us/");
    
    // Select Report Issue
    cy.get("select#contactType").select("Report Issue");
    
    // Fill out form
    cy.get("input#name").type("Test User");
    cy.get("input#email").type("test@example.com");
    cy.get("input#link").type("https://pulsars.org.au/MeerTime/J0437-4715/");
    cy.get("textarea#message").type("Data appears incorrect for this pulsar.");
    
    // Submit
    cy.get("button[type='submit']").click();
    
    // Wait for mutation
    cy.wait("@ContactUsMutation");
    
    // Check success message
    cy.contains("Thank you for contacting us!").should("be.visible");
  });

  it("should validate required fields", () => {
    cy.visit("/contact-us/");
    
    // Try to submit empty form
    cy.get("button[type='submit']").click();
    
    // Should show Yup validation errors
    cy.contains("Please include your name").should("be.visible");
    cy.contains("Please include an email").should("be.visible");
    cy.contains("Please include a message").should("be.visible");
  });

  it("should validate email format", () => {
    cy.visit("/contact-us/");
    
    // Fill form with invalid email
    cy.get("input#name").type("Test User");
    cy.get("input#email").type("invalid-email");
    cy.get("textarea#message").type("Test message");
    
    // Try to submit
    cy.get("button[type='submit']").click();
    
    // Should show Yup validation error
    cy.contains("Invalid email format").should("be.visible");
  });

  it("should show character count for message field", () => {
    cy.visit("/contact-us/");
    
    const testMessage = "This is a test message";
    cy.get("textarea#message").type(testMessage);
    
    // Check character count
    cy.contains(`${testMessage.length}/2000`).should("be.visible");
  });

  it("should validate maximum message length", () => {
    cy.visit("/contact-us/");
    
    // Fill form
    cy.get("input#name").type("Test User");
    cy.get("input#email").type("test@example.com");
    
    // Create message over 2000 characters
    const longMessage = "A".repeat(2001);
    cy.get("textarea#message").invoke("val", longMessage).trigger("change");
    
    // Try to submit
    cy.get("button[type='submit']").click();
    
    // Should show validation error (Yup validation)
    cy.contains("2000 characters").should("be.visible");
  });

  it("should handle submission errors", () => {
    // Mock error response
    cy.intercept("http://localhost:5173/api/graphql/", (req) => {
      if (req.body.query && req.body.query.includes("ContactUsMutation")) {
        req.reply({
          fixture: "contactFormError.json"
        });
        req.alias = "ContactUsMutation";
      }
    });
    
    cy.visit("/contact-us/");
    
    // Fill and submit form
    cy.get("input#name").type("Test User");
    cy.get("input#email").type("test@example.com");
    cy.get("textarea#message").type("Test message");
    cy.get("button[type='submit']").click();
    
    cy.wait("@ContactUsMutation");
    
    // Should show error message
    cy.get(".alert-danger").should("be.visible");
    cy.contains("Captcha validation failed").should("be.visible");
  });

  it("should allow sending another message after success", () => {
    cy.visit("/contact-us/");
    
    // Submit form
    cy.get("input#name").type("Test User");
    cy.get("input#email").type("test@example.com");
    cy.get("textarea#message").type("First message");
    cy.get("button[type='submit']").click();
    
    cy.wait("@ContactUsMutation");
    
    // Click send another message
    cy.contains("Send Another Message").click();
    
    // Form should be visible again
    cy.get("textarea#message").should("be.visible");
    cy.get("button[type='submit']").should("be.visible");
  });

  it("should work for authenticated users without name/email fields", () => {
    // Mock authenticated session
    cy.intercept("GET", "/api/auth/session/", {
      statusCode: 200,
      body: {
        isAuthenticated: true,
        user: {
          username: "testuser@test.com",
          email: "testuser@test.com",
          isStaff: false,
          isUnrestricted: true
        }
      }
    }).as("checkSessionAuth");
    
    cy.visit("/contact-us/");
    
    // Name and email fields should not be visible
    cy.get("input#name").should("not.exist");
    cy.get("input#email").should("not.exist");
    
    // Fill and submit form
    cy.get("select#contactType").select("Contact Us");
    cy.get("textarea#message").type("Message from authenticated user");
    cy.get("button[type='submit']").click();
    
    cy.wait("@ContactUsMutation");
    
    // Check success
    cy.contains("Thank you for contacting us!").should("be.visible");
  });

  it("should hide link field when switching from Report Issue to Contact Us", () => {
    cy.visit("/contact-us/");
    
    // Select Report Issue
    cy.get("select#contactType").select("Report Issue");
    cy.get("input#link").should("be.visible");
    
    // Switch back to Contact Us
    cy.get("select#contactType").select("Contact Us");
    cy.get("input#link").should("not.exist");
  });

  it("should validate all fields together", () => {
    cy.visit("/contact-us/");
    
    // Fill valid form
    cy.get("select#contactType").select("Report Issue");
    cy.get("input#name").type("Valid Name");
    cy.get("input#email").type("valid@example.com");
    cy.get("input#link").type("https://pulsars.org.au/test");
    cy.get("textarea#message").type("This is a valid message with sufficient content.");
    
    // Submit should work
    cy.get("button[type='submit']").click();
    cy.wait("@ContactUsMutation");
    cy.contains("Thank you for contacting us!").should("be.visible");
  });
});
