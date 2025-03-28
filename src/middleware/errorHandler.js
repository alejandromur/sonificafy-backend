const { SonificationError } = require("../errors/customErrors");

function errorHandler(err, req, res, next) {
  console.error("Error:", err);

  if (err instanceof SonificationError) {
    return res.status(err.statusCode).json({
      error: err.message,
    });
  }

  return res.status(500).json({
    error: "Internal server error",
  });
}

module.exports = errorHandler;
