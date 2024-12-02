import { useErrorBoundary } from "react-error-boundary";

const ErrorFallback = ({ error }) => {
  const { resetBoundary } = useErrorBoundary();

  return (
    <div role="alert">
      <p>Something went wrong</p>
      <pre style={{ color: "red" }}>{error.message}</pre>
      <button className="btn btn-primary" onClick={resetBoundary}>
        Try again
      </button>
    </div>
  );
};

export default ErrorFallback;
