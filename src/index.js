const express = require("express");
const errorHandler = require("./middleware/errorHandler");
const { processSonification } = require("./controllers/sonificationController");

const app = express();

app.use(express.json());

app.post("/api/sonificate", processSonification);

app.use(errorHandler);

app.listen(3000, () => {
  console.log("Server is running on port 3000");
});
