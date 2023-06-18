// Fix packages that rely on global being defined.
if (window.global === undefined) {
  window.global = window;
}
