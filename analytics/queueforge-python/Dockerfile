FROM gcc:14-bookworm AS cpp-build

RUN apt-get update \
    && apt-get install -y --no-install-recommends cmake ninja-build \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace/engine
COPY engines/simulation-cpp/CMakeLists.txt .
COPY engines/simulation-cpp/include include
COPY engines/simulation-cpp/src src
COPY engines/simulation-cpp/tests tests

RUN cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Release \
    && cmake --build build \
    && ctest --test-dir build --output-on-failure

FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    QUEUEFORGE_ENGINE_PATH=/usr/local/bin/queueforge-sim

WORKDIR /app

COPY analytics/queueforge-python/pyproject.toml .
COPY analytics/queueforge-python/src src
COPY analytics/queueforge-python/tests tests

RUN python -m pip install --no-cache-dir . \
    && python -m unittest discover -s tests -v

COPY --from=cpp-build /workspace/engine/build/queueforge-sim /usr/local/bin/queueforge-sim
RUN queueforge-sim --health

CMD ["python", "-m", "queueforge_analytics", "health"]
