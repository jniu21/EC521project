require('dotenv').config();

const dns = require('dns');
const whois = require('whois');
const axios = require('axios');
const { URL } = require('url');
const puppeteer = require('puppeteer');

async function isFaviconExternal(url) {
    try {
        const parsedUrl = new URL(url);
        const hostname = parsedUrl.hostname;
        const faviconUrl = `${parsedUrl.origin}/favicon.ico`; //pretty much guessing where its gonna be (will often return 404)

        const response = await axios.get(faviconUrl, { maxRedirects: 5 });
        const faviconDomain = new URL(response.config.url).hostname;

        return faviconDomain !== hostname ? 1 : 0;
    } catch (error) {
        console.error("Error fetching favicon:", error.message);
        return 1; //just assume worst case (external)
    }
}

async function scrapePage(url) {
    const browser = await puppeteer.launch({headless: true}); //headless = no GUI 
    const page = await browser.newPage();

    try {
        await page.goto(url, { waitUntil: 'networkidle2' });

        //look for anchors
        const links = await page.$$eval('a', anchors =>
            anchors.map(anchor => anchor.href)
        );

        //look for links
        const linkTags = await page.$$eval('link', links =>
            links.map(link => link.href)
        );

        return { links, linkTags };
    } catch (error) {
        console.error("Error scraping page:", error.message);
        return { links: [], linkTags: [] };
    } finally {
        await browser.close();
    }
}

async function calculateRatios(url) {
    const {links, linkTags} = await scrapePage(url);
    const parsedUrl = new URL(url);
    const hostname = parsedUrl.hostname;

    //request URL ratio
    const totalLinks = links.length;
    const externalLinks = links.filter(link => {
        try {
            const linkHostname = new URL(link).hostname;
            return linkHostname !== hostname && linkHostname !== "";
        } catch {
            return false; 
        }
    }).length;
    const requestUrlRatio = totalLinks > 0 ? Math.round((externalLinks / totalLinks) * 100) : 0;

    //anchor URL ratio
    const unsafeLinks = links.filter(link =>
        link.startsWith('#') || link.startsWith('javascript') || link.startsWith('mailto')
    ).length;
            //NOTE: toFixed() will produce a STRING representation of the float, so will need to convert afterwards 
    const anchorUrlRatio = totalLinks > 0 ? (unsafeLinks / totalLinks).toFixed(2) : 0; 

    //links in tags ratio
    const internalLinks = linkTags.filter(tag => {
        try {
            const tagHostname = new URL(tag).hostname;
            return tagHostname === hostname;
        } catch {
            return false; 
        }
    }).length;
        //see note above about toFixed()
    const linksInTagsRatio = linkTags.length > 0 ? (internalLinks / linkTags.length).toFixed(2) : 0;

    return {requestUrlRatio, anchorUrlRatio, linksInTagsRatio};
}

async function isGoogleIndexed(url, apiKey, searchEngineId) {
    try {
        
        const apiEndpoint = `https://customsearch.googleapis.com/customsearch/v1`;
        const response = await axios.get(apiEndpoint, {
            params: {key: apiKey, cx: searchEngineId, q: `site:${url}`, num: 1 
            }
        });
        return response.data.items && response.data.items.length > 0 ? 1 : 0;
    } catch (error) {
        if (error.response && error.response.status === 404) {
            return 0;
        }
        console.error("Error checking Google index:", error.message);
        return 0; 
    }
}

async function getPageRank(url, apiKey) {
    try {
        const apiEndpoint = "https://openpagerank.com/api/v1.0/getPageRank";

        const response = await axios.get(apiEndpoint, {
            headers: {"API-OPR": apiKey},
            params: {domains: [url]} //important: singular urls still need to be placed into an array
        });
        if (response.data && response.data.response && response.data.response[0]) {
            const rank = response.data.response[0].page_rank_decimal;
            return rank !== null ? rank : 0; 
        } else {
            return 0; 
        }
    } catch (error) {
        console.error("Error fetching PageRank:", error.message);
        return 0; 
    }
}

