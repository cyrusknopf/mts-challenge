FROM oven/bun:latest
COPY . ./
RUN bun add -d @swc/cli @swc/core
RUN bun install --frozen-lockfile
ENTRYPOINT ["bun", "run", "dev"]
