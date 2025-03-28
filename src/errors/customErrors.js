class SonificationError extends Error {
  constructor(message, statusCode = 500) {
    super(message);
    this.name = this.constructor.name;
    this.statusCode = statusCode;
  }
}

class ValidationError extends SonificationError {
  constructor(message) {
    super(message, 400);
  }
}

class AudioProcessingError extends SonificationError {
  constructor(message) {
    super(message, 500);
  }
}

module.exports = {
  SonificationError,
  ValidationError,
  AudioProcessingError,
};
