package com.library.model;

import java.util.List;

/** A data set for the store: what src/main/resources/seed.json holds. */
public record LibraryData(List<Book> books, List<Member> members, List<Loan> loans) {}
