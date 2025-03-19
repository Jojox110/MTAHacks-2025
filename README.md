# FilmBuddy

**MTAHacks 2025 winner!**

A friendly chat-bot that will recommnend you the perfect movie to watch on your day off!

## QuickStart

- Create a virtual enviornment using conda with python 3.10 <br>
`conda create -n <name> python=3.10` <br>
`conda activate <name>`
- Install Ollama <br>
`curl -fsSL https://ollama.com/install.sh | sh`
- Pull llama-3.1-8b <br>
`ollama pull meta/llama3:8b`
- Install some requirements using conda <br>
`conda install -c conda-forge libgcc-ng` <br>
`conda install -c pytorch -c nvidia faiss-gpu`
- Install python dependencies <br>
`pip install -r requirements.txt`
- Install npm dependencies <br>
`npm i`
- Start the Ollama service <br>
`sudo systemctl start ollama`
- Run the project <br>
`npm run dev`  

## License

This project is licensed under the Apache License 2.0. Please note that some components were adapted from Vercel's open source AI Chatbot project.
