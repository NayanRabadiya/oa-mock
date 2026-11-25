package com.library.config;

/** The library's lending rules. */
public final class LoanRules {
    public static final int MAX_OPEN_LOANS = 3;   // a member can have at most 3 books out at once
    public static final int LOAN_DAYS = 14;       // a book is due 14 days after it was borrowed
    public static final int FEE_PER_DAY = 10;     // late fee for each day after the due date
    public static final int MAX_FEE = 200;        // the fee for one loan never goes above this

    private LoanRules() {}
}
