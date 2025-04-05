require("dotenv").config();
const path = require("path");
const fs = require("fs").promises;
const fsSync = require("fs");
const { exec } = require("child_process");
const util = require("util");
const execPromise = util.promisify(exec);

const LIMIT = parseInt(process.env.LIMIT, 10);
const AUDIO_FILES_DIR = path.join(__dirname, "../../audios");
const MAX_FILE_AGE_MS = 24 * 60 * 60 * 1000; // 24 hours
let cleanupInProgress = false;

async function cleanOldAudioFiles() {
  if (cleanupInProgress || process.env.ENVIRONMENT !== "PRODUCTION") return;

  try {
    cleanupInProgress = true;
    const files = await fs.readdir(AUDIO_FILES_DIR);
    const now = Date.now();

    const deletePromises = files.map(async (file) => {
      try {
        const filePath = path.join(AUDIO_FILES_DIR, file);
        const stats = await fs.stat(filePath);
        const fileAge = now - stats.mtimeMs;

        if (fileAge > MAX_FILE_AGE_MS) {
          await fs.unlink(filePath);
          console.log(`Deleted old audio file: ${file}`);
        }
      } catch (err) {
        console.error(`Error processing file ${file}:`, err);
      }
    });

    await Promise.all(deletePromises);
  } catch (err) {
    console.error("Error during cleanup:", err);
  } finally {
    cleanupInProgress = false;
  }
}

function getSlice(string) {
  if (string.length <= LIMIT) return string;

  const indexStart = Math.ceil((string.length - LIMIT) / 2);
  return string.slice(indexStart, indexStart + LIMIT);
}

function assignName(url, startTime) {
  if (!url) return null;

  const originUrlName = new URL(url).hostname;

  const time = startTime.getTime();
  return process.env.ENVIRONMENT === "PRODUCTION"
    ? `${originUrlName}_${time}.wav`
    : `${originUrlName}.wav`;
}

async function generateSoundFromHTML(
  htmlContent,
  scriptVariant,
  outputFileName
) {
  fsSync.writeFileSync("src/temp.html", htmlContent);

  const scriptPath = path.join(__dirname, `../../scripts/${scriptVariant}.py`);
  const outputPath = path.join(__dirname, "../../audios", outputFileName);

  cleanOldAudioFiles().catch((err) =>
    console.error("Background cleanup failed:", err)
  );

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
