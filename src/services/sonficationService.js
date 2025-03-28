const axios = require("axios");
const {
  ValidationError,
  AudioProcessingError,
} = require("../errors/customErrors");
const { generateSoundFromHTML } = require("../utils/sonificationUtils");

class SonificationService {
  async validateAndFetchUrl(url) {
    if (!url) {
      throw new ValidationError("No URL provided");
    }

    try {
      const response = await axios.get(url);
      return response;
    } catch (error) {
      throw new ValidationError(
        `Error when downloading the URL: ${error.message}`
      );
    }
  }

  async processAudio(html, fileName) {
    try {
      const result = await generateSoundFromHTML(html, fileName);
      return result;
    } catch (error) {
      throw new AudioProcessingError(
        `Error when processing the audio: ${error.message}`
      );
    }
  }

  createMetadata(url, response, html, fileName, startTime) {
    return {
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
  }
}

module.exports = new SonificationService();
