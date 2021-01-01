mkdir -p ~/.streamlit/
echo “\
[general]\n\
email = \”<ian.yu@arc.com.co>\”\n\
“ > ~/.streamlit/credentials.toml
echo “\
[server]\n\
headless = true\n\
enableCORS=false\n\
process.env.PORT
“ > ~/.streamlit/config.toml