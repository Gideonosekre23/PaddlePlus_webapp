import React from "react";
import { Home, Map, Settings, ExitToApp } from "@mui/icons-material";
import { useNavigate } from "react-router-dom";

const OwnerNav = ({ isExpanded }) => {
  // const navigate = useNavigate();

  const handleLogout = () => {
    // localStorage.clear();
    // navigate("/landing");
  }

  return (
    <ul className="nav-options">
      <li>
        <Home />
        {isExpanded && <span>Home</span>}
      </li>
      <li>
        <Map />
        {isExpanded && <span>Map</span>}
      </li>
      <li>
        <Settings />
        {isExpanded && <span>Settings</span>}
      </li>
      <li className="logout" onClick={() => handleLogout()}>
        <ExitToApp />
        {isExpanded && <span>Log Out</span>}
      </li>
    </ul>
  );
};

export default OwnerNav;