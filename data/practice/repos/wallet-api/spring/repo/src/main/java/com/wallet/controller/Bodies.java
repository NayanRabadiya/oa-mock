package com.wallet.controller;

import com.wallet.service.WalletException;
import com.wallet.util.Times;
import java.util.Map;

/** Reading request bodies. */
final class Bodies {
    private Bodies() {}

    static String text(Map<String, Object> body, String key) {
        Object value = body == null ? null : body.get(key);
        return value == null || value.toString().isEmpty() ? null : value.toString();
    }

    static Object value(Map<String, Object> body, String key) {
        return body == null ? null : body.get(key);
    }

    static String time(Map<String, Object> body) {
        String at = text(body, "at") == null ? Times.now() : text(body, "at");
        if (!Times.isIsoTime(at)) {
            throw new WalletException(400, "at must be a time like 2026-11-15T09:30:00Z");
        }
        return at;
    }
}
