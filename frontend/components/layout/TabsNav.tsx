import React from "react";

export interface TabItem {
  id: string;
  label: string;
  counter?: number;
}

interface TabsNavProps {
  tabs: TabItem[];
  activeTab: string;
  onTabChange: (id: string) => void;
}

export function TabsNav({ tabs, activeTab, onTabChange }: TabsNavProps) {
  return (
    <nav className="kestrel-tabs" aria-label="Secondary Navigation">
      {tabs.map((tab) => (
        <button
          key={tab.id}
          className={activeTab === tab.id ? "is-active" : ""}
          onClick={() => onTabChange(tab.id)}
        >
          <span>{tab.label}</span>
          {tab.counter !== undefined && (
            <span style={{
              marginLeft: "8px",
              fontSize: "11px",
              padding: "2px 7px",
              borderRadius: "999px",
              background: activeTab === tab.id ? "var(--accent-tint)" : "var(--elev-2)",
              color: activeTab === tab.id ? "var(--accent-2)" : "var(--text-3)",
              fontWeight: 700
            }}>
              {tab.counter}
            </span>
          )}
        </button>
      ))}
    </nav>
  );
}
