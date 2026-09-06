package com.mc.pgs.lab2.tta.error;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import java.util.Map;

/** Global error responses. Opaque to the caller, detailed in the log. */
@RestControllerAdvice
public class TtaExceptionHandler {

    private static final Logger log = LoggerFactory.getLogger(TtaExceptionHandler.class);

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<Map<String, String>> onValidationFailure(MethodArgumentNotValidException ex) {
        log.info("Rejected a refund request at the boundary: {} violation(s)",
                ex.getBindingResult().getErrorCount());
        return ResponseEntity.badRequest().body(Map.of("error", "VALIDATION_FAILED"));
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<Map<String, String>> onUnexpected(Exception ex) {
        log.error("Unexpected failure translating a refund", ex);
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(Map.of("error", "SYSTEM_ERROR"));
    }
}
