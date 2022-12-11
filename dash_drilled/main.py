import psycopg2
import datetime
import numpy as np
import pandas as pd
from decouple import config as c
from sqlalchemy import create_engine
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi import Request
from fastapi.templating import Jinja2Templates
from fastapi import APIRouter


routerDrill = APIRouter()



templates = Jinja2Templates(directory="templates")

@routerDrill.get('/stat/{id}/session/{sid}', tags=['Session Room Route'], response_class=HTMLResponse)
async def index(request: Request, id:int, sid:int, title='index'):
    
    # number of watching card
    async def dataset_watching(eventid=id, streamid=sid):
        engine = create_engine(f'postgresql://{c.user}:{c.password}@{c.host}:{c.port}/{c.database}') 
        dbConnection = engine.connect()
        sql =  f'''
                    select COUNT(counttable.uid) 
                    from( select statplayer.uid 
                          from statplayer 
                          inner join 
                          (select MAX(date) as date, uid 
                          from statplayer 
                          where uid is not NULL 
                          and eventid = {eventid}
                          AND streamid = {streamid}  
                          group by uid order by date) as t1 on t1.uid=statplayer.uid and t1.date=statplayer.date 
                          where playing = 1 and eventid = {eventid} and streamid = {streamid} 
                    UNION ALL 
                    select statplayer.guestid 
                    from statplayer  
                    inner join
                    (select MAX(date) as date, guestid 
                    from statplayer 
                    where guestid is not NULL 
                    and eventid = {eventid}
                    AND streamid = {streamid} 
                    group by guestid order by date) as t1 on t1.guestid=statplayer.guestid and t1.date=statplayer.date 
                    where playing = 1 and eventid = {eventid} and streamid = {streamid} ) as counttable
                '''       
        table_watching = pd.read_sql_query(con=dbConnection, sql=sql)
        dbConnection.close()
        return table_watching
    
    dataset_watching = await dataset_watching()
    number_watching = list(dataset_watching.iloc[0])[0]
    
    # number of on pauses card
    async def dataset_pause(eventid=id, streamid=sid):
        engine = create_engine(f'postgresql://{c.user}:{c.password}@{c.host}:{c.port}/{c.database}') 
        dbConnection = engine.connect()
        sql = f'''
                select 
                COUNT(counttable.uid) 
                from( 
                    select statplayer.uid 
                    from statplayer 
                    inner join 
                    (select MAX(date) as date, uid 
                    from statplayer 
                    where uid is not NULL 
                    and eventid = {eventid}
                    AND streamid = {streamid} 
                    group by uid 
                    order by date) as t1 on t1.uid=statplayer.uid and t1.date=statplayer.date 
                    where playing = 0 and eventid = {eventid} and streamid = {streamid} 
                UNION ALL 
                select statplayer.guestid 
                from statplayer  
                inner join 
                (select MAX(date) as date, guestid 
                from statplayer 
                where guestid is not NULL 
                and eventid = {eventid}
                AND streamid = {streamid} 
                group by guestid 
                order by date) as t1 on t1.guestid=statplayer.guestid and t1.date=statplayer.date 
                where playing = 0 and eventid = {eventid} and streamid = {streamid} ) as counttable

               '''
                
        table_pause = pd.read_sql_query(con=dbConnection, sql=sql)
        dbConnection.close()
        return table_pause
    
    dataset_pause= await dataset_pause()
    number_pause = list(dataset_pause.iloc[0])[0]
    
    # Computing the AVD (average view duration) card
    async def dataset_avd(eventid=id, streamid=sid):
        engine = create_engine(f'postgresql://{c.user}:{c.password}@{c.host}:{c.port}/{c.database}') 
        dbConnection = engine.connect()
        sql =  f'''
                    select round((sum(tableavd.playbackwatch)*0.0167)/count(tableavd.uid),2) 
                    from(
                        select uid, playbackwatch 
                        from statplayer 
                        where playing = 1 
                        AND uid is not null 
                        and eventid = {eventid} 
                        AND streamid = {streamid}
                    UNION ALL
                    select guestid, playbackwatch 
                    from statplayer 
                    where playing = 1 
                    and guestid is not null
                    and eventid = {eventid} 
                    AND streamid = {streamid}) as tableavd 
                '''
           
        table_avd = pd.read_sql_query(con=dbConnection, sql=sql)
        dbConnection.close()
        return table_avd
    
    dataset_avd = await dataset_avd()
    dataset_avd = list(dataset_avd.iloc[0])[0]
    
    
    async def dataset_avd_prct(eventid=id, streamid=sid):
        engine = create_engine(f'postgresql://{c.user}:{c.password}@{c.host}:{c.port}/{c.database}') 
        dbConnection = engine.connect()
        sql =  f'''
                    select round(((((sum(tableavd.playbackwatch)*0.0167)/count(tableavd.uid))/(max(tableavd.playbackwatch))*0.0167)*100),2) 
                    from(
                        select uid, playbackwatch 
                        from statplayer 
                        where playing = 1 
                        AND uid is not null 
                        and eventid = {eventid}
                        AND streamid = {streamid}
                    UNION ALL
                    select guestid, playbackwatch 
                    from statplayer 
                    where playing = 1 
                    and guestid is not null
                    and eventid = {eventid} 
                    AND streamid = {streamid}) as tableavd 
                '''
           
        table_avd = pd.read_sql_query(con=dbConnection, sql=sql)
        dbConnection.close()
        return table_avd
    
    avd_prct = await dataset_avd_prct()
    avd_prct = list(avd_prct.iloc[0])[0]
    
    
    # status table
    async def dataset_table(eventid=id, streamid=sid):
        engine = create_engine(f'postgresql://{c.user}:{c.password}@{c.host}:{c.port}/{c.database}') 
        dbConnection = engine.connect()
        sql = f'''
                select * from (
                    select statplayer.uid as Зритель, statplayer.playing as Статус from statplayer 
                    inner join 
                    (select MAX(date) as date, uid 
                    from statplayer 
                    where uid is not NULL 
                    and eventid = {eventid}
                    AND streamid = {streamid} 
                    group by uid order by date) as t1 on t1.uid=statplayer.uid and t1.date=statplayer.date
                    WHERE eventid = {eventid} and streamid = {streamid}  
                    UNION ALL 
                    select statplayer.guestid, statplayer.playing 
                    from statplayer 
                    inner join (
                        select MAX(date) as date, guestid 
                        from statplayer 
                        where guestid is not NULL 
                        and eventid = {eventid}
                        AND streamid = {streamid} 
                        group by guestid order by date) as t1 on t1.guestid=statplayer.guestid and t1.date=statplayer.date
                        where eventid = {eventid} and streamid = {streamid} ) as tablestatus 
                    order by Статус, Зритель asc
               '''
        
        table_table = pd.read_sql_query(con=dbConnection, sql=sql) 
        dbConnection.close()
        return table_table
        
    dataset_table = await dataset_table()
    
    dataset_table['Активность'] = 0
    dataset_table.loc[dataset_table['Статус']==1,'Активность'] = ''

    
    dataset_table.loc[dataset_table['Статус']==1,'Статус'] = 'online'
    dataset_table.loc[dataset_table['Статус']==0,'Статус'] = 'offline'
    
    dataset_table['Зритель'] = dataset_table['Зритель'].astype(np.int64)
    dataset_table = dataset_table[['Статус', 'Зритель', 'Активность']]
    
    heading = dataset_table.columns
    contents_list = []
    for i,j in dataset_table.iterrows():
        contents_list.append(list(j))
        

    # plot data online
    async def dataonline_table(eventid=id, streamid=sid):
        engine = create_engine(f'postgresql://{c.user}:{c.password}@{c.host}:{c.port}/{c.database}') 
        dbConnection = engine.connect()
        sql = f'''
                select array_agg(date) as date, array_agg(usercount) as usercount 
                from(
                    select cast(t1.date as TEXT) as date, COUNT(t1.userid_count) as usercount
                    from(
                        (select date, uid as userid_count 
                        from statplayer 
                        where playing=1 
                        and eventid = {eventid}
                        and streamid={streamid} 
                        and uid is not null)
                UNION ALL
                (select date, guestid as userid_count 
                from statplayer 
                where playing=1 
                and eventid = {eventid}
                and streamid={streamid}
                and guestid is not null)) as t1
                group by t1.date
                order by t1.date) as online_plot
               '''
        table = pd.read_sql_query(con=dbConnection, sql=sql)
        
        dbConnection.close()
        return table
        
    dataonline_table = await dataonline_table()
    
    online_labels = dataonline_table['date'][0]
    online_data = dataonline_table['usercount'][0]

    # plot data offline
    async def dataoffline_table(eventid=id, streamid=sid):
        engine = create_engine(f'postgresql://{c.user}:{c.password}@{c.host}:{c.port}/{c.database}') 
        dbConnection = engine.connect()
        sql = f'''                
                select array_agg(date) as date, array_agg(usercount) as usercount 
                from(
                    select cast(t1.date as TEXT) as date, COUNT(t1.userid_count) as usercount
                    from(
                        (select date, uid as userid_count 
                        from statplayer 
                        where playing=0 
                        and eventid = {eventid}
                        and streamid={streamid} 
                        and uid is not null)
                UNION ALL
                (select date, guestid as userid_count 
                from statplayer 
                where playing=0 
                and eventid = {eventid}
                and streamid={streamid}
                and guestid is not null)) as t1
                group by t1.date
                order by t1.date) as offline_plot
               '''
        dataoffline_table = pd.read_sql_query(con=dbConnection, sql=sql)
        
        date_count_list = []
        date = dataoffline_table['date'][0]
        date_count_list.append(date)
        usercount = dataoffline_table['usercount'][0]
        date_count_list.append(usercount)
        
        dbConnection.close()
        return date_count_list
        
    dataoffline_table = await dataoffline_table()
    
    offline_labels = dataoffline_table[0]
    offline_data = dataoffline_table[1]
    
    # plot data unique watching
    async def dataset_dataunique(eventid=id, streamid=sid):
        engine = create_engine(f'postgresql://{c.user}:{c.password}@{c.host}:{c.port}/{c.database}') 
        dbConnection = engine.connect()
        sql = f'''
                select cast(t1.date as TEXT) as date, count(t1.uid) from (
                    select uid, min(date) as date 
                    from statplayer 
                    where uid is not null 
                    and playing=1 
                    and eventid = {eventid}
                    and streamid = {streamid} 
                    group by uid
                UNION ALL
                select guestid, min(date) as date 
                from statplayer 
                where guestid is not null 
                and playing=1 
                and eventid = {eventid}
                and streamid = {streamid} 
                group by guestid) as t1
                group by date
                order by date
               '''
        table = pd.read_sql_query(con=dbConnection, sql=sql)
        dbConnection.close()
        return table
    
    dataset_dataunique = await dataset_dataunique()

    unique_labels = list(dataset_dataunique['date'])
    unique_data = list(dataset_dataunique['count'])
    
    sum_uniqueusers = sum(dataset_dataunique['count'])
    
    # PEAK watch
    async def dataonline_table(eventid=id, streamid=sid):
        engine = create_engine(f'postgresql://{c.user}:{c.password}@{c.host}:{c.port}/{c.database}') 
        dbConnection = engine.connect()
        sql = f'''
                select array_agg(date) as date, array_agg(usercount) as usercount 
                from(
                    select SUBSTRING(cast(t1.date as TEXT),12) as date, COUNT(t1.userid_count) as usercount
                    from(
                        (select date, uid as userid_count 
                        from statplayer 
                        where playing=1 
                        AND eventid = {eventid}
                        and streamid={streamid} 
                        and uid is not null)
                UNION ALL
                (select date, guestid as userid_count 
                from statplayer 
                where playing=1 
                AND eventid = {eventid}
                and streamid={streamid}
                and guestid is not null)) as t1
                group by t1.date
                order by t1.date) as online_plot
               '''
        table = pd.read_sql_query(con=dbConnection, sql=sql)
        
        dbConnection.close()
        return table
        
    dataonline_table = await dataonline_table()
    
    try:
        peak_data = max(dataonline_table['usercount'][0])
    except:
        peak_data = 0

    
    id_url = id
    sid_url = sid
    return templates.TemplateResponse("index.html", {"request": request, 'title':title, 'watch':number_watching,
                                                     'pause':number_pause , 'avd':dataset_avd, 'avdprct':avd_prct,
                                                     'heading':heading,
                                                     'contents':contents_list,
                                                     'plot_online_data':online_data,
                                                     'plot_online_label':online_labels,
                                                     'plot_offline_data':offline_data,
                                                     'plot_offline_label':offline_labels,
                                                     'unique_labels':unique_labels,
                                                     'unique_data':unique_data,
                                                     'sum_unique':sum_uniqueusers,
                                                     'id':id_url,
                                                     'sid':sid_url,
                                                     'peak_data' : peak_data})


