package com.wallet.controller;

import com.wallet.service.WalletException;
import java.util.Map;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

/** Turns a WalletException into its HTTP answer. */
@RestControllerAdvice
public class ApiErrors {
    @ExceptionHandler(WalletException.class)
    public ResponseEntity<Map<String, String>> walletError(WalletException e) {
        return ResponseEntity.status(e.status()).body(Map.of("message", e.getMessage()));
    }
}
