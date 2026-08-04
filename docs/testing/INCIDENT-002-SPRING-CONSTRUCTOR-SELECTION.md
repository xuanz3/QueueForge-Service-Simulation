# Incident 002: Spring Could Not Construct RunService

## Summary

The Phase 4 Docker image compiled and packaged successfully. PostgreSQL started,
Flyway applied the first migration, and Tomcat initialized. Spring then stopped
while creating the `RunService` bean.

## Observed failure

```text
Failed to instantiate RunService: No default constructor found
NoSuchMethodException: RunService.<init>()
```

## Root cause

`RunService` declares two constructors:

- a five-argument production dependency-injection constructor
- a six-argument package-private constructor that accepts a test clock

Spring automatically uses an unannotated constructor only when the bean class
has a single constructor. With multiple unannotated constructors and no
primary/default constructor, the intended injection point was ambiguous.

## Resolution

The production constructor is explicitly marked with `@Autowired`.

A focused application-context test now registers all five production
dependencies and asks Spring to create `RunService`. This tests constructor
selection instead of only compiling or directly invoking the class.

## Prevention

- repository verification requires the explicit constructor annotation
- repository verification requires the context regression test
- Maven executes the context test during the API image build
- the end-to-end demo still requires the real API to start against PostgreSQL

## Impact

No Phase 4 branch was pushed and no Phase 4 pull request was created before the
full lifecycle verification passed.
