package dev.queueforge.controlplane.run;

import java.net.URI;
import java.time.Instant;
import java.util.stream.Collectors;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.ProblemDetail;
import org.springframework.http.ResponseEntity;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

@RestControllerAdvice
public class ApiExceptionHandler {

    @ExceptionHandler(InvalidRunRequestException.class)
    ResponseEntity<ProblemDetail> invalidRun(InvalidRunRequestException exception) {
        return problem(HttpStatus.BAD_REQUEST, "Invalid run request", exception.getMessage());
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    ResponseEntity<ProblemDetail> validation(MethodArgumentNotValidException exception) {
        String detail = exception.getBindingResult().getFieldErrors().stream()
                .map(error -> error.getField() + " " + error.getDefaultMessage())
                .collect(Collectors.joining("; "));
        return problem(HttpStatus.BAD_REQUEST, "Request validation failed", detail);
    }

    @ExceptionHandler(HttpMessageNotReadableException.class)
    ResponseEntity<ProblemDetail> unreadable(HttpMessageNotReadableException exception) {
        return problem(HttpStatus.BAD_REQUEST, "Malformed JSON", "Request body could not be parsed");
    }

    @ExceptionHandler(RunNotFoundException.class)
    ResponseEntity<ProblemDetail> notFound(RunNotFoundException exception) {
        return problem(HttpStatus.NOT_FOUND, "Run not found", exception.getMessage());
    }

    @ExceptionHandler(RunConflictException.class)
    ResponseEntity<ProblemDetail> conflict(RunConflictException exception) {
        return problem(HttpStatus.CONFLICT, "Run result unavailable", exception.getMessage());
    }

    @ExceptionHandler(RunCapacityException.class)
    ResponseEntity<ProblemDetail> capacity(RunCapacityException exception) {
        ProblemDetail detail = detail(
                HttpStatus.TOO_MANY_REQUESTS,
                "Run capacity exhausted",
                exception.getMessage());
        detail.setProperty("capacity", exception.capacity());
        return ResponseEntity.status(HttpStatus.TOO_MANY_REQUESTS)
                .header(HttpHeaders.RETRY_AFTER, "2")
                .body(detail);
    }

    private static ResponseEntity<ProblemDetail> problem(
            HttpStatus status,
            String title,
            String detail) {
        return ResponseEntity.status(status).body(detail(status, title, detail));
    }

    private static ProblemDetail detail(
            HttpStatus status,
            String title,
            String detail) {
        ProblemDetail problem = ProblemDetail.forStatusAndDetail(status, detail);
        problem.setTitle(title);
        problem.setType(URI.create("https://queueforge.dev/problems/" + status.value()));
        problem.setProperty("timestamp", Instant.now().toString());
        return problem;
    }
}
