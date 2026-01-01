FROM python:3.11-slim

LABEL maintainer="lvbibir"
LABEL description="JetBrainsLxgwNerdMono Font Builder"

WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

# Copy project files
COPY pyproject.toml .
COPY src/ src/
COPY build.py .

# Install dependencies
RUN uv sync --no-dev

# Create mount points
VOLUME /app/fonts
VOLUME /app/output

# Default entrypoint
ENTRYPOINT ["uv", "run", "python", "build.py", "--fonts-dir", "/app/fonts", "--output-dir", "/app/output"]

# Default command (can be overridden)
CMD []
