package com.wallet.config;

import java.util.List;

/** Limits of the wallet API. */
public final class Limits {
    public static final int DEFAULT_PAGE = 20;     // transactions returned when no limit is given
    public static final int MAX_PAGE = 100;        // the most a client can ask for
    public static final List<String> TYPES = List.of("deposit", "withdrawal", "transfer_in", "transfer_out");

    private Limits() {}
}
