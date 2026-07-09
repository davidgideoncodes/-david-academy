// portal_status.js
// This file runs in the student's browser
// Every 15 seconds it asks the server "is the portal open?"
// If the answer changed, it updates the page automatically

function checkPortalStatus() {
    fetch("/api/portal-status")
        .then(function(response) {
            return response.json();
        })
        .then(function(data) {
            var portalClosed = document.getElementById("portal-closed");
            var portalOpen = document.getElementById("portal-open");

            if (!portalClosed && !portalOpen) {
                return;
            }

            if (data.is_open) {
                if (portalClosed) {
                    location.reload();
                }
            } else {
                if (portalOpen) {
                    location.reload();
                }
            }
        })
        .catch(function(error) {
            console.log("Portal status check failed:", error);
        });
}

setInterval(checkPortalStatus, 15000);