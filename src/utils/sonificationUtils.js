require("dotenv").config();
const path = require("path");
const fs = require("fs");
const { exec } = require("child_process");
const util = require("util");
const execPromise = util.promisify(exec);

const LIMIT = parseInt(process.env.LIMIT, 10);

function getSlice(string) {
  if (string.length <= LIMIT) return string;

  const indexStart = Math.ceil((string.length - LIMIT) / 2);
  return string.slice(indexStart, indexStart + LIMIT);
}

function assignName(url, startTime) {
  const originUrlName = url.substring(url.indexOf("://") + 3, url.indexOf("."));
  const time = startTime.getTime();
  return process.env.ENVIRONMENT === "PRODUCTION"
    ? `${originUrlName}_${time}.wav`
    : `${originUrlName}.wav`;
}

async function generateSoundFromHTML(htmlContent, outputFileName) {
  fs.writeFileSync("src/temp.html", htmlContent);

  const scriptPath = path.join(
    __dirname,
    "../../scripts/john_frusciante_inspiration.py"
  );
  const outputPath = path.join(__dirname, "../../audios", outputFileName);

  const { stdout, stderr } = await execPromise(
    `${process.env.PYTHON_PATH} ${scriptPath} ${path.join(
      __dirname,
      "../temp.html"
    )} ${outputPath}`,
    {
      env: process.env,
      cwd: path.join(__dirname, "../../"),
    }
  );

  if (stderr) {
    console.warn(`Warning: ${stderr}`);
  }

  return stdout;
}

module.exports = {
  getSlice,
  assignName,
  generateSoundFromHTML,
};
