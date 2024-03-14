import pymysql


class MysqlUtil:
    def __init__(self):

        host = '127.0.0.1'
        user = 'root'
        password = '123456'
        database = 'fruitrecognition'
        self.db = pymysql.connect(host=host, user=user, password=password, db=database)
        self.cursor = self.db.cursor(cursor=pymysql.cursors.DictCursor)  

    def insert(self, sql):
        try:
            result = self.cursor.execute(sql)
            self.db.commit()
        except Exception as e:
            print("发生异常", e)
            self.db.rollback()
        finally:

            pass
        return result

    def fetchone(self, sql):
        try:
            self.cursor.execute(sql)
            result = self.cursor.fetchone()
        except Exception as e:
            print("发生异常", e)
            self.db.rollback()
        finally:

            pass
        return result

    def fetchall(self, sql):
        try:
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
        except Exception as e:
            print("发生异常", e)
            self.db.rollback()
        finally:
            self.db.close()
        return result

    def delete(self, sql):
        try:
            result = self.cursor.execute(sql)
            self.db.commit()
        except Exception as e:
            print("发生异常", e)
            self.db.rollback()
        finally:

            pass
        return result

    def update(self, sql):
        try:
            result = self.cursor.execute(sql)
            self.db.commit()
        except Exception as e:
            print("发生异常", e)
            self.db.rollback()
        finally:
            self.db.close()
        return result

    def close(self):
        try:
            self.db.close()
        except Exception as e:
            print("发生异常", e)

