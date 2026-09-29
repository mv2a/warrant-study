# Builder image for the Warrant study: Claude Code plus Python 3, run as an unprivileged user.
# The image contains no task material; each run mounts only its own workspace at /work.
FROM node:22-slim
RUN apt-get update && apt-get install -y --no-install-recommends python3 ca-certificates && rm -rf /var/lib/apt/lists/*
ARG CLAUDE_CODE_VERSION=2.1.252
RUN npm install -g @anthropic-ai/claude-code@${CLAUDE_CODE_VERSION} && npm cache clean --force
RUN useradd -m -u 1500 builder && mkdir -p /work && chown builder /work
USER builder
WORKDIR /work
