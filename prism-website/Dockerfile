# Use official Bun image
FROM oven/bun:1 AS base
WORKDIR /usr/src/app

# Copy and install dependencies
FROM base AS install
COPY package.json bun.lock ./
RUN bun install --frozen-lockfile
RUN bun next telemetry disable

# Copy the entire project and build
FROM base AS build
COPY --from=install /usr/src/app/node_modules ./node_modules
COPY . .
RUN mkdir -p .next && chown -R bun:bun .next

RUN bun run build
RUN bun add -d @swc/cli @swc/core
RUN mkdir -p /usr/src/app/.next && chown -R bun:bun /usr/src/app/.next

# Final image for running the app
FROM base AS release
COPY --from=install /usr/src/app/node_modules ./node_modules
COPY --from=build /usr/src/app/.next ./.next
COPY --from=build /usr/src/app/public ./public
COPY --from=build /usr/src/app/src ./src
COPY package.json bun.lock ./

USER bun
ENTRYPOINT ["bun", "run", "build"]
