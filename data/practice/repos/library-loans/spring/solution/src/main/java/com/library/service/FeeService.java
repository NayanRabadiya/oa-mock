package com.library.service;

import com.library.config.LoanRules;
import com.library.model.LateFee;
import com.library.util.Dates;
import org.springframework.stereotype.Service;

@Service
public class FeeService {
    /** Days a return is late, and the fee for it. A book returned on its due date (day 14) is on time. */
    public LateFee lateFee(String borrowedAt, String returnedAt) {
        long daysLate = Math.max(0, Dates.daysBetween(borrowedAt, returnedAt) - LoanRules.LOAN_DAYS);
        return new LateFee(daysLate, Math.min(daysLate * LoanRules.FEE_PER_DAY, LoanRules.MAX_FEE));
    }
}
