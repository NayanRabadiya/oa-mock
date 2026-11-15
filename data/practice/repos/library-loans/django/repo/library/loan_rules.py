"""The library's lending rules."""
MAX_OPEN_LOANS = 3     # a member can have at most 3 books out at once
LOAN_DAYS = 14         # a book is due 14 days after it was borrowed
FEE_PER_DAY = 10       # late fee for each day after the due date
MAX_FEE = 200          # the fee for one loan never goes above this
