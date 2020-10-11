mkdir -p ~/.streamlit/

echo "\
[server]\n\
port = $PORT\n\
enableCORS = false\n\
headless = true\n\
\n\
" > ~/.streamlit/config.toml

curl -c /tmp/cookies "https://drive.google.com/uc?export=download&id=1vztBL9WwUh1vjXOjSfPVgnUTpqdFEcKY" > /tmp/intermezzo.html
curl -L -b /tmp/cookies "https://drive.google.com$(cat /tmp/intermezzo.html | grep -Po 'uc-download-link" [^>]* href="\K[^"]*' | sed 's/\&amp;/\&/g')" > pth/bert_w0.pth.tar

#python -m spacy download en_core_web_sm
