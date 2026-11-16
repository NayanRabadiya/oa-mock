package com.library.store;

import com.library.model.Book;
import com.library.model.LibraryData;
import com.library.model.Loan;
import com.library.model.Member;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.function.Predicate;
import org.springframework.stereotype.Component;

/**
 * An in-memory store standing in for the library database. reset() loads a data set (seed.json when the app
 * starts; the tests load their own).
 */
@Component
public class LibraryStore {
    private Map<String, Book> books = new LinkedHashMap<>();
    private Map<String, Member> members = new LinkedHashMap<>();
    private List<Loan> loans = new ArrayList<>();
    private int nextLoanId = 1;

    public synchronized void reset(LibraryData data) {
        books = new LinkedHashMap<>();
        members = new LinkedHashMap<>();
        loans = new ArrayList<>();
        if (data != null) {
            if (data.books() != null) data.books().forEach(b -> books.put(b.id(), b));
            if (data.members() != null) data.members().forEach(m -> members.put(m.id(), m));
            if (data.loans() != null) loans.addAll(data.loans());
        }
        nextLoanId = loans.size() + 1;
    }

    public synchronized List<Book> allBooks() {
        return List.copyOf(books.values());
    }

    public synchronized Book getBook(String id) {
        return books.get(id);
    }

    public synchronized Member getMember(String id) {
        return members.get(id);
    }

    public synchronized Loan getLoan(String id) {
        return loans.stream().filter(l -> l.id().equals(id)).findFirst().orElse(null);
    }

    public synchronized List<Loan> openLoans(Predicate<Loan> keep) {
        return loans.stream().filter(l -> l.open() && keep.test(l)).toList();
    }

    public synchronized Loan addLoan(Loan loan) {
        Loan saved = loan.withId("L" + nextLoanId++);
        loans.add(saved);
        return saved;
    }

    public synchronized Loan markReturned(String id, String date) {
        for (int i = 0; i < loans.size(); i++) {
            if (loans.get(i).id().equals(id)) {
                loans.set(i, loans.get(i).returned(date));
                return loans.get(i);
            }
        }
        return null;
    }
}
