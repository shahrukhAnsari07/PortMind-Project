function Header({
  title = "PortMind AI",
}) {
  return (
    <header className="legacy-header">

      <div>
        <strong>
          ⚓ {title}
        </strong>

        <span>
          Real-Time Shipping Port
          Digital Twin
        </span>
      </div>

      <span className="live-badge">
        ● SYSTEM ONLINE
      </span>

    </header>
  );
}

export default Header;