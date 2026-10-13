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
                VALUES (%s, %s, %s)"""
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

# Notes Queries
class NotesQueries:
    @staticmethod
    def insertNotesRecord(userid: int, title: str, content: str):
        db_config = None
        cursor = None
        try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor()
            query = """
                INSERT INTO notes (userid, title, content)
                VALUES (%s, %s, %s)"""
            cursor.execute(query, (userid, title, content))
            db_config.commit()
            return True, "Notes added successfully"
        except Exception as e:
            if db_config:
                db_config.rollback()
            return False, f"Error in insertNotesRecord(): {e}"
        finally:
            if cursor:
                cursor.close()
            if db_config:
                db_config.close()

# get all notes records 
    @staticmethod
    def getAllNotes(userid: int, notesid:int=None):
        try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor(dictionary=True)
            query = """select * from notes where userid = %s"""
            values = [userid]
            if notesid:
                query += " and notesid = %s"
                values.append(notesid)
                cursor.execute(query, tuple(values))
                notes =  cursor.fetchone()
            else:
                cursor.execute(query, (userid,))
                notes = cursor.fetchall()
            db_config.close()
            cursor.close()
            return True, notes

        except Exception as e:
            return False, f"something wrong in database/utilsDB.py-NOtesQueries.getAllNotes(): {e}"