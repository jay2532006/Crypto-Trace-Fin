import React from "react";

export type Route =
  | "overview"
  | "cases"
  | "alerts"
  | "investigations"
  | "transactions"
  | "wallets"
  | "typologies"
  | "vasp"
  | "cross-chain"
  | "evidence"
  | "reports"
  | "supervisor"
  | "system";

interface SidebarProps {
  currentRoute: Route;
  onNavigate: (route: Route) => void;
  openAlertsCount?: number;
  onQuickAction?: (action: "intake" | "trace" | "supervisor") => void;
  mobileOpen?: boolean;
  onClose?: () => void;
}

type NavItem = {
  id: Route;
  label: string;
  icon: React.ReactNode;
  counter?: number;
  isAlert?: boolean;
};

export function Sidebar({
  currentRoute,
  onNavigate,
  openAlertsCount = 18,
  onQuickAction,
  mobileOpen = false,
  onClose
}: SidebarProps) {
  const [collapsed, setCollapsed] = React.useState(false);

  const navGroups: Array<{ label: string; items: NavItem[] }> = [
    {
      label: "Work",
      items: [
        { id: "overview", label: "Overview", icon: <HomeIcon /> },
        { id: "cases", label: "Cases", icon: <CasesIcon /> },
        { id: "alerts", label: "Alerts", icon: <AlertIcon />, counter: openAlertsCount, isAlert: true }
      ]
    },
    {
      label: "Trace",
      items: [
        { id: "investigations", label: "Investigations", icon: <SearchIcon /> },
        { id: "transactions", label: "Transactions", icon: <TransferIcon /> },
        { id: "wallets", label: "Wallets", icon: <WalletIcon /> },
        { id: "typologies", label: "Typologies", icon: <LayersIcon /> },
        { id: "vasp", label: "VASP Intelligence", icon: <VaspIcon /> },
        { id: "cross-chain", label: "Cross-Chain", icon: <CrossChainIcon /> }
      ]
    },
    {
      label: "Record",
      items: [
        { id: "evidence", label: "Evidence", icon: <DocumentIcon /> },
        { id: "reports", label: "Reports", icon: <ReportIcon /> },
        { id: "supervisor", label: "Supervisor", icon: <UserIcon /> },
        { id: "system", label: "System Status", icon: <SettingsIcon /> }
      ]
    }
  ];

  const navigate = (route: Route) => {
    onNavigate(route);
    onClose?.();
  };

  return (
    <>
      {mobileOpen && <button className="mobile-nav-backdrop" onClick={onClose} aria-label="Close navigation" />}
      <aside className={`kestrel-sidebar ${collapsed ? "collapsed" : ""} ${mobileOpen ? "mobile-open" : ""}`}>
        <div className="kestrel-brand">
          <button className="kestrel-logo" onClick={() => navigate("overview")} title="CryptoTrace LEA">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true">
              <path d="M4.5 19.5L12 4L19.5 19.5L12 15.3L4.5 19.5Z" fill="#05130F" />
            </svg>
          </button>
          {!collapsed && (
            <div className="kestrel-brand-text">
              <h1>CryptoTrace LEA</h1>
              <span>SIH 26183 Field Console</span>
            </div>
          )}
          {mobileOpen && (
            <button className="mobile-nav-close" onClick={onClose} aria-label="Close navigation">
              <CloseIcon />
            </button>
          )}
        </div>

        <nav className="navlist" aria-label="Investigation Navigation">
          {navGroups.map((group) => (
            <div className="nav-group" key={group.label}>
              {!collapsed && <span className="nav-section-title">{group.label}</span>}
              {group.items.map((item) => (
                <button
                  key={item.id}
                  className={currentRoute === item.id ? "is-active" : ""}
                  onClick={() => navigate(item.id)}
                  title={collapsed ? item.label : undefined}
                  aria-current={currentRoute === item.id ? "page" : undefined}
                >
                  {item.icon}
                  {!collapsed && <span>{item.label}</span>}
                  {!collapsed && item.counter !== undefined && (
                    <span className={`nav-counter ${item.isAlert ? "alert" : ""}`}>{item.counter}</span>
                  )}
                </button>
              ))}
            </div>
          ))}
        </nav>

        <div className="sidebar-quick-actions">
          {!collapsed && <div className="nav-section-title">Quick Actions</div>}
          <nav className="actionlist" aria-label="Quick Actions">
            <button onClick={() => { navigate("cases"); onQuickAction?.("intake"); }} title="Case Intake">
              <span className="dot"><PlusIcon /></span>
              {!collapsed && <span>New Intake</span>}
            </button>
            <button onClick={() => { navigate("investigations"); onQuickAction?.("trace"); }} title="Run Bounded Trace">
              <span className="dot"><ClockIcon /></span>
              {!collapsed && <span>Run Trace</span>}
            </button>
            <button onClick={() => { navigate("supervisor"); onQuickAction?.("supervisor"); }} title="Draft Preservation">
              <span className="dot"><UploadIcon /></span>
              {!collapsed && <span>Preservation</span>}
            </button>
          </nav>
        </div>

        <button
          className="sidebar-collapse-btn"
          onClick={() => setCollapsed(!collapsed)}
          aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
          title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          <svg width="18" height="18" viewBox="0 0 16 16" fill="none" aria-hidden="true">
            <path d={collapsed ? "M6 2.6L11.4 8L6 13.4" : "M10 2.6L4.6 8L10 13.4"} stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </button>
      </aside>
    </>
  );
}

