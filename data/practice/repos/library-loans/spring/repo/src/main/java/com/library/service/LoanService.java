package com.library.service;

import com.library.config.LoanRules;
import com.library.model.Book;
import com.library.model.Loan;
import com.library.model.Member;
import com.library.store.LibraryStore;
import java.util.List;
import org.springframework.stereotype.Service;

@Service
public class LoanService {
    private final LibraryStore store;

    public LoanService(LibraryStore store) {
        this.store = store;
    }

    /** How many copies of a book are on the shelf right now. */
    public int availableCopies(Book book) {
        return book.copies() - store.openLoans(l -> l.bookId().equals(book.id())).size();
    }

    /** Why a member can't borrow a book right now, or null when they can. */
    public String cannotBorrow(Member member, Book book) {
        if (availableCopies(book) <= 0) {
            return "No copies available";
        }
        List<Loan> open = store.openLoans(l -> l.memberId().equals(member.id()));
        if (open.size() > LoanRules.MAX_OPEN_LOANS) {
            return "Loan limit reached";
        }
        return null;
    }
}
