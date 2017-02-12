import psycopg2
import sys

class Psql(object):

    def __init__(self, db, user, password=None):
        try:
            self.conn = psycopg2.connect(database=db, user=user, password=password)
        except psycopg2.DatabaseError as e:
            print('Error %s' % e)
            sys.exit(1)
        finally:
            pass

    def close():
        pass

    def create_col(self, name, path, ended=False):
        # Check if there is no exsist table, create it.
        with self.conn:
            with self.conn.cursor() as cur:
                cur.execute("SELECT * FROM collections WHERE name = %s;", (name,))
                colexsist = cur.fetchone()
                if(colexsist == None):
                    cur.execute("INSERT INTO collections (name, path, ended) VALUES (%s, %s, %s);", (name, path, ended))
        
    def update_col(self, name):
        # Count image number and update to collection
        with self.conn:
            with self.conn.cursor() as cur:
                cur.execute("SELECT images.id FROM images, collections WHERE collections.name = %s AND images.col = collections.id;", (name,))
                cur.execute("UPDATE collections SET pic_num= %s WHERE name= %s;", (cur.rowcount, name))

    def create_img(self, colname, name, checksum, size, path, url, source='generic'):
        # Check if there is no exsist image with the same checksum, then create it.
        with self.conn:
            with self.conn.cursor() as cur:
                    cur.execute("SELECT * FROM images WHERE hash = %s;", (checksum,))
                    imgexsist = cur.fetchone()
                    if(imgexsist == None):
                        cur.execute("SELECT * FROM collections WHERE name = %s;", (colname,))
                        colexsist = cur.fetchone()
                        if(colexsist != None):
                            colid = colexsist[0]
                            cur.execute(
                                "INSERT INTO images (col, name, hash, width, height, filepath, url, source) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);", 
                                (colid, name, checksum, size[0], size[1], path, url, source))

    def update_img():
        pass