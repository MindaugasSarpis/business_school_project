FROM python:3.12-bullseye

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PATH="/root/.local/bin/:$PATH"

WORKDIR /app
COPY . .

# Install uv
RUN curl -LsSf https://astral.sh/uv/0.6.2/install.sh | sh

# Install dependencies
RUN uv sync
RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]