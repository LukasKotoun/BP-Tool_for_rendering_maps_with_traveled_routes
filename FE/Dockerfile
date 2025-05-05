# Dockerfile for the frontend
# author: Lukáš Kotoun, xkotou08
FROM node:lts-alpine
RUN corepack enable
WORKDIR /app

COPY package.json pnpm-lock.yaml ./

RUN pnpm install --frozen-lockfile

COPY . .

RUN pnpm run build
CMD ["pnpm", "preview", "--host"]
EXPOSE 4173