from dataclasses import dataclass
from contextlib import closing
import sqlite3
from database import get_connection

@dataclass
class Book:
    title:str
    description:str
    author:str 
    purchase_price:float
    rental_price:float
    stock:int



def read_book () :
    print("------------------------------------------------")
    title = input("Enter book title : ")
    description = input("Enter book description : ")
    author = input("Enter book author : ")
    while True:
        try:
            purchase_price = float(input("Enter book purchase price : "))
            rental_price = float(input("Enter book rental price : "))
            stock = int(input("Enter book stock : "))
            break
        except ValueError:
            print("Please enter valid numbers for prices and stock.")
    print("------------------------------------------------")
    return Book(
       title,
       description,
       author,
       purchase_price,
       rental_price,
       stock
     )

def add_book (Book) :
    with closing(get_connection()) as conn:
        conn.execute(
            """INSERT INTO books (title, description, author, purchase_price, rental_price, stock) VALUES (?, ?, ?, ?, ?, ?)""",
            (Book.title, Book.description, Book.author, Book.purchase_price, Book.rental_price, Book.stock)
        )
        conn.commit()
  
      






   
    