# _-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-UPDATING SESSION ROOMS-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-

# Watching Card
@routerDrill.post('/card_watch_drill/{id}/{sid}', tags=['card_watch'], response_class=HTMLResponse)
async def update(request:Request, id:int, sid:int):
    async def dataset_watching(eventid=id, streamid=sid):
        engine = create_engine(f'postgresql://{c.user}:{c.password}@{c.host}:{c.port}/{c.database}') 
        dbConnection = engine.connect()
        
        sql =  f'''
                    select COUNT(counttable.uid) 
                    from( select statplayer.uid 
                          from statplayer 
                          inner join 
                          (select MAX(date) as date, uid 
                          from statplayer 
                          where uid is not NULL 
                          AND eventid = {eventid} 
                          AND streamid = {streamid}  
                          group by uid order by date) as t1 on t1.uid=statplayer.uid and t1.date=statplayer.date 
                          where playing = 1 and eventid = {eventid} and streamid = {streamid} 
                    UNION ALL 
                    select statplayer.guestid 
                    from statplayer  
                    inner join
                    (select MAX(date) as date, guestid 
                    from statplayer 
                    where guestid is not NULL 
                    AND eventid = {eventid}
                    AND streamid = {streamid} 
                    group by guestid order by date) as t1 on t1.guestid=statplayer.guestid and t1.date=statplayer.date 
                    where playing = 1 and eventid = {eventid} and streamid = {streamid} ) as counttable
                
                '''
                
        table_watching = pd.read_sql_query(con=dbConnection, sql=sql)
        dbConnection.close()
        return table_watching
    
    dataset_watching = await dataset_watching()
    number_watching = list(dataset_watching.iloc[0])[0]
    
    return templates.TemplateResponse('update_drill/card_watch.html', {'request':request, 'watch':number_watching})

