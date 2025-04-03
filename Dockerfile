FROM ubuntu:latest

# for uv
ENV PATH=/root/.local/bin:$PATH

# for uvicorn
ENV PATH=/app/.venv/bin:$PATH
WORKDIR /app

RUN apt-get update && \
	apt-get install -y wget curl gcc python3-dev && \
	rm -rf /var/lib/apt/lists/*

RUN curl -LsSf https://astral.sh/uv/install.sh | sh
COPY . /app
RUN uv sync --python 3.13.2
RUN uv add uvicorn

EXPOSE 8080
CMD [ "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080" ]
