package com.desk.util;

import java.time.Instant;
import java.time.format.DateTimeParseException;
import java.time.temporal.ChronoUnit;

/** Times are ISO 8601 strings in UTC, like 2026-11-15T09:30:00Z. */
public final class Times {
    public static final long SECONDS_PER_HOUR = 60 * 60;

    private Times() {}

    public static boolean isIsoTime(String value) {
        if (value == null || !value.matches("\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}(:\\d{2}(\\.\\d+)?)?Z")) {
            return false;
        }
        try {
            parse(value);
            return true;
        } catch (DateTimeParseException e) {
            return false;
        }
    }

    public static Instant parse(String value) {
        return Instant.parse(value.length() == 17 ? value.replace("Z", ":00Z") : value);
    }

    public static String now() {
        return Instant.now().truncatedTo(ChronoUnit.SECONDS).toString();
    }
}
