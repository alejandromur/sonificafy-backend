const path = require("path");
const express = require("express");
const axios = require("axios");
const { exec } = require("child_process");
const fs = require("fs");
const app = express();

app.use(express.json());

const pythonPath =
  "/usr/local/Caskroom/miniforge/base/envs/sonificafy/bin/python";

app.get("/", (req, res) => {
  res.send("<h1>Hello World</h1>");
});

app.post("/api/sonificate", async (req, res) => {
  try {
    const { url } = req.body;
    if (!url) return res.status(400).json({ error: "An URL is required" });

    const response = await axios.get(url);
    const html = response.data.slice(0, 100); // TODO: Strip the html to the first 234 characters

    fs.writeFileSync("temp.html", html);

    // const pythonPath = "/usr/local/bin/python3";

    exec(
      `${pythonPath} ${path.join(
        __dirname,
        "html_to_sound_piano_style.py"
      )} ${path.join(__dirname, "temp.html")} ${path.join(
        __dirname,
        "output.wav"
      )}`,
      {
        env: process.env,
        cwd: __dirname,
      },
      (error, stdout, stderr) => {
        if (error) {
          console.error(`Error: ${error.message}`);
          console.error(`stderr: ${stderr}`);
          return res.status(500).json({ error: "Error in processing" });
        }
        if (stderr) {
          console.warn(`Warning: ${stderr}`);
        }
        console.log(`stdout: ${stdout}`);

        res.json({ audioUrl: "output.wav" });
      }
    );
  } catch (err) {
    console.error("Error completo:", err);
    res.status(500).json({ error: "Error in processing the URL" });
  }
});

app.listen(3000, () => {
  console.log("Server is running on port 3000");
});
