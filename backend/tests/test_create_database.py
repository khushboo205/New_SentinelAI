if __name__ == "__main__":
    from database.schema import Schema

    schema = Schema()
    schema.create_tables()
    print("Database created successfully.")