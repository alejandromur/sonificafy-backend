const path = require("path");

function getAudioFile(req, res) {
  const { filename } = req.params;
  res.sendFile(path.join(__dirname, "../../audios", filename));
}

module.exports = {
  getAudioFile,
};
