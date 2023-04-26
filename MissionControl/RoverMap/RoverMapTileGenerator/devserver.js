const express = require('express');
const { existsSync } = require('fs');
const app = express()
const port = 3000

app.get('/', (req, res) => {
  res.sendFile("index.html", {
      root: "./"
  });
})


app.get("/tiles/:z/:x/:y", (req, res) => {
    if(existsSync(`./tiles/z${req.params.z}, x${req.params.x}, y${req.params.y}.jpg`)){
        res.sendFile(`z${req.params.z}, x${req.params.x}, y${req.params.y}.jpg`, {
            root: "./tiles/"
        })
    } else{
        res.send(400)
    }
    console.log(req.params.z, req.params.x, req.params.y);
})


app.listen(port, () => {
  console.log(`Example app listening on port ${port}`)
})