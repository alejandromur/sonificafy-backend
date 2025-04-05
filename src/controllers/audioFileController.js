const path = require("path");

function getAudioFile(req, res) {
  const { filename } = req.params;

  // Configure headers to prevent caching
  res.set({
    "Cache-Control": "no-store, no-cache, must-revalidate, proxy-revalidate",
    Pragma: "no-cache",
    Expires: "0",
  });

  res.sendFile(path.join(__dirname, "../../audios", filename));
}

module.exports = {
  getAudioFile,
};
