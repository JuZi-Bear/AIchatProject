package com.aichat.platform.config;

import com.aichat.platform.dto.ApiResponse;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.BindException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.client.RestClientException;
import org.springframework.web.server.ResponseStatusException;

@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(ResponseStatusException.class)
    public ResponseEntity<ApiResponse<Object>> handleResponseStatus(ResponseStatusException error) {
        String message = error.getReason() == null ? error.getMessage() : error.getReason();
        return ResponseEntity.status(error.getStatusCode())
                .body(ApiResponse.fail(message));
    }

    @ExceptionHandler({MethodArgumentNotValidException.class, BindException.class})
    public ResponseEntity<ApiResponse<Object>> handleValidation(Exception error) {
        return ResponseEntity.badRequest()
                .body(ApiResponse.fail("request validation failed"));
    }

    @ExceptionHandler(RestClientException.class)
    public ResponseEntity<ApiResponse<Object>> handleRestClient(RestClientException error) {
        return ResponseEntity.status(HttpStatus.BAD_GATEWAY)
                .body(ApiResponse.fail("python agent engine request failed: " + error.getMessage()));
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<ApiResponse<Object>> handleUnexpected(Exception error) {
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(ApiResponse.fail("java platform service error: " + error.getMessage()));
    }
}
