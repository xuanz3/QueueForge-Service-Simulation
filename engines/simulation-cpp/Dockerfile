FROM gcc:14-bookworm AS build
RUN apt-get update && apt-get install -y --no-install-recommends cmake ninja-build && rm -rf /var/lib/apt/lists/*
WORKDIR /workspace
COPY CMakeLists.txt .
COPY include include
COPY src src
COPY tests tests
RUN cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Release && cmake --build build && ctest --test-dir build --output-on-failure
FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends libstdc++6 && rm -rf /var/lib/apt/lists/*
COPY --from=build /workspace/build/queueforge-sim /usr/local/bin/queueforge-sim
RUN /usr/local/bin/queueforge-sim --health
USER 10001
ENTRYPOINT ["queueforge-sim"]
