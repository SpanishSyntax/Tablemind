# Stage 1: Build
FROM node:20-slim AS builder
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
RUN corepack enable # Faster way to get pnpm in Node 20

WORKDIR /app

# Only copy lockfile and package.json first for layer caching
COPY ./Frontend/tablemind/package.json ./Frontend/tablemind/pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

# IMPORTANT: Ensure you have a .dockerignore with 'node_modules' 
# to prevent the next line from crashing
COPY ./Frontend/tablemind ./
RUN pnpm build

# Stage 2: Run (using a smaller image)
FROM node:20-slim AS runner
WORKDIR /app
ENV NODE_ENV=production

# The standalone folder includes a minimal node_modules
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

EXPOSE 3000
ENV PORT=3000
# Next.js standalone uses 'hostname' by default; 0.0.0.0 is needed for Docker
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]
