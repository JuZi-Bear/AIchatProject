FROM maven:3.9.9-eclipse-temurin-17 AS maven-tools

FROM eclipse-temurin:17-jdk AS build

COPY --from=maven-tools /usr/share/maven /usr/share/maven

ENV MAVEN_HOME=/usr/share/maven
ENV PATH="${MAVEN_HOME}/bin:${PATH}"

WORKDIR /app

COPY pom.xml .
COPY src ./src

RUN mvn -q -DskipTests package

FROM eclipse-temurin:17-jre

WORKDIR /app

COPY --from=build /app/target/*.jar app.jar

EXPOSE 8088

ENTRYPOINT ["java", "-jar", "app.jar"]
