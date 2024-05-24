let blockedWebsites = [];

async function fetchBlockedWebsites() {
  try {
    const response = await fetch('http://localhost:5000/blocked_websites');
    if (response.ok) {
      blockedWebsites = await response.json();
      console.log('Blocked websites fetched:', blockedWebsites);
    } else {
      console.error('Failed to fetch blocked websites:', response.status);
    }
  } catch (error) {
    console.error('Error fetching blocked websites:', error);
  }
}

function blockWebsite(blockedWebsites) {
  try {
    const currentURL = window.location.href;

    if (blockedWebsites.some(site => currentURL.includes(site))) {
      document.body.innerHTML = `
        <div style="display: flex; justify-content: center; align-items: center; height: 100vh; background-color: #f44336; color: white; font-size: 24px;">
          Blocked Website
        </div>
      `;
    }
  } catch (error) {
    console.error('Error blocking website:', error);
  }
}

// Send heartbeat to server
async function sendHeartbeat() {
    try {
      let incognito = false;
      if (chrome.extension.isAllowedIncognitoAccess) {
        incognito = await new Promise((resolve) => {
          chrome.extension.isAllowedIncognitoAccess(resolve);
        });
      }
  
      const response = await fetch('http://localhost:5000/heartbeat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ status: 'active', incognito: incognito })
      });
      if (!response.ok) {
        console.error('Failed to send heartbeat:', response.status);
      } else {
        console.log('Heartbeat sent successfully');
      }
    } catch (error) {
      console.error('Error sending heartbeat:', error);
    }
  }
  
  setInterval(sendHeartbeat, 5000);
  

// Fetch the blocked websites initially and start heartbeat
fetchBlockedWebsites();
setInterval(fetchBlockedWebsites, 5000);
setInterval(sendHeartbeat, 5000);

chrome.runtime.onStartup.addListener(fetchBlockedWebsites);
chrome.runtime.onInstalled.addListener(fetchBlockedWebsites);

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (blockedWebsites.length > 0) {
    chrome.scripting.executeScript({
      target: { tabId: tabId },
      func: blockWebsite,
      args: [blockedWebsites]
    }).catch(error => console.error('Error executing script:', error)); 
  }
});