async function extractURLFeatures(url) {
    try {
        const parsedUrl = new URL(url);
        const hostname = parsedUrl.hostname;
        //const path = parsedUrl.pathname;

        const urlLength = url.length;
        //console.log(urlLength);
        const hasHttps = parsedUrl.protocol === "https:" ? 1 : 0;
        
        const ipAddressRegex = /^(?:\d{1,3}\.){3}\d{1,3}$|^(0x[0-9A-Fa-f]+)(\.|$)/;
        const hasIPAddress = ipAddressRegex.test(hostname) ? 1 : 0; //there is an easier way to do this but regex is more robust
        
        const shorteningServices = ["bit.ly", "tinyurl.com", "goo.gl", "ow.ly", "is.gd", "buff.ly", "adf.ly"];
        const isShortenedURL = shorteningServices.some(service => hostname.includes(service)) ? 1 : 0;
        
        const hasAtSymbol = url.includes('@') ? 1 : 0;
        
        const doubleSlashIndex = url.indexOf("//", 8); //ideally this skips the protocol part but might need to tweak
        const hasDoubleSlashRedirecting = doubleSlashIndex > 7 ? 1 : 0;
        
        const hasDash = hostname.includes('-') ? 1 : 0;
        
        const domainParts = hostname.replace(/^www\./, '').split('.');
        const subDomainCount = domainParts.length - 2;
        //const hasSubDomain = subDomainCount;

        const hasPort = parsedUrl.port ? 1 : 0;
        //easy code ends here
        
        //NOTE: these are grouped together because they all require HTML parsing
        const {requestUrlRatio, anchorUrlRatio, linksInTagsRatio} = await calculateRatios(url);

        const faviconExternal = await isFaviconExternal(url);

        let domainInfo = {Domain_Registration_Length: 0, 
                          Domain_age: 0,
                          Abnormal_URL: 1
        };
        whois.lookup(hostname, (err, data) => {
            if (!err) {
                const expirationDate = parseExpDate(data);
                //console.log("Expiration Date", expirationDate); 
                const creationDate = parseCreatDate(data);
                domainInfo = {
                    Domain_Registration_Length: calculateYears(expirationDate, creationDate), //lots of nulls !!
                    Domain_age: calculateDays(creationDate),
                    Abnormal_URL: creationDate ? 1 : 0
                };
            }
        });

        let hasDNSRecord = 0;
        dns.lookup(hostname, (err) => {
            hasDNSRecord = err ? 0 : 1;
        });

        //const websiteTraffic = "------"; //similarweb or ahrefs?

        const pageRankAPIKey = `${process.env.PAGE_RANK_API_KEY}`;
        const pageRank = await getPageRank(url, pageRankAPIKey);

        const googleAPIKey = `${process.env.GOOGLE_API_KEY}`;
        const searchEngineId = `${process.env.searchEngineId}`;
        const isIndexed = await isGoogleIndexed(url, googleAPIKey, searchEngineId);

        return { //you can/should redo the naming because its mildly inconvenient
            URL_Length: urlLength,
            having_HTTPS: hasHttps,
            having_IP_Address: hasIPAddress,
            Shortening_Service: isShortenedURL,
            having_At_Symbol: hasAtSymbol,
            Double_slash_redirecting: hasDoubleSlashRedirecting,
            Prefix_Suffix: hasDash,
            Sub_Domain_Count: subDomainCount,
            Domain_Registration_Length: domainInfo.Domain_Registration_Length,
            Favicon: faviconExternal,
            Port: hasPort,
            Request_URL: requestUrlRatio,
            Anchor_URL: anchorUrlRatio,
            Links_in_Tags: linksInTagsRatio,
            Abnormal_URL: domainInfo.Abnormal_URL,
            Domain_age: domainInfo.Domain_age,
            DNS_record: hasDNSRecord,
            //Website_traffic: websiteTraffic,
            Page_rank: pageRank,
            Google_Index: isIndexed
        };
    } catch (error) { //being extra safe
        console.error("Invalid URL:", error);
        
        return { 
        URL_Length: 100,
        having_HTTPS: 1,
        having_IP_Address: 1,
        Shortening_Service: 1,
        having_At_Symbol: 1,
        Double_slash_redirecting: 1,
        Prefix_Suffix: 1,
        Sub_Domain_Count: 2,
        Domain_Registration_Length: 1,
        Favicon: 1,
        Port: 1,
        Request_URL: 100,
        Anchor_URL: 1.0,
        Links_in_Tags: 1.0,
        Abnormal_URL: 1,
        Domain_age: 0,
        DNS_record: 0,
        //Website_traffic: 0,
        Page_rank: -1,
        Google_Index: 0};
    }
}

//these are helpers for date conversions - credit to chat...
function parseExpDate(data) {
    const match = data.match(/Expiry Date:\s*(.*)/i);
    return match ? new Date(match[1]) : null;
}
function parseCreatDate(data) {
    const match = data.match(/Creation Date:\s*(.*)/i);
    return match ? new Date(match[1]) : null;
}
function calculateYears(expirationDate, creationDate) {
    if (expirationDate && creationDate) {
        return ((expirationDate - creationDate) / (1000 * 60 * 60 * 24 * 365)).toFixed(2);
    }
    return null;
}
function calculateDays(creationDate) {
    if (creationDate) {
        return Math.floor((Date.now() - creationDate) / (1000 * 60 * 60 * 24));
    }
    return null;
}

module.exports = {
    extractURLFeatures
};

// (async () => { //needs to be async otherwise you're just gonna get Promises returned
//     var start = Date.now();
//     const url = "https://www.google.com/";
//     try {
//         const features = await extractURLFeatures(url);
//         console.log("Extraction Time (ms):", Date.now()-start);
//         console.log("Extracted Features:", features);
//     } catch (error) {
//         console.error("Error extracting features:", error);
//     }
// })();
