const sonificationService = require("../services/sonficationService");
const { getSlice, assignName } = require("../utils/sonificationUtils");

async function processSonification(req, res, next) {
  try {
    const startTime = new Date();

    const response = await sonificationService.validateAndFetchUrl(
      req.body.url
    );
    const scriptVariant = req.body.scriptVariant;

    const html = getSlice(response.data);
    const fileName = assignName(req.body.url, startTime);

    await sonificationService.processAudio(html, scriptVariant, fileName);

    const metadata = sonificationService.createMetadata(
      req.body.url,
      response,
      html,
      fileName,
      startTime
    );

    res.json(metadata);
  } catch (error) {
    next(error);
  }
}

module.exports = {
  processSonification,
};
