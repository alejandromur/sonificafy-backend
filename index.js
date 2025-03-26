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
  const LIMIT = 300;

  function getSlice(string) {
    if (string.length <= LIMIT) return string;

    const indexStart = Math.ceil((string.length - LIMIT) / 2);
    return string.slice(indexStart, indexStart + LIMIT);
  }

  function assignName(url, startTime) {
    const originUrlName = url.substring(
      url.indexOf("://") + 3,
      url.indexOf(".")
    );
    const time = startTime.getTime();
    return `${originUrlName}.wav`;
    return `${originUrlName}_${time}.wav`;
  }

  try {
    const { url } = req.body;
    if (!url) return res.status(400).json({ error: "An URL is required" });

    const startTime = new Date();
    const response = await axios.get(url);
    const html = getSlice(response.data);
    console.log(response.data.length, html.length, html);

    const fileName = assignName(url, startTime);

    fs.writeFileSync("temp.html", html);

    exec(
      `${pythonPath} ${path.join(
        __dirname,
        "scripts/html_to_sound_trigrams.py"
      )} ${path.join(__dirname, "temp.html")} ${path.join(
        __dirname,
        fileName
      )} lofi`,
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

        const metadata = {
          audioUrl: fileName,
          processingInfo: {
            timestamp: startTime,
            processingTime: `${new Date() - startTime}ms`,
            originalUrl: url,
            originalContentLength: response.data.length,
            processedContentLength: html.length,
            contentType: response.headers["content-type"],
            statusCode: response.status,
            fileName: fileName,
          },
        };

        res.json(metadata);
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
