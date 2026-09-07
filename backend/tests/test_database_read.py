if __name__ == "__main__":
    from database.database import Database

    db = Database()
    rows = db.fetchall("SELECT * FROM tracks")
    print("Tracks in database:", len(rows))
    for row in rows:
        print(dict(row))
    db.close()