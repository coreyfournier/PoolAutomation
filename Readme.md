#Authentication
I used Synology Application proxy to manage HTTPS and configured it to point to localhost 8081.
I then used an LDAP reverse proxy container using: https://hub.docker.com/r/dariko/httpd-rproxy-ldap/

docker run -p 80:80 -e LDAP_URI="ldap://nas.myfournier.com/dc=myfournier,dc=com?uid?sub?(objectClass=*)" -e PROXY_URI="http://raspberrypi.myfournier.com:8080/" -e LISTEN_PORT=80 -e SERVERNAME=localhost dariko/httpd-rproxy-ldap

Set the following configuration for the container:
Set resource limitation to 256MB
Went to advanced settings
 Enabled auto-restart
 Network left in bridge mode
 Port Settings - Container port 8081
 Environment
    LDAP_URI=ldap://{DomainName.com}/dc={DomainName},dc=com?uid?sub?(objectClass=*)PROXY_URI=http://{YourPi}:8080/
    LISTEN_PORT=8081
    SERVERNAME={YouNasServerName}
    