from database.connection import DatabaseConnection

class AuthQueries:
    @staticmethod
    def checkEmailExists(email:str):
        try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor()
            query="""select * from users where email =%s"""
            cursor.execute(query,(email,))
            user = cursor.fetchone()
            db_config.close()
            cursor.close()
            if user:
                return True , "Email Exists"
            else:
                return False , "Email not Exists"
            

        except Exception as e:
            return False,  f"Something wrong in \database/utilsDB.py-AuthQueries.checkEmailExists():{e}"
    @staticmethod
    def insertUserRecord(username: str, email: str, hash_password: str):
        try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor()
            query = """INSERT INTO users(username, email, hashpassword) VALUES(%s, %s,%s)"""
            cursor.execute(query, (username,email, hash_password))
            db_config.commit()
            cursor.close()
            db_config.close()
            return True, "Successfully Registered"
        except Exception as e:
            return False, f"Something wrong in insertUserRecord(): {e}"