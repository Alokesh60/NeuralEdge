import React from "react";

const Header = () => {
  return (
    <header
      style={{
        background: "var(--surface)",
        borderBottom: "1px solid var(--border)",
        padding: "1rem 2rem",
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        position: "sticky",
        top: 0,
        zIndex: 50,
      }}
    >
      <div
        className="logo"
        style={{
          display: "flex",
          alignItems: "center",
          gap: "10px",
          fontWeight: 700,
          fontSize: "1.25rem",
        }}
      >
        <span className="logo-icon">⚖️</span>
        AuditPro
        <span style={{ fontWeight: 300, color: "var(--text-muted)" }}>
          Analytics
        </span>
      </div>
      <div
        className="user-badge"
        style={{
          fontSize: "0.8rem",
          background: "var(--primary-light)",
          color: "var(--primary)",
          padding: "4px 12px",
          borderRadius: "20px",
          fontWeight: 600,
        }}
      >
        NIT Silchar Hub
      </div>
    </header>
  );
};

export default Header;
