from sqlite3 import connect,Cursor
from utils.utils import msgw

IE_TOTAL_SQL:str = """
SELECT 
    SUM(CASE WHEN ie = '收入' THEN Amount ELSE 0 END) AS TotalIncome,
    SUM(CASE WHEN ie = '支出' THEN Amount ELSE 0 END) AS TotalExpenses,
    SUM(CASE WHEN ie = '收入' THEN Amount ELSE 0 END) - SUM(CASE WHEN ie = '支出' THEN Amount ELSE 0 END) AS netTotal
FROM Accounting
"""# WHERE date LIKE '%2022%';

class database:
    """
    https://www.1keydata.com/tw/sql/sqlinsert.html

    2023-08-12
    """
    def __init__(self,filename:str) -> None:
        assert '.db' in filename,'[FileError] 資料庫應為 .db 檔.'
        self.conn = connect(filename,check_same_thread=False)
        self.cursor:Cursor = self.conn.cursor()

    def __call__(self,exe:str) -> list:
        return self.cursor.execute(exe).fetchall()
    
    def commit(self) -> None:
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()

    def get_head(self,table) -> list:
        return [column[1] for column in self.__call__(f"PRAGMA table_info({table})")]
    
    def get_table(self) -> list:
        return [table[0] for table in self.__call__("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")]
    
    def get_col(self,table, col_name, search:dict = {}, distinct = False, customize = ''):
        """
        ```
        print(db.get_col('Hospital','name',['name','%小%']))
        print(db.get_col('Hospital','name,area',['name','%小%']))
        ```
        """
        distinct = '' if distinct==False else 'DISTINCT' # SELECT DISTINCT  無重複
        if search=={}:
            return self.__call__(f"SELECT {distinct} {col_name} FROM {table} {customize}")
        else:
            _like = ''
            for n ,(key,value) in  enumerate(search.items()):
                if n==0: _like += f"{key} LIKE '{value}'"
                else: _like += f" AND {key} LIKE '{value}'"
            # print(f"SELECT {distinct} {col_name} FROM {table} WHERE {_like} {customize}")
            return self.__call__(f"SELECT {distinct} {col_name} FROM {table} WHERE {_like} {customize}")
        
    def get_row(self,table:str, row_name:list, col_name = None):
        """
        ```
        print(db.get_row('Data',['ID','1'],"hospital_name,rdate,ddate"))
        ```
        """
        col_name='*' if col_name==None else f"{col_name}"
        return self.__call__(f"SELECT {col_name} FROM {table} WHERE {row_name[0]} = '{row_name[1]}'")
        
    def exist(self, table:str, row_name:list) -> bool:
        """
        db.exist('Data',['ID','1'])
        """
        return bool(self.__call__(f"SELECT EXISTS(SELECT 1 FROM {table} WHERE {row_name[0]} = '{row_name[1]}')")[0][0])

    def delete(self, table:str, row_name:list):
        """
        db.delete('Data',['ID','1'])
        """
        try:
            self.__call__(f"DELETE FROM {table} WHERE {row_name[0]} = '{row_name[1]}'")
            self.commit()
            return True
        except Exception as e:
            print(f"Error deleting from {table}: {e}")
            return False
        
    def add(self, table:str, add_data:dict, commit:bool = True):
        """
        ```
        db.add('Hospital',{'name':'a'})
        ```
        """
        col_name, values = '',''
        for n, (key, value) in enumerate(add_data.items()):
            if n==0:
                col_name += key
                values += f"'{value}'"
            else:
                col_name += f",{key}"
                values += f",'{value}'"
        self.__call__(f"INSERT INTO {table} ({col_name}) VALUES ({values})")
        if commit==True: self.commit()

    def revise(self, table:str,update_data:dict, col_name:list):
        """
        ```
        db.revise('Data',{'id':'1'},['hospital_name','2'])
        ```
        """
        update_sql = ''
        for n, (key, value) in enumerate(update_data.items()):
            if n==0:
                update_sql += f"{key} = '{value}'"
            else:
                update_sql += f", {key} = '{value}'"
        self.__call__(f"UPDATE  {table} SET {update_sql} WHERE {col_name[0]} = '{col_name[1]}'")
        self.commit()

if __name__ == "__main__":
    db=database('writable/home.db')
    db("UPDATE Accounting SET Datestamp = strftime('%s', Date) WHERE Date IS NOt NULL AND Date LIKE '____/__/__'")
    # hospital_name=YAML(r'C:\Users\jetbo\Downloads\project\project.yaml')['hospital_name']
    # for _1,_2 in hospital_name.items():
    #     try:
    #         db(f"INSERT INTO Hospital (name,area) VALUES ('{_1}', '{_2}')")
    #     except:
    #         print(_1,_2 )
    # db.commit()

    # db.add('Data','hospital_name,rdate,ddate,patient,doctor,item,option,note,amount,create_time',f"'1','1','1','1','1','1','1','1','1','{datetime.now()}'")
    # a=db("SELECT amount*discount FROM Data WHERE ID = '1'")
    # db.revise('Data',['ID','1'],['real_amount',db("SELECT amount*discount FROM Data WHERE ID = '1'")[0][0]])

    
    