@routerDrill.post('/card_pause_drill/{id}/{sid}', tags=['card_pause'], response_class=HTMLResponse)
async def update(request:Request, id:int, sid:int):
    async def dataset_pause(eventid=id, streamid=sid):
        engine = create_engine(f'postgresql://{c.user}:{c.password}@{c.host}:{c.port}/{c.database}') 
        dbConnection = engine.connect()
        sql = f'''
                select 
                COUNT(counttable.uid) 
                from( 
                    select statplayer.uid 
                    from statplayer 
                    inner join 
                    (select MAX(date) as date, uid 
                    from statplayer 
                    where uid is not NULL 
                    AND eventid = {eventid} 
                    AND streamid = {streamid} 
                    group by uid 
                    order by date) as t1 on t1.uid=statplayer.uid and t1.date=statplayer.date 
                    where playing = 0 and eventid = {eventid} and streamid = {streamid}  
                UNION ALL 
                select statplayer.guestid 
                from statplayer  
                inner join 
                (select MAX(date) as date, guestid 
                from statplayer 
                where guestid is not NULL 
                AND eventid = {eventid} 
                AND streamid = {streamid} 
                group by guestid 
                order by date) as t1 on t1.guestid=statplayer.guestid and t1.date=statplayer.date 
                where playing = 0 and eventid = {eventid} and streamid = {streamid} ) as counttable

               '''
                
        table_pause = pd.read_sql_query(con=dbConnection, sql=sql)
        dbConnection.close()
        return table_pause
    
    dataset_pause= await dataset_pause()
    number_pause = list(dataset_pause.iloc[0])[0]

    return templates.TemplateResponse('update_drill/card_pause.html', {'request':request, 'pause':number_pause})

