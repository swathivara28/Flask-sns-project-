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
                query += " order by updated_at desc"
                cursor.execute(query, (userid,))
                notes = cursor.fetchall()
            db_config.close()
            cursor.close()
            return True, notes

        except Exception as e:
            return False, f"something wrong in database/utilsDB.py-NOtesQueries.getAllNotes(): {e}"
    # Update a note
    @staticmethod
    def updateNotes(userid: int, notesid: int, title: str, content: str):
        db_config = None
        cursor = None

        try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor()

            query = """
                UPDATE notes
                SET title = %s, content = %s
                WHERE notesid = %s AND userid = %s
            """
            cursor.execute(query, (title, content, notesid, userid))

            if cursor.rowcount == 0:
                db_config.rollback()
                return False, "Note not found or no changes made"

            db_config.commit()
            return True, "Notes Updated"

        except Exception as e:
            if db_config:
                db_config.rollback()
            return False, f"Error in updateNotes(): {e}"

        finally:
            if cursor:
                cursor.close()
            if db_config:
                db_config.close()

    # Delete a note belonging to the logged-in user
    @staticmethod
    def deleteNotes(userid: int, notesid: int):
        db_config = None
        cursor = None

        try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor()

            query = """
                DELETE FROM notes
                WHERE notesid = %s AND userid = %s
            """
            cursor.execute(query, (notesid, userid))

            if cursor.rowcount == 0:
                db_config.rollback()
                return False, "Note not found"

            db_config.commit()
            return True, "Note deleted successfully"

        except Exception as e:
            if db_config:
                db_config.rollback()
            return False, f"Error in deleteNotes(): {e}"

        finally:
            if cursor:
                cursor.close()
            if db_config:
                db_config.close()

    
    @staticmethod
    def getNotesCount(userid: int):
        db_config = None
        cursor = None

        try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor()

            query = "SELECT COUNT(*) FROM notes WHERE userid = %s"
            cursor.execute(query, (userid,))
            count = cursor.fetchone()[0]

            return True, count

        except Exception as e:
            return False, str(e)

        finally:
            if cursor:
                cursor.close()
            if db_config:
                db_config.close()



 #file queries   
class FilesQueries:

    @staticmethod
    def insertFileRecord(file_data:tuple[str|int]):

        try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor()
            query = """
                INSERT INTO files
                (userid, originalname, storedname,
                 mimetype, size, filepath)
                VALUES (%s, %s, %s, %s, %s, %s)
            """

            cursor.execute(query, file_data)
            db_config.commit()

            return True, "File details saved successfully"

        except Exception as e:
            

            print("File insert error:", e)
            return False, f"Something wrong in database/utilsdb.FilesQueries.insertFileRecord():{e}"

        finally:
            if cursor:
                cursor.close()
            if db_config:
                db_config.close()

    @staticmethod
    def getAllFiles(userid: int, fileid:int=None):
        db_config = None
        cursor = None
    
        try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor(dictionary=True)
    
            query = "SELECT * FROM files WHERE userid = %s"
            values = [userid]
    
            if fileid :
                query +=" and fileid = %s"
                values.append(fileid)
                cursor.execute(query, tuple(values))
                files = cursor.fetchone()
            else:

                query += " ORDER BY created_at DESC"
    
                cursor.execute(query, (userid,))
                files = cursor.fetchall()
    
                return True, files
    
        except Exception as e:
                return False, f"Error in getAllFiles(): {e}"
    
        finally:
                if cursor:
                    cursor.close()
                if db_config:
                    db_config.close()
    
    
    @staticmethod
    def getAllFiles(userid: int, fileid: int = None):
        db_config = None
        cursor = None

        try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor(dictionary=True)

            query = "SELECT * FROM files WHERE userid = %s"
            values = [userid]

            if fileid:
                query += " AND fileid = %s"
                values.append(fileid)

            query += " ORDER BY created_at DESC"

            cursor.execute(query, tuple(values))

            if fileid:
                files = cursor.fetchone()
            else:
                files = cursor.fetchall()

            return True, files

        except Exception as e:
            return False, f"Error in getAllFiles(): {e}"

        finally:
            if cursor:
                cursor.close()
            if db_config:
                db_config.close()

    @staticmethod
    def deleteFile(fileid: int):
        db_config = None
        cursor = None

        try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor(dictionary=True)

            query = """
                DELETE FROM files
                WHERE fileid = %s 
            """
            cursor.execute(query, (fileid,))

            if cursor.rowcount == 0:
                db_config.rollback()
                return False, "File not found"

            db_config.commit()
            return True, "File deleted successfully"

        except Exception as e:
            if db_config:
                db_config.rollback()
            return False, f"Error in deleteNotes(): {e}"

        finally:
            if cursor:
                cursor.close()
            if db_config:
                db_config.close()

    @staticmethod
    def getFilesCount(userid: int):
            db_config = None
            cursor = None
    
            try:
                db_config = DatabaseConnection()
                cursor = db_config.cursor()
    
                query = "SELECT COUNT(*) FROM files WHERE userid = %s"
                cursor.execute(query, (userid,))
                count = cursor.fetchone()[0]
    
                return True, count
    
            except Exception as e:
                return False, str(e)
    
            finally:
                if cursor:
                    cursor.close()
                if db_config:
                    db_config.close()