from database.connection import DatabaseConnection

class AuthQueries:
    @staticmethod
    def checkEmailExists(email:str,data:bool=False):
        try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor(dictionary=True)
            query = """SELECT * FROM users WHERE email = %s"""
            cursor.execute(query, (email,))
            user = cursor.fetchone()
            cursor.close()
            db_config.close()
            if user:
                if data:
                    return True, user
                else:
                    return True, "Email Exists"
            else:
                return False, "Email Not Exist"
        except Exception as e:
            return False, f"Something wrong in database/utilsDB.py-AuthQueries.checkEmailExists(): {e}"
    @staticmethod
    def insertUserRecord(username:str,email:str,hash_password:str):
         try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor()
            query = """insert into users(username,email,hashpassword)
                    values(%s,%s,%s)"""
            cursor.execute(query, ( username,email,hash_password))
            db_config.commit()
            cursor.close()
            db_config.close()
            return True,"Successfully Register"
           
         except Exception as e:
            return False, f"Something wrong in AuthQueries.insertUserRecord(): {e}"