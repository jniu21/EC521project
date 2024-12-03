/* 
Prefix/Suffix: Used dashes in domain names
Subdomains: Included multiple subdomains
Port: Added URLs with non-standard ports (8080)
HTTPS token: Mixed HTTP/HTTPS usage
Request URL: Added external resource requests
Anchor URL: Included multiple external domain links
Links in Tags: Added images and resources from different domains

*/

const express = require('express');
const app = express();
const port = 3001;

app.use(express.static('public'));

app.get('/', (req, res) => {
    res.send(`
<!DOCTYPE html>
<html>
<head>
    <title>Login Portal - Security Check</title>
    <link rel="icon" href="http://198.51.100.1/favicon.ico">
    <style>
        body { font-family: Arial; padding: 20px; }
        .container { max-width: 400px; margin: auto; }
        .warning { background: #ffebee; padding: 10px; margin: 10px 0; }
        input { width: 100%; margin: 10px 0; padding: 8px; }
    </style>
</head>
<body>
    <div class="warning">
        TEST SPECIMEN - FOR PHISHING DETECTION RESEARCH ONLY
    </div>
    
    <div class="container">
        <a href="http://192.168.1.1/login.php">Home</a> |
        <a href="http://user@192.168.1.2/account">Account</a> |
        <a href="http://legitsite.com//redirect//http://suspicious.com">Services</a>
        
        <form action="http://login.secure.service.suspicious-site.com:8080/process.php">
            <h2>Verify Your Account</h2>
            
            <img src="http://different-domain.com/logo.png" alt="Logo">
            <link href="http://another-domain.com/style.css" rel="stylesheet">
            
            <div>
                <a href="http://external-domain1.com">Terms</a>
                <a href="http://external-domain2.com">Privacy</a>
                <a href="http://external-domain3.com">Support</a>
            </div>
            
            <input type="text" placeholder="Username">
            <input type="password" placeholder="Password">
            
            <p>Forgot password? <a href="http://bit.ly/suspicious">Click here</a></p>
            
            <input type="submit" value="Login" formaction="http://suspicious-login-portal.com">
        </form>
        
        <script src="http://external-script.com/script.js"></script>
        <link rel="stylesheet" href="http://external-style.com/style.css">
        
        <iframe src="http://suspicious-site.com:8080/frame.html"></iframe>
    </div>
</body>
</html>
    `);
});

app.listen(port, () => {
    console.log(`Test server running at http://localhost:${port}`);
});