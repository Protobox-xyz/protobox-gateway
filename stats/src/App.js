import logo from './logo.svg';
import './App.css';
import {embedDashboard} from "@superset-ui/embedded-sdk";
import {useEffect} from "react";

function App() {

  async function fetchGuestToken() {
    // Fetch the guest token from your backend
    const response = await fetch(`https://s3.protobox.xyz/api/superset/${process.env.REACT_APP_DASHBOARD_ID}`);
    const data = await response.json();
    console.log(data)
    return data.token;
  }

  useEffect(() => {


    embedDashboard({
      id: process.env.REACT_APP_DASHBOARD_ID, // given by the Superset embedding UI
      supersetDomain: "https://superset.protobox.xyz",
      mountPoint: document.getElementById("my-superset-container"), // any html element that can contain an iframe
      fetchGuestToken: () => fetchGuestToken(),
      dashboardUiConfig: { // dashboard UI config: hideTitle, hideTab, hideChartControls, filters.visible, filters.expanded (optional)
        hideTitle: true,
        filters: {
          expanded: false,
        }
      },
    })
    const container = document.getElementById("my-superset-container");
    container.children[0].width = "98%";
    container.children[0].height = "1000px";
  }, []);

  return (
    <div className="App">
      <div id="my-superset-container">
      </div>
    </div>
  );
}

export default App;
