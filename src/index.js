const express = require("express");
const cors = require("cors");
const errorHandler = require("./middleware/errorHandler");
const { processSonification } = require("./controllers/sonificationController");
const { getAudioFile } = require("./controllers/audioFileController");

const app = express();

app.use(cors());
app.use(express.json());

app.post("/api/sonification", processSonification);
app.get("/api/audio/:filename", getAudioFile);

app.use(errorHandler);

app.listen(3000, () => {
  console.log("Server is running on port 3000");
});
