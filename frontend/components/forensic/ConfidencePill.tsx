import * as React from "react";
import { ConfidenceLevel, LabelType } from "@/types/domain";
import { Badge } from "@/components/ui/Badge";

interface ConfidencePillProps {
  confidence?: ConfidenceLevel | string;
  level?: ConfidenceLevel | string;
  score?: number;
  label?: string;
  labelType?: LabelType;
}

export function ConfidencePill({ confidence, level, score, label, labelType }: ConfidencePillProps) {
  const conf = (level || confidence || "MEDIUM").toUpperCase();

  const variant =
    conf === "HIGH"
      ? "success"
      : conf === "MEDIUM"
      ? "warning"
      : conf === "LOW"
      ? "destructive"
      : "institutional";

  return (
    <div className="inline-flex items-center gap-1.5">
      <Badge variant={variant as any}>
        {label || `${conf} CONFIDENCE`}
        {score !== undefined ? ` (${Math.round(score * 100)}%)` : ""}
      </Badge>
      {labelType && (
        <Badge variant={labelType === "VERIFIED" ? "success" : "warning"} className="text-[10px]">
          {labelType}
        </Badge>
      )}
    </div>
  );
}
