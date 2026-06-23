import { Button, Card } from "react-bootstrap";
import { Link } from "found";

const EmptyStateMessage = ({
  title,
  message,
  body,
  variant = "info",
  actionLabel,
  onAction,
  actionHref,
  className,
}) => {
  const displayTitle = title || message || "No data";

  const borderClass =
    variant === "warning"
      ? "border-warning"
      : variant === "danger"
      ? "border-danger"
      : "";

  const cardClassName = ["text-center", borderClass, className]
    .filter(Boolean)
    .join(" ");

  return (
    <Card className={cardClassName} data-testid="empty-state-message">
      <Card.Body>
        <Card.Title>{displayTitle}</Card.Title>
        {body && <Card.Text>{body}</Card.Text>}
        {actionLabel && actionHref && (
          <Button as={Link} to={actionHref} variant="primary">
            {actionLabel}
          </Button>
        )}
        {actionLabel && !actionHref && onAction && (
          <Button onClick={onAction} variant="primary">
            {actionLabel}
          </Button>
        )}
      </Card.Body>
    </Card>
  );
};

export default EmptyStateMessage;
