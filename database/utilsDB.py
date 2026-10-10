from database.connection import DatabaseConnection


class AuthQueries:

    @staticmethod
    def checkEmailExists(email: str, data: bool = False):
        try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor(dictionary=True)

            query = "SELECT * FROM users WHERE email = %s"
            cursor.execute(query, (email,))
            user = cursor.fetchone()

            cursor.close()
            db_config.close()

            if user:
                if data:
                    return True, user
                return True, "Email Exists"

            return False, "Email not Exists"

        except Exception as e:
            return False, f"Error in checkEmailExists(): {e}"

    @staticmethod
    def insertUserRecord(username: str, email: str, hash_password: str):
        try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor()

            query = """
                INSERT INTO users (username, email, hashpassword)
                VALUES (%s, %s, %s)
            """
            cursor.execute(query, (username, email, hash_password))
            db_config.commit()

            cursor.close()
            db_config.close()

            return True, "Successfully Registered"

        except Exception as e:
            return False, f"Error in insertUserRecord(): {e}"

    @staticmethod
    def updatePassword(email: str, hash_password: str):
        db_config = None
        cursor = None

        try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor()

            query = """
                UPDATE users SET hashpassword = %s WHERE email = %s """
            cursor.execute(query, (hash_password, email))
            db_config.commit()

            if cursor.rowcount == 0:
                return False, "Email not found or password unchanged"

            return True, "Password Updated Successfully"

        except Exception as e:
            if db_config:
                db_config.rollback()
            return False, f"Error in updatePassword(): {e}"

        finally:
            if cursor:
                cursor.close()
            if db_config:
                db_config.close()