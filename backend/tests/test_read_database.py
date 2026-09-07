if __name__ == "__main__":
    from database.database import Database

    db = Database()
    print("=" * 50)
    print("TRACKS")
    print("=" * 50)
    rows = db.fetchall("SELECT * FROM tracks")
    for row in rows:
        print(dict(row))

    print()
    print("=" * 50)
    print("FEATURES")
    print("=" * 50)
    rows = db.fetchall("SELECT * FROM features")
    for row in rows:
        print(dict(row))
    db.close()