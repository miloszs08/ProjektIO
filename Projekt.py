class User:
    def __init__(self, id, email, role):
        self.id = id
        self.email = email
        self.role = role
        self.blocked = False

    def login(self, password):
        return True

    def change_password(self, new_password):
        pass

class Book:
    def __init__(self, id, title, author, year):
        self.id = id
        self.title = title
        self.author = author
        self.year = year
        self.status = "available"

    def is_available(self):
        return self.status == "available"

    def mark_as_borrowed(self):
        if self.is_available():
            self.status = "borrowed"
            return True
        return False

    def mark_as_returned(self):
        if self.status == "borrowed":
            self.status = "available"
            return True
        return False

class Loan:
    def __init__(self, id, user, book):
        self.id = id
        self.user = user
        self.book = book
        self.borrow_date = None
        self.return_date = None

    def calculate_fine(self):
        if self.return_date:
            return 0.0
        return 1.0

    def is_overdue(self):
        return self.return_date is None

class LibrarySystem:
    def __init__(self):
        self.books = []
        self.users = []
        self.loans = []

    def search_books(self, query):
        return [book for book in self.books if query.lower() in book.title.lower()]

    def authenticate_user(self, email, password):
        for user in self.users:
            if user.email == email and user.login(password):
                return user
        return None

    def add_book(self, book):
        self.books.append(book)

    def remove_book(self, book_id):
        self.books = [b for b in self.books if b.id != book_id]


import unittest

class TestLibrarySystem(unittest.TestCase):
    def setUp(self):
        self.library = LibrarySystem()
        self.user = User(1, "test@example.com", "reader")
        self.book = Book(1, "Test Book", "Author", 2020)
        self.library.users.append(self.user)
        self.library.books.append(self.book)

    def test_user_login(self):
        self.assertTrue(self.user.login("password"))
        self.assertFalse(self.user.blocked)

    def test_book_availability(self):
        self.assertTrue(self.book.is_available())
        self.book.mark_as_borrowed()
        self.assertFalse(self.book.is_available())

    def test_loan_creation(self):
        loan = Loan(1, self.user, self.book)
        self.library.loans.append(loan)
        self.assertEqual(len(self.library.loans), 1)
        self.assertEqual(loan.user, self.user)

    def test_fine_calculation(self):
        loan = Loan(1, self.user, self.book)
        self.assertEqual(loan.calculate_fine(), 1.0)
        loan.return_date = "2025-05-15"
        self.assertEqual(loan.calculate_fine(), 0.0)

    def test_book_removal(self):
        self.library.remove_book(1)
        self.assertEqual(len(self.library.books), 0)

if __name__ == "__main__":
    unittest.main()