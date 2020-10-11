mkdir -p ~/.streamlit/

echo "\
[server]\n\
port = $PORT\n\
enableCORS = false\n\
headless = true\n\
\n\
" > ~/.streamlit/config.toml

# curl -c /tmp/cookies "https://drive.google.com/uc?export=download&id=1vztBL9WwUh1vjXOjSfPVgnUTpqdFEcKY" > /tmp/intermezzo.html
# curl -L -b /tmp/cookies "https://drive.google.com$(cat /tmp/intermezzo.html | grep -Po 'uc-download-link" [^>]* href="\K[^"]*' | sed 's/\&amp;/\&/g')" > pth.zip
# unzip pth.zip

curl -c /tmp/cookies "https://drive.google.com/uc?export=download&id=1d78CyW664EE6iS438ylSMiJgIUwIiagG" > /tmp/intermezzo.html
curl -L -b /tmp/cookies "https://drive.google.com$(cat /tmp/intermezzo.html | grep -Po 'uc-download-link" [^>]* href="\K[^"]*' | sed 's/\&amp;/\&/g')" > fld.zip
unzip fld.zip
