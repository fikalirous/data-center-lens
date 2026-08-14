VisQuill Lens Export
====================
visquill.com | © 2026 Dr. Benjamin Niedermann
Free to use with attribution. White-label: contact@visquill.com
Licence: visquill.com/licence

Files
-----
  index.html   Main page — open in a browser (requires a server, see below)
  viewer.js    Viewer bundle — do not modify
  data.json    Your data — can be updated independently of the viewer
  map.json  Map configuration — edit tileUrl/attribution to change the map

Running locally
---------------
Python:   cd visquill-export && python3 -m http.server 8080
          Open http://localhost:8080

Node.js:  cd visquill-export && npx serve .
          Open http://localhost:3000

Deploying
---------
  Netlify:      netlify.com/drop — drag and drop this folder
  GitHub Pages: push to a repo and enable Pages in Settings

Embedding
---------
  <iframe src="https://your-host.com/visquill-export/"
          width="800" height="600" frameborder="0"></iframe>

Note: This folder requires a web server. It cannot be opened directly
from disk (file://) due to browser security restrictions.
