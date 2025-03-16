import express from 'express';
import http from 'http';
import cors from 'cors';
import bodyParser from 'body-parser';
import { Ollama } from 'ollama';

const app = express();
const ollama = new Ollama({ host: 'localhost:11434' });

app.use(cors({origin: 'http://localhost:8502'}));
// app.use(bodyParser.urlencoded({ extended: true }));
// app.use(bodyParser.json());
app.use(express.json());

const server = http.createServer(app);

server.listen(5000, () => {
  console.log("Server running on port 5000");
});

app.post("/ollama", async (req, res) => {
  console.log("HERE");
  const { message } = req.body;

  const response = await ollama.chat({
    model: 'llama3.1',
    messages: [{ role: 'user', content: message }]
  });

  res.json(response);
});
