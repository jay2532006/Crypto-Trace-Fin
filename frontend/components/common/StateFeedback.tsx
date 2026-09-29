import React from "react";

export function SkeletonLoader({ text = "Loading intelligence fixture..." }: { text?: string }) {
  return (
    <div className="state-card state-loading" role="status" aria-live="polite">
      <span className="state-spinner" aria-hidden="true" />
      <span>{text}</span>
    </div>
  );
}

export function ErrorNotice({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div className="state-card state-error" role="alert">
      <div>
        <strong>Service Error</strong>
        <span>{message}</span>
      </div>
      {onRetry && <button className="btn-secondary" onClick={onRetry}>Retry</button>}
    </div>
  );
}

export function EmptyState({
  title = "No records found",
  description = "No entries match the current filter or fixture state.",
  actionLabel,
  onAction
}: {
  title?: string;
  description?: string;
  actionLabel?: string;
  onAction?: () => void;
}) {
  return (
    <div className="state-card state-empty">
      <div>
        <h3>{title}</h3>
        <p>{description}</p>
      </div>
      {actionLabel && onAction && <button className="btn-secondary" onClick={onAction}>{actionLabel}</button>}
    </div>
  );
}
