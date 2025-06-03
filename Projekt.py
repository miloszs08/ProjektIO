import unittest
from datetime import datetime, timedelta

class User:
    def __init__(self, id, email, role, password="default_password"):
        self.id = id
        self.email = email
        self.role = role
        self.password = password
        self.blocked = False

    def login(self, password):
        if self.blocked:
            return False
        return self.password == password

    def change_password(self, old_password, new_password):
        if self.blocked:
            return False
        if self.password != old_password:
            return False
        if len(new_password) < 6:
            return False
        self.password = new_password
        return True

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
        self.borrow_date = datetime.now()
        self.return_date = None

    def calculate_fine(self):
        if self.return_date:
            return 0.0
        days_overdue = (datetime.now() - self.borrow_date).days - 14
        if days_overdue > 0:
            return days_overdue * 1.0
        return 0.0

    def is_overdue(self):
        if self.return_date:
            return False
        return (datetime.now() - self.borrow_date).days > 14

class LibrarySystem:
    def __init__(self):
        self.books = []
        self.users = []
        self.loans = []

    def search_books(self, query):
        return [book for book in self.books if query.lower() in book.title.lower() or query.lower() in book.author.lower()]

    def authenticate_user(self, email, password):
        for user in self.users:
            if user.email == email and user.login(password):
                return user
        return None

    def add_book(self, book):
        self.books.append(book)

    def remove_book(self, book_id):
        self.books = [b for b in self.books if b.id != book_id]

class TestLibrarySystem(unittest.TestCase):
    def setUp(self):
        self.library = LibrarySystem()
        self.user = User(1, "test@example.com", "reader", "password123")
        self.book = Book(1, "Test Book", "Test Author", 2020)
        self.book2 = Book(2, "Another Book", "Other Author", 2021)
        self.library.users.append(self.user)
        self.library.books.append(self.book)
        self.library.books.append(self.book2)

    # Tests for User.login
    def test_user_login_success(self):
        self.assertTrue(self.user.login("password123"))

    def test_user_login_invalid_password(self):
        self.assertFalse(self.user.login("wrong_password"))

    def test_user_login_blocked_user(self):
        self.user.blocked = True
        self.assertFalse(self.user.login("password123"))

    def test_user_login_empty_password(self):
        self.assertFalse(self.user.login(""))

    # Tests for User.change_password
    def test_change_password_success(self):
        result = self.user.change_password("password123", "newpassword456")
        self.assertTrue(result)
        self.assertEqual(self.user.password, "newpassword456")

    def test_change_password_invalid_old_password(self):
        result = self.user.change_password("wrong_password", "newpassword456")
        self.assertFalse(result)
        self.assertEqual(self.user.password, "password123")

    def test_change_password_too_short(self):
        result = self.user.change_password("password123", "short")
        self.assertFalse(result)
        self.assertEqual(self.user.password, "password123")

    def test_change_password_blocked_user(self):
        self.user.blocked = True
        result = self.user.change_password("password123", "newpassword456")
        self.assertFalse(result)
        self.assertEqual(self.user.password, "password123")

    # Tests for Book.is_available
    def test_book_is_available_initially(self):
        self.assertTrue(self.book.is_available())

    def test_book_is_available_after_borrowed(self):
        self.book.mark_as_borrowed()
        self.assertFalse(self.book.is_available())

    def test_book_is_available_after_returned(self):
        self.book.mark_as_borrowed()
        self.book.mark_as_returned()
        self.assertTrue(self.book.is_available())

    def test_book_is_available_multiple_borrows(self):
        self.book.mark_as_borrowed()
        self.book.mark_as_borrowed()
        self.assertFalse(self.book.is_available())

    # Tests for Book.mark_as_borrowed
    def test_mark_as_borrowed_available_book(self):
        self.assertTrue(self.book.mark_as_borrowed())
        self.assertEqual(self.book.status, "borrowed")

    def test_mark_as_borrowed_already_borrowed(self):
        self.book.mark_as_borrowed()
        self.assertFalse(self.book.mark_as_borrowed())
        self.assertEqual(self.book.status, "borrowed")

    def test_mark_as_borrowed_after_return(self):
        self.book.mark_as_borrowed()
        self.book.mark_as_returned()
        self.assertTrue(self.book.mark_as_borrowed())
        self.assertEqual(self.book.status, "borrowed")

    def test_mark_as_borrowed_status_unchanged_on_failure(self):
        self.book.mark_as_borrowed()
        self.book.mark_as_borrowed()
        self.assertEqual(self.book.status, "borrowed")

    # Tests for Loan.calculate_fine
    def test_calculate_fine_no_overdue(self):
        loan = Loan(1, self.user, self.book)
        self.assertEqual(loan.calculate_fine(), 0.0)

    def test_calculate_fine_after_return(self):
        loan = Loan(1, self.user, self.book)
        loan.return_date = datetime.now()
        self.assertEqual(loan.calculate_fine(), 0.0)

    def test_calculate_fine_overdue(self):
        loan = Loan(1, self.user, self.book)
        loan.borrow_date = datetime.now() - timedelta(days=15)
        self.assertEqual(loan.calculate_fine(), 1.0)

    def test_calculate_fine_multiple_days_overdue(self):
        loan = Loan(1, self.user, self.book)
        loan.borrow_date = datetime.now() - timedelta(days=20)
        self.assertEqual(loan.calculate_fine(), 6.0)

    # Tests for LibrarySystem.search_books
    def test_search_books_by_title(self):
        results = self.library.search_books("Test")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].title, "Test Book")

    def test_search_books_by_author(self):
        results = self.library.search_books("Author")
        self.assertEqual(len(results), 2)  
        self.assertIn(self.book, results)
        self.assertIn(self.book2, results)

    def test_search_books_no_results(self):
        results = self.library.search_books("Nonexistent")
        self.assertEqual(len(results), 0)

    def test_search_books_case_insensitive(self):
        results = self.library.search_books("test book")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].title, "Test Book")

if __name__ == "__main__":
    unittest.main()
