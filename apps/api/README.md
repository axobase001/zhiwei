# apps/api

Serverless API adapter for serving Paper IR examples and benchmark outputs.

Vercel currently still uses the root `api/` directory as compatibility entrypoints. The source layout is mirrored here so the repository has a monorepo shape while the deployed preview remains stable.

Future work: make `apps/api` the only API source and generate deployment adapters from it.
