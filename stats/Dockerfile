FROM node:18.16-alpine3.18 as builder

WORKDIR /app

COPY package*.json ./

RUN --mount=type=cache,target=/app/.npm \
    npm set cache /app/.npm && \
    npm ci

COPY public ./public
COPY src ./src

RUN npm run build

CMD ["npm", "start"]
