package com.library.model;

/** A loan; returnedAt is null while the book is out. */
public record Loan(String id, String memberId, String bookId, String borrowedAt, String returnedAt) {
    public Loan withId(String newId) {
        return new Loan(newId, memberId, bookId, borrowedAt, returnedAt);
    }

    public Loan returned(String date) {
        return new Loan(id, memberId, bookId, borrowedAt, date);
    }

    public boolean open() {
        return returnedAt == null;
    }
}
