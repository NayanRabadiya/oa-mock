package com.library.util;

import java.time.LocalDate;
import java.time.ZoneOffset;
import java.time.format.DateTimeParseException;
import java.time.temporal.ChronoUnit;

/** Dates are calendar days in UTC, written "YYYY-MM-DD". */
public final class Dates {
    private Dates() {}

    public static boolean isIsoDate(String value) {
        if (value == null || !value.matches("\\d{4}-\\d{2}-\\d{2}")) {
            return false;
        }
        try {
            LocalDate.parse(value);
            return true;
        } catch (DateTimeParseException e) {
            return false;
        }
    }

    /** Whole days from `from` to `to` (negative when `to` is earlier). */
    public static long daysBetween(String from, String to) {
        return ChronoUnit.DAYS.between(LocalDate.parse(from.substring(0, 10)), LocalDate.parse(to.substring(0, 10)));
    }

    public static String today() {
        return LocalDate.now(ZoneOffset.UTC).toString();
    }
}
