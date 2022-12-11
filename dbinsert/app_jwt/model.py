from playhouse.postgres_ext import *
from decouple import config

ext_db = PostgresqlExtDatabase(config('database'),
                              user=config('user'),
                              password=config('password'),
                              host=config('host'),
                              port=config('port'))

ext_db.connect()

class jsondata(Model):
    id = AutoField()
    date = DateTimeField(null=False)
    jsondata = BinaryJSONField(null=False)


    class Meta:
        database = ext_db

class mestumdata(Model):
    id = AutoField()
    date = DateTimeField(null=False)
    eventid = IntegerField(null=False)
    streamid = IntegerField(null=False)
    uid = IntegerField(null=True)
    guestid = IntegerField(null=True)
    playing = IntegerField(null=False)
    playbackTime = IntegerField(null=False)
    playbackWatch = IntegerField(null=False)


    class Meta:
        database = ext_db

if __name__ == '__main__':
    jsondata.create_table()
    mestumdata.create_table()