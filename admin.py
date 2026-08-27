from dataclasses import dataclass
from contextlib import closing
from database import get_connection

@dataclass
class Book:
    title:str
    discription:str
    author:str 
    price_buy:float
    price_rent:float
    stock:int



def read_book_ (title ,discription ,author ,price_rent  ,price_buy ,stock) :
    title = input("enter book title : ")
    discription = input("enter book discription : ")
    author = input("enter book author : ")
    price_rent = float(input("enter book price_sell : "))
    price_buy = float(input("enter book price_buy : "))
    stock = int(input("enter book stock : "))
    return Book(
       title,
       discription,
       author,
       price_rent,
       price_buy,
       stock
     )

def add_book (Book) :
    conn = get_connection()
    conn.execute(
        """INSERT INTO Books (title ,discription ,author ,price_rent  ,price_buy ,stock) VALUES (?,?,?,?,?,?)"""
    )
    conn.commit()
    conn.close()
  
      






   
    