@routerDrill.post('/peak_data/{id}/{sid}', tags=['dataOnline'], response_class=HTMLResponse)
async def update(request:Request,id:int, sid:int):
    async def dataonline_table(eventid=id, streamid=sid):
        engine = create_engine(f'postgresql://{c.user}:{c.password}@{c.host}:{c.port}/{c.database}') 
        dbConnection = engine.connect()
        sql = f'''
                select array_agg(date) as date, array_agg(usercount) as usercount 
                from(
                    select SUBSTRING(cast(t1.date as TEXT),12) as date, COUNT(t1.userid_count) as usercount
                    from(
                        (select date, uid as userid_count 
                        from statplayer 
                        where playing=1 
                        AND eventid = {eventid}
                        and streamid={streamid} 
                        and uid is not null)
                UNION ALL
                (select date, guestid as userid_count 
                from statplayer 
                where playing=1 
                AND eventid = {eventid}
                and streamid={streamid}
                and guestid is not null)) as t1
                group by t1.date
                order by t1.date) as online_plot
               '''
        table = pd.read_sql_query(con=dbConnection, sql=sql)
        
        dbConnection.close()
        return table
        
    dataonline_table = await dataonline_table()
    try:
        peak_data = max(dataonline_table['usercount'][0])
    except:
        peak_data = 0


    return templates.TemplateResponse("update_drill/peak_data.html", {"request": request,
                                                     'peak_data':peak_data,
                                                    })

