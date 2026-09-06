package com.mc.pgs.lab2.processor.error;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.MissingRequestHeaderException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import java.util.Map;

/**
 * Global, consistent error responses.
 *
 * <p>Client errors are distinguished from server errors, and the body handed back to a caller is
 * opaque: no stack trace, no internal class name, no field values. Detail useful for
 * investigation goes to the log, not the response.
 */
@RestControllerAdvice
public class ApiExceptionHandler {

    private static final Logger log = LoggerFactory.getLogger(ApiExceptionHandler.class);

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<Map<String, String>> onValidationFailure(MethodArgumentNotValidException ex) {
        log.info("Rejected a refund request that failed boundary validation: {} violation(s)",
                ex.getBindingResult().getErrorCount());
        return ResponseEntity.badRequest().body(Map.of("error", "VALIDATION_FAILED"));
    }

    @ExceptionHandler(MissingRequestHeaderException.class)
    public ResponseEntity<Map<String, String>> onMissingHeader(MissingRequestHeaderException ex) {
        log.info("Rejected a refund request missing a required header: {}", ex.getHeaderName());
        return ResponseEntity.badRequest().body(Map.of("error", "VALIDATION_FAILED"));
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<Map<String, String>> onUnexpected(Exception ex) {
        log.error("Unexpected failure handling a refund request", ex);
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(Map.of("error", "SYSTEM_ERROR"));
    }
}
