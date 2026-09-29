import React from "react";

export interface BadgeProps {
  children: React.ReactNode;
  tone?: string;
  className?: string;
}

export function Badge({ children, tone = "neutral", className = "" }: BadgeProps) {
  const toneClass = tone.toLowerCase().replace(/[^a-z0-9_-]/g, "");
  return (
    <span className={`badge ${toneClass} ${className}`}>
      {children}
    </span>
  );
}
