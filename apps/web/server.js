const fs = require("fs");
const http = require("http");
const path = require("path");
const { URL } = require("url");

const ROOT = path.join(__dirname, "..", "..");
const STATIC_DIR = path.join(__dirname, "static");
const API_DIR = path.join(ROOT, "api");
const HOST = process.env.ZHIWEI_HOST || "127.0.0.1";
const PORT = Number(process.env.ZHIWEI_PORT || 8765);

const mimeTypes = {
  ".html": "text/html; charset=utf-8",
  ".js": "application/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".svg": "image/svg+xml; charset=utf-8",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg"
};

function send(res, status, body, headers = {}) {
  res.writeHead(status, headers);
  res.end(body);
}

function createApiResponse(res) {
  return {
    status(code) {
      res.statusCode = code;
      return this;
    },
    setHeader(name, value) {
      res.setHeader(name, value);
      return this;
    },
    json(payload) {
      if (!res.getHeader("Content-Type")) {
        res.setHeader("Content-Type", "application/json; charset=utf-8");
      }
      res.end(JSON.stringify(payload));
    },
    send(payload) {
      res.end(payload);
    },
    end(payload) {
      res.end(payload);
    }
  };
}

function loadHandler(relativePath) {
  return require(path.join(API_DIR, relativePath));
}

function matchApi(pathname) {
  if (pathname === "/api/health") return { file: "health.js", query: {} };
  if (pathname === "/api/papers") return { file: "papers.js", query: {} };

  const parts = pathname.split("/").filter(Boolean);
  if (parts[0] !== "api" || parts[1] !== "papers" || !parts[2]) return null;

  const paperId = decodeURIComponent(parts[2]);
  if (parts.length === 3) return { file: path.join("papers", "[paperId].js"), query: { paperId } };
  if (parts[3] === "anchors") return { file: path.join("papers", "[paperId]", "anchors.js"), query: { paperId } };
  if (parts[3] === "blocks") return { file: path.join("papers", "[paperId]", "blocks.js"), query: { paperId } };
  if (parts[3] === "corrections") return { file: path.join("papers", "[paperId]", "corrections.js"), query: { paperId } };
  if (parts[3] === "ir") return { file: path.join("papers", "[paperId]", "ir.js"), query: { paperId } };
  if (parts[3] === "pdf") return { file: path.join("papers", "[paperId]", "pdf.js"), query: { paperId } };
  if (parts[3] === "reparse") return { file: path.join("papers", "[paperId]", "reparse.js"), query: { paperId } };
  if (parts[3] === "export" && parts[4]) {
    return {
      file: path.join("papers", "[paperId]", "export", "[kind].js"),
      query: { paperId, kind: decodeURIComponent(parts[4]) }
    };
  }

  return null;
}

function serveStatic(pathname, res) {
  const requestPath = pathname === "/" ? "/index.html" : pathname.replace(/^\/static\//, "/");
  const resolved = path.resolve(STATIC_DIR, `.${requestPath}`);
  if (!resolved.startsWith(path.resolve(STATIC_DIR))) {
    send(res, 403, "forbidden");
    return;
  }
  if (!fs.existsSync(resolved) || fs.statSync(resolved).isDirectory()) {
    send(res, 404, "not found");
    return;
  }
  const type = mimeTypes[path.extname(resolved).toLowerCase()] || "application/octet-stream";
  send(res, 200, fs.readFileSync(resolved), { "Content-Type": type });
}

const server = http.createServer((req, res) => {
  const url = new URL(req.url, `http://${req.headers.host || `${HOST}:${PORT}`}`);
  const route = matchApi(url.pathname);

  if (route) {
    try {
      req.query = Object.fromEntries(url.searchParams.entries());
      req.query = { ...req.query, ...route.query };
      loadHandler(route.file)(req, createApiResponse(res));
    } catch (error) {
      send(res, 500, JSON.stringify({ error: error.message }), {
        "Content-Type": "application/json; charset=utf-8"
      });
    }
    return;
  }

  if (url.pathname === "/" || url.pathname.startsWith("/static/")) {
    serveStatic(url.pathname, res);
    return;
  }

  serveStatic("/index.html", res);
});

server.listen(PORT, HOST, () => {
  console.log(`知微 dev server: http://${HOST}:${PORT}`);
});