@routerDrill.post('/avd_drill/{id}/{sid}', tags=['avd'], response_class=HTMLResponse)
async def update(request:Request, id:int, sid:int):
    async def dataset_avd(eventid=id, streamid=sid):
        engine = create_engine(f'postgresql://{c.user}:{c.password}@{c.host}:{c.port}/{c.database}') 
        dbConnection = engine.connect()
        sql =  f'''
                    select round((sum(tableavd.playbackwatch)*0.0167)/count(tableavd.uid),2) 
                    from(
                        select uid, playbackwatch 
                        from statplayer 
                        where playing = 1 
                        AND uid is not null 
                        AND eventid = {eventid} 
                        AND streamid = {streamid} 
                    UNION ALL
                    select guestid, playbackwatch 
                    from statplayer 
                    where playing = 1 
                    and guestid is not null
                    AND eventid = {eventid} 
                    AND streamid = {streamid} ) as tableavd 
                '''
           
        table_avd = pd.read_sql_query(con=dbConnection, sql=sql)
        dbConnection.close()
        return table_avd
    
    dataset_avd = await dataset_avd()
    dataset_avd = list(dataset_avd.iloc[0])[0]
    
    return templates.TemplateResponse('update_drill/avd.html', {'request':request, 'avd':dataset_avd})


@routerDrill.post('/avdprct_drill/{id}/{sid}', tags=['avd'], response_class=HTMLResponse)
async def update(request:Request, id:int, sid:int):
    async def dataset_avd_prct(eventid=id, streamid=sid):
            engine = create_engine(f'postgresql://{c.user}:{c.password}@{c.host}:{c.port}/{c.database}') 
            dbConnection = engine.connect()
            sql =  f'''
                        select round(((((sum(tableavd.playbackwatch)*0.0167)/count(tableavd.uid))/(max(tableavd.playbackwatch))*0.0167)*100),2) 
                        from(
                            select uid, playbackwatch 
                            from statplayer 
                            where playing = 1 
                            AND uid is not null 
                            and eventid = {eventid}
                            AND streamid = {streamid}
                        UNION ALL
                        select guestid, playbackwatch 
                        from statplayer 
                        where playing = 1 
                        and guestid is not null
                        and eventid = {eventid} 
                        AND streamid = {streamid}) as tableavd 
                    '''           
            
            table_avd = pd.read_sql_query(con=dbConnection, sql=sql)
            dbConnection.close()
            return table_avd
        
    avd_prct = await dataset_avd_prct()
    avd_prct = list(avd_prct.iloc[0])[0]
    

    return templates.TemplateResponse('update_drill/avdprct.html', {'request':request, 'avdprct':avd_prct})

@routerDrill.post('/update_time_drill/', tags=['update_time'], response_class=HTMLResponse)
async def update(request:Request):
    time = datetime.datetime.now().time().strftime('%H:%M')
    return templates.TemplateResponse('update_drill/updatetime.html', {'request':request, 'time':time})

