import os

BOOKS_FILE = "books.csv"
MEMBERS_FILE = "members.csv"
XML_FILE = "borrowed_books.xml"

books = []
members = []

if os.path.exists(BOOKS_FILE):
    with open(BOOKS_FILE, "r") as f:
        books = [line.strip() for line in f if line.strip()]

if os.path.exists(MEMBERS_FILE):
    with open(MEMBERS_FILE, "r") as f:
        members = [line.strip() for line in f if line.strip()]

def save_books():
    with open(BOOKS_FILE, "w") as f:
        for b in books:
            f.write(b + "\n")

def save_members():
    with open(MEMBERS_FILE, "w") as f:
        for m in members:
            f.write(m + "\n")

def split_book(line):
    p = line.split(",")
    if len(p) < 5:
        return None
    return {
        "id": int(p[0]),
        "title": p[1],
        "author": p[2],
        "isbn": p[3],
        "available": p[4].lower() == "true"
    }

def get_book(bid):
    for b in books:
        d = split_book(b)
        if d and d["id"] == bid:
            return d
    return None

def find_member(card):
    for m in members:
        parts = m.split(",", 1)
        if parts[0] == card:
            return parts
    return None

def add_book(title, author, isbn):
    nid = 1
    for b in books:
        d = split_book(b)
        if d and d["id"] >= nid:
            nid = d["id"] + 1
    books.append(f"{nid},{title},{author},{isbn},true")
    save_books()
    print(f"Book added (ID {nid}).")

def register(card):
    if find_member(card):
        print("Card already exists.")
        return
    members.append(f"{card},")
    save_members()
    print("Member registered.")

def list_books():
    for b in books:
        d = split_book(b)
        if d:
            print(f'[{d["id"]}] {d["title"]} - {"Available" if d["available"] else "Borrowed"}')

def borrow(card, bid):
    mem = find_member(card)
    if not mem:
        print("Member not found.")
        return
    bk = get_book(bid)
    if not bk:
        print("Book not found.")
        return
    if not bk["available"]:
        print("Already borrowed.")
        return
    # Update book
    for i, b in enumerate(books):
        if b.startswith(str(bid) + ","):
            p = b.split(",")
            p[4] = "false"
            books[i] = ",".join(p)
            break
    # Update member
    for i, m in enumerate(members):
        if m.startswith(card + ","):
            members[i] = card + ","
            break
    save_books()
    save_members()
    print(f"Borrowed: {bk['title']}")

def return_book(card, bid):
    mem = find_member(card)
    if not mem:
        print("Member not found.")
        return
    borrowed_list = mem[1].split(";") if len(mem) > 1 and mem[1] else []
    if str(bid) not in borrowed_list:
        print("No such loan.")
        return
    # Update book
    for i, b in enumerate(books):
        if b.startswith(str(bid) + ","):
            p = b.split(",")
            p[4] = "true"
            books[i] = ",".join(p)
            break
    # Update member
    for i, m in enumerate(members):
        if m.startswith(card + ","):
            blist = m.split(",", 1)[1].split(";") if m.split(",", 1)[1] else []
            blist.remove(str(bid))
            members[i] = card + "," + ";".join(blist)
            break
    save_books()
    save_members()
    print("Returned.")

def list_members():
    for m in members:
        p = m.split(",", 1)
        print(f"Card: {p[0]}  Borrowed: {p[1] if len(p) > 1 else 'none'}")

def generate_xml():
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<library>\n  <borrowedBooks>\n'
    for m in members:
        p = m.split(",", 1)
        if len(p) > 1 and p[1]:
            for bid in p[1].split(";"):
                bk = get_book(int(bid))
                if bk:
                    xml += f'    <book borrowedBy="{p[0]}">\n'
                    xml += f'      <id>{bk["id"]}</id>\n'
                    xml += f'      <title>{bk["title"]}</title>\n'
                    xml += f'      <author>{bk["author"]}</author>\n'
                    xml += f'      <isbn>{bk["isbn"]}</isbn>\n'
                    xml += '    </book>\n'
    xml += '  </borrowedBooks>\n</library>\n'
    with open(XML_FILE, "w", encoding="utf-8") as f:
        f.write(xml)
    print(f"XML saved to {XML_FILE}")   

while True:
    print("\n1.Add Book  2.List Books  3.Register  4.List Members")
    print("5.Borrow   6.Return      7.XML       0.Exit")
    c = input("Choice: ")
    if c == "1":
        add_book(input("Title: "), input("Author: "), input("ISBN: "))
    elif c == "2":
        list_books()
    elif c == "3":
        register(input("Card: "))
    elif c == "4":
        list_members()
    elif c == "5":
        borrow(input("Card: "), int(input("Book ID: ")))
    elif c == "6":
        return_book(input("Card: "), int(input("Book ID: ")))
    elif c == "7":
        generate_xml()
    elif c == "0":
        print("Bye.")
        break
    else:
        print("Invalid choice.")