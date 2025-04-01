FROM oven/bun:latest
COPY . ./
RUN bun add -d @swc/cli @swc/core
RUN bun install --frozen-lockfile
RUN bun run build
ENTRYPOINT ["bun", "run", "start"]