function Icon({ children }: { children: React.ReactNode }) {
  return <svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true">{children}</svg>;
}

function HomeIcon() { return <Icon><path d="M4 10.6L12 4L20 10.6V19C20 19.5523 19.5523 20 19 20H5C4.44772 20 4 19.5523 4 19V10.6Z" fill="currentColor" fillOpacity="0.2" stroke="currentColor" strokeWidth="1.8" /></Icon>; }
function CasesIcon() { return <Icon><path d="M4 7V19C4 20.1 4.9 21 6 21H18C19.1 21 20 20.1 20 19V7M4 7H20M4 7L6 3H18L20 7" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" /></Icon>; }
function AlertIcon() { return <Icon><path d="M18 8A6 6 0 0 0 6 8C6 15 3 17 3 17H21S18 15 18 8Z" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" /><path d="M13.73 21A2 2 0 0 1 10.27 21" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" /></Icon>; }
function SearchIcon() { return <Icon><circle cx="11" cy="11" r="7" stroke="currentColor" strokeWidth="1.8" /><path d="M21 21L16.5 16.5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" /></Icon>; }
function TransferIcon() { return <Icon><path d="M7 16V4M7 4L3 8M7 4L11 8M17 8V20M17 20L21 16M17 20L13 16" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" /></Icon>; }
function WalletIcon() { return <Icon><rect x="3" y="6" width="18" height="13" rx="2" stroke="currentColor" strokeWidth="1.8" /><path d="M16 11H21V15H16C14.8954 15 14 14.1046 14 13C14 11.8954 14.8954 11 16 11Z" stroke="currentColor" strokeWidth="1.8" /></Icon>; }
function LayersIcon() { return <Icon><path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" /><path d="M2 17L12 22L22 17M2 12L12 17L22 12" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" /></Icon>; }
function VaspIcon() { return <Icon><path d="M3 21H21M4 18H20M5 14H19M7 10H17M9 6H15M11 2H13" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" /></Icon>; }
function CrossChainIcon() { return <Icon><path d="M16 3H21V8M21 3L13 11M8 21H3V16M3 21L11 13" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" /></Icon>; }
function DocumentIcon() { return <Icon><path d="M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 19.9V8L14 2Z" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" /><path d="M14 2V8H20" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" /></Icon>; }
function ReportIcon() { return <Icon><path d="M9 17V11M12 17V7M15 17V13M5 21H19C20.1 21 21 20.1 21 19V5C21 3.9 20.1 3 19 3H5C3.9 3 3 3.9 3 5V19C3 20.1 3.9 21 5 21Z" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" /></Icon>; }
function UserIcon() { return <Icon><path d="M12 12C14.21 12 16 10.21 16 8C16 5.79 14.21 4 12 4C9.79 4 8 5.79 8 8C8 10.21 9.79 12 12 12ZM12 14C9.33 14 4 15.34 4 18V20H20V18C20 15.34 14.67 14 12 14Z" fill="currentColor" fillOpacity="0.2" stroke="currentColor" strokeWidth="1.8" /></Icon>; }
function SettingsIcon() { return <Icon><circle cx="12" cy="12" r="3" stroke="currentColor" strokeWidth="1.8" /><path d="M19.4 15A1.65 1.65 0 0 0 20 16.2L20.2 17.5A2 2 0 0 1 18.2 19.8L16.9 19.4A1.65 1.65 0 0 0 15 20.1L14.4 21.3A2 2 0 0 1 12.1 22.4H11.9A2 2 0 0 1 9.6 21.3L9 20.1A1.65 1.65 0 0 0 7.1 19.4L5.8 19.8A2 2 0 0 1 3.8 17.5L4 16.2A1.65 1.65 0 0 0 4.6 15L3.4 14.4A2 2 0 0 1 2.3 12.1V11.9A2 2 0 0 1 3.4 9.6L4.6 9A1.65 1.65 0 0 0 4 7.8L3.8 6.5A2 2 0 0 1 5.8 4.2L7.1 4.6A1.65 1.65 0 0 0 9 3.9L9.6 2.7A2 2 0 0 1 11.9 1.6H12.1A2 2 0 0 1 14.4 2.7L15 3.9A1.65 1.65 0 0 0 16.9 4.6L18.2 4.2A2 2 0 0 1 20.2 6.5L20 7.8A1.65 1.65 0 0 0 20.6 9L21.8 9.6A2 2 0 0 1 22.9 11.9V12.1A2 2 0 0 1 21.8 14.4L20.6 15Z" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" /></Icon>; }
function PlusIcon() { return <svg width="17" height="17" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M12 5V19M5 12H19" stroke="currentColor" strokeWidth="2" strokeLinecap="round" /></svg>; }
function ClockIcon() { return <svg width="17" height="17" viewBox="0 0 24 24" fill="none" aria-hidden="true"><circle cx="12" cy="12" r="8" stroke="currentColor" strokeWidth="1.8" /><path d="M12 8V12L15 14" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" /></svg>; }
function UploadIcon() { return <svg width="17" height="17" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M12 15V4.5M8 8.5L12 4.5L16 8.5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" /><path d="M5.5 14.5V18C5.5 19 6.5 20 7.5 20H16.5C17.5 20 18.5 19 18.5 18V14.5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" /></svg>; }
function CloseIcon() { return <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M18 6L6 18M6 6L18 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" /></svg>; }
