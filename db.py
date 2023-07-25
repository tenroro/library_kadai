import os, psycopg2, string, random, hashlib


def get_connection():
    url = os.environ["DATABASE_URL"]
    connection = psycopg2.connect(url)
    return connection


def get_salt():
    charset = string.ascii_letters + string.digits

    salt = "".join(random.choices(charset, k=30))
    return salt


def get_hash(password, salt):
    b_pw = bytes(password, "utf-8")
    b_salt = bytes(salt, "utf-8")
    hashed_password = hashlib.pbkdf2_hmac("sha256", b_pw, b_salt, 1246).hex()
    return hashed_password


def insert_user(user_name,  mail, password):
    sql = "INSERT INTO user_tosyo VALUES(default, %s, %s,%s,%s)"

    salt = get_salt()
    hashed_password = get_hash(password, salt)

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(sql, (user_name,mail, hashed_password, salt))
        count = cursor.rowcount  # 更新件数を取得
        connection.commit()

    except psycopg2.DatabaseError:
        count = 0

    finally:
        cursor.close()
        connection.close()

    return count


def login(mail, password):
    sql = "SELECT hashed_password, salt FROM user_tosyo WHERE mail = %s"
    flg = False

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(sql, (mail,))
        user = cursor.fetchone()

        if user != None:
            # SQLの結果からソルトを取得
            salt = user[1]

            # DBから取得したソルト + 入力したパスワード からハッシュ値を取得
            hashed_password = get_hash(password, salt)

            # 生成したハッシュ値とDBから取得したハッシュ値を比較する
            if hashed_password == user[0]:
                flg = True

    except psycopg2.DatabaseError:
        flg = False

    finally:
        cursor.close()
        connection.close()

    return flg


def insert_book(isbn, title, author, publisher):
    sql = "INSERT INTO book_tosyo VALUES(default, %s, %s, %s,%s)"

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        sql,
        (
            isbn,
            title,
            author,
            publisher,
        ),
    )
    connection.commit()

    cursor.close()
    connection.close()


def delete_book(id):
    connection = get_connection()
    cursor = connection.cursor()
    sql = "delete from book_tosyo where id=%s"

    cursor.execute(sql, (id,))
    connection.commit()

    cursor.close()
    connection.close()


def search_book(title):
    connection = get_connection()
    cursor = connection.cursor()

    sql = "SELECT * FROM book_tosyo WHERE title LIKE %s"

    title2 = "%" + title + "%"

    cursor.execute(sql, (title2,))

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    return rows


def list_book():
    connection = get_connection()
    cursor = connection.cursor()

    sql = "SELECT ISBN,title,author,publisher FROM book_tosyo"

    cursor.execute(sql)

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    return rows


def update_book(ISBN, title, author, publisher, id):
    connection = get_connection()
    cursor = connection.cursor()
    sql = "update book_tosyo set ISBN=%s,title=%s,author=%s,publisher=%s where id=%s"

    cursor.execute(sql, (ISBN, title, author, publisher, id))
    connection.commit()

    cursor.close()
    connection.close()
