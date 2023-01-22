# Pool Automation

## Authentication
No security is provided, but I used my synology nas to help me out here. I already have a certificate installed on it. The NAS also provides an option for reverse proxy, but it doesn't include authentication. I found a docker container project that provides the LDAP authentication. With the two, i piped traffice from one proxy to another. I could just use the Docker container, but then I would have to manage the cert in two places. This is a set it and forget it solution.

### Synology Reverse Proxy
I used Synology Application proxy to manage HTTPS and configured it to point to it's self 8081.
You can read about how to configure it here: https://mariushosting.com/synology-how-to-use-reverse-proxy/
* Source
** protocol HTTPS
** hostname: {YouNasServerName}
** Port: {Port you want to expose on the server}
* Destination
** Protocol: HTTP
** Hostname: {YouNasServerName}
** Port: {The port number you are going to use in the container}

### Docker Container in Synology for LDAP authentication
reverse proxy container using: https://hub.docker.com/r/dariko/httpd-rproxy-ldap/

Set the following configuration for the container:
* Initial screen
** Set resource limitation to 256MB
* Go to advanced settings
** Enabled auto-restart
** Network - choose "Use the same network as Docker Host"
** Port Settings - Container port 8081
** Environment
*** LDAP_URI=ldap://{DomainName.com}/dc={DomainName},dc=com?uid?sub?(objectClass=*)
*** PROXY_URI=http://{YourPi}:8080/
*** LISTEN_PORT=8081
*** SERVERNAME={YouNasServerName}    