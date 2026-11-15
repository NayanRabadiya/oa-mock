package com.library.controller;

import com.library.model.Book;
import com.library.model.LateFee;
import com.library.model.Loan;
import com.library.model.Member;
import com.library.service.FeeService;
import com.library.service.LoanService;
import com.library.store.LibraryStore;
import com.library.util.Dates;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api")
public class LoanController {
    private final LibraryStore store;
    private final LoanService loans;
    private final FeeService fees;

    public LoanController(LibraryStore store, LoanService loans, FeeService fees) {
        this.store = store;
        this.loans = loans;
        this.fees = fees;
    }

    private static ResponseEntity<Map<String, String>> error(int status, String message) {
        return ResponseEntity.status(status).body(Map.of("message", message));
    }

    private static String text(Map<String, Object> body, String key) {
        Object value = body == null ? null : body.get(key);
        return value == null || value.toString().isEmpty() ? null : value.toString();
    }

    /** GET /api/books  every book, with how many copies are on the shelf */
    @GetMapping("/books")
    public List<Map<String, Object>> listBooks() {
        return store.allBooks().stream().map(b -> {
            Map<String, Object> row = new LinkedHashMap<>();
            row.put("id", b.id());
            row.put("title", b.title());
            row.put("copies", b.copies());
            row.put("available", loans.availableCopies(b));
            return row;
        }).toList();
    }

    /** POST /api/loans  {memberId, bookId, borrowedAt?} */
    @PostMapping("/loans")
    public ResponseEntity<?> borrowBook(@RequestBody(required = false) Map<String, Object> body) {
        String memberId = text(body, "memberId");
        String bookId = text(body, "bookId");
        String borrowedAt = text(body, "borrowedAt") == null ? Dates.today() : text(body, "borrowedAt");
        if (memberId == null || bookId == null) {
            return error(400, "memberId and bookId are required");
        }
        if (!Dates.isIsoDate(borrowedAt)) {
            return error(400, "borrowedAt must be a date like 2026-11-15");
        }
        Member member = store.getMember(memberId);
        if (member == null) {
            return error(404, "Member not found");
        }
        Book book = store.getBook(bookId);
        if (book == null) {
            return error(404, "Book not found");
        }
        String problem = loans.cannotBorrow(member, book);
        if (problem != null) {
            return error(409, problem);
        }
        return ResponseEntity.status(201).body(store.addLoan(new Loan(null, memberId, bookId, borrowedAt, null)));
    }

    /** POST /api/loans/{loanId}/return  {returnedAt?} */
    @PostMapping("/loans/{loanId}/return")
    public ResponseEntity<?> returnBook(@PathVariable String loanId,
                                        @RequestBody(required = false) Map<String, Object> body) {
        Loan loan = store.getLoan(loanId);
        if (loan == null) {
            return error(404, "Loan not found");
        }
        if (!loan.open()) {
            return error(409, "Loan already returned");
        }
        String returnedAt = text(body, "returnedAt") == null ? Dates.today() : text(body, "returnedAt");
        if (!Dates.isIsoDate(returnedAt)) {
            return error(400, "returnedAt must be a date like 2026-11-15");
        }
        store.markReturned(loanId, returnedAt);
        LateFee fee = fees.lateFee(loan.borrowedAt(), returnedAt);
        Map<String, Object> out = new LinkedHashMap<>();
        out.put("loanId", loanId);
        out.put("returnedAt", returnedAt);
        out.put("daysLate", fee.daysLate());
        out.put("fee", fee.fee());
        return ResponseEntity.ok(out);
    }
}
