from datetime import date

from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import relationship

from .database import Base
from .security import hash_password, verify_password

book_authors = Table(
    "book_authors",
    Base.metadata,
    Column("book_id", Integer, ForeignKey("books.id"), primary_key=True),
    Column("author_id", Integer, ForeignKey("authors.id"), primary_key=True),
)


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    publication_date = Column(Date, nullable=True)
    available_copies = Column(Integer, nullable=False, default=0)
    genre = Column(String(100), nullable=False)
    authors = relationship("Author", secondary=book_authors, back_populates="books")


class Author(Base):
    __tablename__ = "authors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    biography = Column(Text, nullable=True)
    birth_date = Column(Date, nullable=True)
    books = relationship("Book", secondary=book_authors, back_populates="authors")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_admin = Column(Boolean, nullable=False, default=False)

    def set_password(self, password: str) -> None:
        self.hashed_password = hash_password(password)

    def check_password(self, password: str) -> bool:
        return verify_password(password, self.hashed_password)


class BorrowRecord(Base):
    __tablename__ = "borrow_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    borrow_date = Column(Date, nullable=False, default=date.today)
    return_date = Column(Date, nullable=True)

    user = relationship("User")
    book = relationship("Book")
