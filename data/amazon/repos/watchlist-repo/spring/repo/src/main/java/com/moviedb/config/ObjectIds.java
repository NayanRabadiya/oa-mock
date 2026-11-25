package com.moviedb.config;

import java.util.regex.Pattern;

// Movie ids are 24 hexadecimal characters, like MongoDB ObjectIds.
public final class ObjectIds {
    private static final Pattern OBJECT_ID = Pattern.compile("^[0-9a-fA-F]{24}$");

    private ObjectIds() {
    }

    public static boolean isValid(String value) {
        return value != null && OBJECT_ID.matcher(value).matches();
    }
}