@routerDrill.post('/dataoffline_drill/{id}/{sid}', tags=['dataOffline'], response_class=HTMLResponse)
async def update(request:Request,id:int, sid:int):
    async def dataoffline_table(eventid=id, streamid=sid):
        engine = create_engine(f'postgresql://{c.user}:{c.password}@{c.host}:{c.port}/{c.database}') 
        dbConnection = engine.connect()
        sql = f'''                
                select array_agg(date) as date, array_agg(usercount) as usercount 
                from(
                    select cast(t1.date as TEXT) as date, COUNT(t1.userid_count) as usercount
                    from(
                        (select date, uid as userid_count 
                        from statplayer 
                        where playing=0 
                        AND eventid = {eventid}
                        and streamid={streamid} 
                        and uid is not null)
                UNION ALL
                (select date, guestid as userid_count 
                from statplayer 
                where playing=0 
                AND eventid = {eventid}
                and streamid={streamid}
                and guestid is not null)) as t1
                group by t1.date
                order by t1.date) as offline_plot
               '''
        dataoffline_table = pd.read_sql_query(con=dbConnection, sql=sql)
        
        date_count_list = []
        date = dataoffline_table['date'][0]
        date_count_list.append(date)
        usercount = dataoffline_table['usercount'][0]
        date_count_list.append(usercount)
        
        dbConnection.close()
        return date_count_list
        
    dataoffline_table = await dataoffline_table()
    
    offline_labels = dataoffline_table[0]
    offline_data = dataoffline_table[1]
    
    return templates.TemplateResponse("update_drill/data_offline.html", {"request": request,
                                                     'plot_offline_data':offline_data,
                                                     'plot_offline_label':offline_labels
                                                    })

@routerDrill.post('/dataonline_drill/{id}/{sid}', tags=['dataOnline'], response_class=HTMLResponse)
async def update(request:Request,id:int, sid:int):
    async def dataonline_table(eventid=id, streamid=sid):
        engine = create_engine(f'postgresql://{c.user}:{c.password}@{c.host}:{c.port}/{c.database}') 
        dbConnection = engine.connect()
        sql = f'''
                select array_agg(date) as date, array_agg(usercount) as usercount 
                from(
                    select cast(t1.date as TEXT) as date, COUNT(t1.userid_count) as usercount
                    from(
                        (select date, uid as userid_count 
                        from statplayer 
                        where playing=1 
                        AND eventid = {eventid}
                        and streamid={streamid} 
                        and uid is not null)
                UNION ALL
                (select date, guestid as userid_count 
                from statplayer 
                where playing=1 
                AND eventid = {eventid}
                and streamid={streamid}
                and guestid is not null)) as t1
                group by t1.date
                order by t1.date) as online_plot
               '''
        table = pd.read_sql_query(con=dbConnection, sql=sql)
        
        dbConnection.close()
        return table
        
    dataonline_table = await dataonline_table()
    
    online_labels = dataonline_table['date'][0]
    online_data = dataonline_table['usercount'][0]


    return templates.TemplateResponse("update_drill/data_online.html", {"request": request,
                                                     'plot_online_data':online_data,
                                                     'plot_online_label':online_labels
                                                    })

@routerDrill.post('/dataunique_drill/{id}/{sid}', tags=['dataOnline'], response_class=HTMLResponse)
async def update(request:Request,id:int, sid:int):
    async def dataset_dataunique(eventid=id, streamid=sid):
        engine = create_engine(f'postgresql://{c.user}:{c.password}@{c.host}:{c.port}/{c.database}') 
        dbConnection = engine.connect()
        sql = f'''
                select cast(t1.date as TEXT) as date, count(t1.uid) from (
                    select uid, min(date) as date 
                    from statplayer 
                    where uid is not null 
                    and playing=1 
                    and eventid = {eventid}
                    and streamid = {streamid} 
                    group by uid
                UNION ALL
                select guestid, min(date) as date 
                from statplayer 
                where guestid is not null 
                and playing=1
                and eventid = {eventid}
                and streamid = {streamid} 
                group by guestid) as t1
                group by date
                order by date
               '''
        table = pd.read_sql_query(con=dbConnection, sql=sql)
        dbConnection.close()
        return table
    
    dataset_dataunique = await dataset_dataunique()

    unique_labels = list(dataset_dataunique['date'])
    unique_data = list(dataset_dataunique['count'])
    
    return templates.TemplateResponse("update_drill/data_unique_online.html", {"request": request,
                                                                  'unique_labels':unique_labels,
                                                                  'unique_data':unique_data  
                                                                    }) 
    
