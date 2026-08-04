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

FROM maven:3.9-eclipse-temurin-21 AS java-build
WORKDIR /workspace/service
COPY services/control-plane-java/pom.xml .
COPY services/control-plane-java/src src
RUN mvn -B test package

FROM eclipse-temurin:21-jre AS java-runtime

FROM python:3.14-slim

ENV JAVA_HOME=/opt/java/openjdk \
    PATH=/opt/java/openjdk/bin:/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends libstdc++6 zlib1g \
    && rm -rf /var/lib/apt/lists/*

COPY --from=java-runtime /opt/java/openjdk /opt/java/openjdk
COPY --from=cpp-build /workspace/engine/build/queueforge-sim /usr/local/bin/queueforge-sim

WORKDIR /opt/queueforge-analytics
COPY analytics/queueforge-python/pyproject.toml .
COPY analytics/queueforge-python/src src
RUN python -m pip install --no-cache-dir . \
    && python -m queueforge_analytics health \
    && queueforge-sim --health

COPY tools/faults /opt/queueforge-faults
RUN chmod 0555 /opt/queueforge-faults/*.sh

WORKDIR /app
COPY --from=java-build /workspace/service/target/control-plane-java-0.4.0-SNAPSHOT.jar app.jar
RUN mkdir -p /var/lib/queueforge/runs \
    && chown -R 10001:0 /var/lib/queueforge /app

USER 10001
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "/app/app.jar"]
