/**
 * You have a limited version of the Millennium API available to you in the webkit context.
 */
type Millennium = {
    /**
     * Call a function in the backend (python) of your plugin
     * @param methodName a public static method declared and defined in your plugin backend (python)
     * @param kwargs an object of key value pairs that will be passed to the backend method. accepted types are: string, number, boolean
     * @returns string | number | boolean
     */
    callServerMethod: (methodName: string, kwargs?: any) => Promise<any>,
    /**
     * Async wait for an element in the document using DOM observers and querySelector
     * @param privateDocument document object of the webkit context
     * @param querySelector the querySelector string to find the element (as if you were using document.querySelector)
     * @param timeOut If the element is not found within the timeOut, the promise will reject
     * @returns 
     */
    findElement: (privateDocument: Document,  querySelector: string, timeOut?: number) => Promise<NodeListOf<Element>>,
};

declare const Millennium: Millennium;

export default async function WebkitMain() {
    
    console.log("FaceIt Stats loaded.")
    const rightCol = await Millennium.findElement(document, '.profile_rightcol');

    if (rightCol.length > 0) {
        console.log("Detected rightcol.");
        
        // Create and show loading spinner immediately
        const loadingHTML = document.createElement("div");
        loadingHTML.className = "account-row";
        loadingHTML.innerHTML = `
            <div class="faceit-loading-container">
                <div class="faceit-spinner"></div>
                <div class="faceit-loading-text">Loading Faceit data...</div>
            </div>
        `;
        rightCol[0].insertBefore(loadingHTML, rightCol[0].children[1]);
        
        try {
            const parser = new DOMParser();

            // Fetch the XML data from the current document URL with ?xml=1 appended
            const profileUrl = `${window.location.href}/?xml=1`;
            const profileResponse = await fetch(profileUrl);
            const profileXmlText = await profileResponse.text();
            const profileXmlDoc = parser.parseFromString(profileXmlText, "application/xml");

            // Extract the necessary variables from the XML
            const steamID64 = profileXmlDoc.querySelector("steamID64")?.textContent || "0";

            const memberSince = profileXmlDoc.querySelector("memberSince")?.textContent || "N/A";
            const vacBanned = parseInt(profileXmlDoc.querySelector("vacBanned")?.textContent || "0", 10);
            const tradeBanState = profileXmlDoc.querySelector("tradeBanState")?.textContent || "Not played.";
            const isLimitedAccount = parseInt(profileXmlDoc.querySelector("isLimitedAccount")?.textContent || "0", 10);
            
            const gameStatUrl = `${window.location.href}/games?tab=all&xml=1`;
            const gameResponse = await fetch(gameStatUrl);
            const gameXmlText = await gameResponse.text();
            const gameXmlDoc = parser.parseFromString(gameXmlText, "application/xml");

            const cs2 = Array.from(gameXmlDoc.querySelectorAll("game")).find(g => g.querySelector("appID")?.textContent === "730");
            const csHours = cs2 ? cs2.querySelector("hoursOnRecord")?.textContent || "Private" : "Private";
            const csRecentHours = cs2 ? cs2.querySelector("hoursLast2Weeks")?.textContent || "0" : "Private";
            
            // Fetch stats from the /stats/CSGO?xml=1 URL
            const statsUrl = `${window.location.href}/stats/CSGO?xml=1`;
            const statsResponse = await fetch(statsUrl);
            const statsText = await statsResponse.text();
            const statsXml = parser.parseFromString(statsText, "application/xml");

            // Extract the unlock timestamp and format it
            const unlockTimestamp = statsXml.querySelector("achievement > unlockTimestamp")?.textContent ?? null;
            const playsSince = unlockTimestamp
                ? new Date(parseInt(unlockTimestamp, 10) * 1000).toLocaleDateString("en-US", { year: 'numeric', month: 'long', day: 'numeric' })
                : "None";

            //const bannedFriends = gameXmlDoc.querySelector("bannedFriends")?.textContent || "0/0 (0%)";
            // Create a new div to hold the stats HTML
            const faceItUser = await Millennium.callServerMethod("get_user_by_steamId", {steamId: steamID64})
            const faceItUserJSON = JSON.parse(faceItUser);

            const leetifyAimRating = await Millennium.callServerMethod("get_aim_rating", {steamId: steamID64})

            const statsHTML = document.createElement("div");
            statsHTML.innerHTML = `
            <div class="account-row">
                <div id="steaminfo_76561198328925991" class="account-steaminfo-container">
                    <div class="account-steaminfo-row">
                        <ul style="margin: 0; padding: 0;">
                            <li class="tick acc_created">Created: <span class="account-steaminfo-row-value">${memberSince}</span></li>
                        </ul>
                    </div>
                    <div class="account-steaminfo-row">
                        <ul style="margin: 0; padding: 0;">
                            <li class="tick">Restrictions:
                                <span class="account-steaminfo-row-value ${vacBanned === 0 ? 'account-steaminfo-row-value-confirmed' : 'account-steaminfo-row-value-urgent'}">VAC</span>
                                <span class="account-steaminfo-row-value ${tradeBanState === "None" ? 'account-steaminfo-row-value-confirmed' : 'account-steaminfo-row-value-urgent'}">Trade</span>
                                <span class="account-steaminfo-row-value ${isLimitedAccount === 0 ? 'account-steaminfo-row-value-confirmed' : 'account-steaminfo-row-value-urgent'}">Limited</span>
                            </li>
                        </ul>
                    </div>
                    <div class="account-steaminfo-row">
                        <ul style="margin: 0; padding: 0;">
                            <li class="cross">CS2 since: <span class="account-steaminfo-row-value">${playsSince}</span></li>
                        </ul>
                    </div>
                    <div class="account-steaminfo-row">
                        <ul style="margin: 0; padding: 0;">
                            <li class="tick">CS total hours: <a target="_blank" class="nolink" href="https://steamcommunity.com/profiles/${steamID64}/games/?tab=all" rel="noopener"><span class="account-steaminfo-row-value">${csHours}</span></a></li>
                        </ul>
                    </div>
                    <div class="account-steaminfo-row">
                        <ul style="margin: 0; padding: 0;">
                            <li class="tick">CS2 last 2 weeks hours: <a target="_blank" class="nolink" href="https://steamcommunity.com/profiles/${steamID64}/games/?tab=recent" rel="noopener"><span class="account-steaminfo-row-value">${csRecentHours}</span></a></li>
                        </ul>
                    </div>
                    <div class="account-steaminfo-row">
                        <ul style="margin: 0; padding: 0;">
                            <li class="tick">Leetify aim rating: <a target="_blank" class="nolink" href="https://leetify.com/app/profile/${steamID64}" rel="noopener"><span class="account-steaminfo-row-value">${leetifyAimRating != 0 ? `${leetifyAimRating}%` : 'N/A'}</span></a></li>
                        </ul>
                    </div>
                </div>
                <div class="account-faceitinfo-container">
                    <div class="account-faceit-cover" style="background-image: url(${faceItUserJSON?.cover_image_url ?? ''})"></div>
                    ${
                        faceItUserJSON
                            ? `
                            <a target="_blank" class="nolink" href="https://www.faceit.com/en/players/${faceItUserJSON?.nickname ?? ''}" rel="noopener">
                                <img src="https://steamloopback.host/FaceItFinder/faceit_arrow.png" class="account-faceitinfo-container-arrow" alt="FaceIt profile arrow">
                            </a>
                            <div class="account-faceit-title">
                                <a target="_blank" class="nolink" href="https://www.faceit.com/en/players/${faceItUserJSON?.nickname ?? ''}" rel="noopener">
                                    <img class="account-faceit-flag" src="https://faceitfinder.com/resources/flags/svg/${faceItUserJSON?.country ?? 'default'}.svg" alt="FaceIt country flag" width="26" height="20">
                                    <span class="account-faceit-title-username">${faceItUserJSON?.nickname ?? 'Unknown'}</span>
                                </a>
                            </div>
                            <div class="account-faceit-level">
                                <a target="_blank" class="nolink" href="https://www.faceit.com/en/players/${faceItUserJSON?.nickname ?? ''}/stats/cs2" rel="noopener">
                                    <img src="https://steamloopback.host/FaceItFinder/skill_level_${faceItUserJSON?.skill_level ?? 0}_lg.png" alt="FaceIt level ${faceItUserJSON?.skill_level ?? 0} icon" width="48" height="48">
                                </a>
                            </div>
                            <div class="stats_pager">
                                <div class="account-faceit-stats page1">
                                    <div class="account-faceit-stats-single">Matches: <strong>${faceItUserJSON?.stats?.matches ?? 'N/A'}</strong></div>
                                    <div class="account-faceit-stats-single">ELO: <strong>${faceItUserJSON?.faceit_elo ?? 'N/A'}</strong></div>
                                    <div class="account-faceit-stats-single">K/D: <strong>${faceItUserJSON?.stats?.avg_kd ?? 'N/A'}</strong></div>
                                </div>
                                <div class="account-faceit-stats page2 hidden">
                                    <div class="account-faceit-stats-single">H/S: <strong>${faceItUserJSON?.stats?.avg_hs ?? 'N/A'}</strong></div>
                                    <div class="account-faceit-stats-single">ADR: <strong>${faceItUserJSON?.stats?.adr ?? 'N/A'}</strong></div>
                                    <div class="account-faceit-stats-single">WIN: <strong>${faceItUserJSON?.stats?.winrate ?? 'N/A'}</strong></div>
                                </div>
                            </div>
                            <div class="account-faceit-detailed-stats">
                                <a class="nolink" href="https://faceittracker.net/players/${faceItUserJSON?.nickname ?? ''}">Show detailed Faceit stats</a>
                            </div>
                            `
                            : `<div class="account-faceit-message"><strong>No FaceIt account found.</strong></div>`
                    }
                </div>
            </div>
            `;
            
            // Remove loading spinner and add content
            rightCol[0].removeChild(loadingHTML);
            rightCol[0].insertBefore(statsHTML, rightCol[0].children[1]);
            const statsPager = statsHTML.querySelector('.stats_pager');
            if (statsPager) {
                statsPager.addEventListener('click', () => {
                    const page1 = statsPager.querySelector('.page1');
                    const page2 = statsPager.querySelector('.page2');

                    // Toggle the hidden class between page1 and page2
                    if (page1.classList.contains('hidden')) {
                        page1.classList.remove('hidden');
                        page2.classList.add('hidden');
                    } else {
                        page1.classList.add('hidden');
                        page2.classList.remove('hidden');
                    }
                });
            }
        }
        catch (e) {
            console.log(e);
            
            // Remove loading spinner and show error message on failure
            try {
                rightCol[0].removeChild(loadingHTML);
                
                // Create an error message element
                const errorHTML = document.createElement("div");
                errorHTML.className = "account-row";
                errorHTML.innerHTML = `
                    <div class="account-container">
                        <div class="account-faceit-message">
                            <strong>Failed to load Faceit data.</strong>
                        </div>
                    </div>
                `;
                rightCol[0].insertBefore(errorHTML, rightCol[0].children[1]);
            } catch (cleanupError) {
                console.log("Error cleaning up loading spinner:", cleanupError);
            }
        }
    } else {
        console.error("Parent container \".profile_rightcol\" not found");
    }
}