@routerDrill.post('/tablestat_drill/{id}/{sid}', tags=['table status'], response_class=HTMLResponse)
async def index(request: Request, id:int, sid:int):
    async def dataset_table(eventid=id, streamid=sid):
        engine = create_engine(f'postgresql://{c.user}:{c.password}@{c.host}:{c.port}/{c.database}') 
        dbConnection = engine.connect()
        sql = f'''
                select * from (
                    select statplayer.uid as Зритель, statplayer.playing as Статус from statplayer 
                    inner join 
                    (select MAX(date) as date, uid 
                    from statplayer 
                    where uid is not NULL 
                    and eventid = {eventid}
                    AND streamid = {streamid} 
                    group by uid order by date) as t1 on t1.uid=statplayer.uid and t1.date=statplayer.date
                    WHERE eventid = {eventid} and streamid = {streamid}  
                    UNION ALL 
                    select statplayer.guestid, statplayer.playing 
                    from statplayer 
                    inner join (
                        select MAX(date) as date, guestid 
                        from statplayer 
                        where guestid is not NULL 
                        and eventid = {eventid}
                        AND streamid = {streamid} 
                        group by guestid order by date) as t1 on t1.guestid=statplayer.guestid and t1.date=statplayer.date
                        where eventid = {eventid} and streamid = {streamid} ) as tablestatus 
                    order by Статус, Зритель asc
               '''
        
        table_table = pd.read_sql_query(con=dbConnection, sql=sql) 
        dbConnection.close()
        return table_table
        
    dataset_table = await dataset_table()
    
    dataset_table['Активность'] = 0
    dataset_table.loc[dataset_table['Статус']==1,'Активность'] = ''

    
    dataset_table.loc[dataset_table['Статус']==1,'Статус'] = 'online'
    dataset_table.loc[dataset_table['Статус']==0,'Статус'] = 'offline'
    
    dataset_table['Зритель'] = dataset_table['Зритель'].astype(np.int64)
    dataset_table = dataset_table[['Статус', 'Зритель', 'Активность']]
    
    heading = dataset_table.columns
    contents_list = []
    for i,j in dataset_table.iterrows():
        contents_list.append(list(j))
    
    return templates.TemplateResponse('update_drill/table_status.html', {'request':request,
                                                            'heading':heading,
                                                            'contents':contents_list})

@routerDrill.post('/card_unique_drill/{id}/{sid}', tags=['unique numbers'], response_class=HTMLResponse)
async def update(request:Request, id:int, sid:int):
    async def dataset_dataunique(eventid=id, streamid=sid):
        engine = create_engine(f'postgresql://{c.user}:{c.password}@{c.host}:{c.port}/{c.database}') 
        dbConnection = engine.connect()
        sql = f'''
                select SUBSTRING(cast(t1.date as TEXT),12) as date, count(t1.uid) from (
                    select uid, min(date) as date 
                    from statplayer 
                    where uid is not null and eventid = {eventid}
                    AND streamid = {streamid} 
                    and playing=1 
                    group by uid
                UNION ALL
                select guestid, min(date) as date 
                from statplayer 
                where guestid is not null and eventid = {eventid}
                AND streamid = {streamid} 
                and playing=1
                
                
                group by guestid) as t1
                group by date
                order by date
               '''
        table = pd.read_sql_query(con=dbConnection, sql=sql)
        dbConnection.close()
        return table  
        
    dataunique = await dataset_dataunique()
    
    sum_uniqueusers = sum(dataunique['count'])
        
    return templates.TemplateResponse('update_drill/card_unique.html', {'request':request,'sum_unique':sum_uniqueusers}) 

@routerDrill.post('/unique_watch/{id}/{sid}', tags=['unique numbers'], response_class=HTMLResponse)
async def update(request:Request, id:int, sid:int):
    async def dataset_dataunique(eventid=id, streamid=sid):
        engine = create_engine(f'postgresql://{c.user}:{c.password}@{c.host}:{c.port}/{c.database}') 
        dbConnection = engine.connect()
        sql = f'''
                select SUBSTRING(cast(t1.date as TEXT),12) as date, count(t1.uid) from (
                    select uid, min(date) as date 
                    from statplayer 
                    where uid is not null and eventid = {eventid}
                    AND streamid = {streamid} 
                    and playing=1 
                    group by uid
                UNION ALL
                select guestid, min(date) as date 
                from statplayer 
                where guestid is not null and eventid = {eventid}
                AND streamid = {streamid} 
                and playing=1
                
                
                group by guestid) as t1
                group by date
                order by date
               '''
        table = pd.read_sql_query(con=dbConnection, sql=sql)
        dbConnection.close()
        return table  
        
    dataunique = await dataset_dataunique()
    
    sum_uniqueusers = sum(dataunique['count'])
        
    return templates.TemplateResponse('update_drill/unique_watch.html', {'request':request,'sum_unique':sum_uniqueusers}) 

