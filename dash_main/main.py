import psycopg2
import datetime
import pandas as pd
from decouple import config as c
from sqlalchemy import create_engine
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi import Request
from fastapi.templating import Jinja2Templates
from fastapi import APIRouter


routerMain = APIRouter()



templates = Jinja2Templates(directory="templates")

# main dashboard
@routerMain.get('/stat/{id}', tags=['main route'], response_class=HTMLResponse)
async def index(request: Request, id:int, title='index'):
    
    # number of watching card
    async def dataset_watching(eventid=id):
        engine = create_engine(f'postgresql://{c.user}:{c.password}@{c.host}:{c.port}/{c.database}') 
        dbConnection = engine.connect()
        sql =  f'''
                    select COUNT(counttable.uid) 
                    from( select statplayer.uid 
                          from statplayer 
                          inner join 
                          (select MAX(date) as date, uid 
                          from statplayer 
                          where uid is not NULL and eventid = {eventid}
                          
                          
                          group by uid order by date) as t1 on t1.uid=statplayer.uid and t1.date=statplayer.date 
                          where playing = 1 
                    UNION ALL 
                    select statplayer.guestid 
                    from statplayer  
                    inner join
                    (select MAX(date) as date, guestid 
                    from statplayer 
                    where guestid is not NULL and eventid = {eventid}
                    
                     
                    group by guestid order by date) as t1 on t1.guestid=statplayer.guestid and t1.date=statplayer.date 
                    where playing = 1 ) as counttable
                '''       
        table_watching = pd.read_sql_query(con=dbConnection, sql=sql)
        dbConnection.close()
        return table_watching
    
    try:
        dataset_watching_org = await dataset_watching()
        number_watching = list(dataset_watching_org.iloc[0])[0]
    except:
        number_watching = 0
        
    # number of on pauses card
    async def dataset_pause(eventid = id):
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
                    where uid is not NULL and eventid = {eventid}
                    
                     
                    group by uid 
                    order by date) as t1 on t1.uid=statplayer.uid and t1.date=statplayer.date 
                    where playing = 0 
                UNION ALL 
                select statplayer.guestid 
                from statplayer  
                inner join 
                (select MAX(date) as date, guestid 
                from statplayer 
                where guestid is not NULL and eventid = {eventid}
                
                 
                group by guestid 
                order by date) as t1 on t1.guestid=statplayer.guestid and t1.date=statplayer.date 
                where playing = 0 ) as counttable

               '''
                
        table_pause = pd.read_sql_query(con=dbConnection, sql=sql)
        dbConnection.close()
        return table_pause
    
    try:
        dataset_pause = await dataset_pause()
        number_pause = list(dataset_pause.iloc[0])[0]
    except:
        number_pause = 0
    
    # Computing the AVD (average view duration) card
    async def dataset_avd(eventid = id):
        engine = create_engine(f'postgresql://{c.user}:{c.password}@{c.host}:{c.port}/{c.database}') 
        dbConnection = engine.connect()
        sql =  f'''
                    select round((sum(tableavd.playbackwatch)*0.0167)/count(tableavd.uid),2) 
                    from(
                        select uid, playbackwatch 
                        from statplayer 
                        where playing = 1 
                        AND uid is not null and eventid = {eventid}
                        
                        
                    UNION ALL
                    select guestid, playbackwatch 
                    from statplayer 
                    where playing = 1 
                    and guestid is not null and eventid = {eventid}) as tableavd 
                '''
           
        table_avd = pd.read_sql_query(con=dbConnection, sql=sql)
        dbConnection.close()
        return table_avd
    
    try:
        dataset_avd_org = await dataset_avd()
        dataset_avd = list(dataset_avd_org.iloc[0])[0]
    except:
        dataset_avd = 0
    
    # time card
    time = datetime.datetime.now().time().strftime('%H:%M')
    
    
    # plot data online
    async def dataonline_table(eventid = id):
        engine = create_engine(f'postgresql://{c.user}:{c.password}@{c.host}:{c.port}/{c.database}') 
        dbConnection = engine.connect()
        sql = f'''             
                
            select array_agg(date_date) as date_date, array_agg(usercount) as usercount 
                from(
                    select SUBSTRING(cast(t1.date as TEXT),0) as date_date, COUNT(t1.userid_count) as usercount
                    from(
                        (select date, uid as userid_count 
                        from statplayer 
                        where playing=1 
                        and uid is not null
                        and eventid = {eventid})
                UNION ALL
                (select date, guestid as userid_count 
                from statplayer 
                where playing=1 
                and guestid is not null and eventid = {eventid})) as t1
                group by t1.date
                order by t1.date) as online_plot
				
                
               '''
               
               
        table = pd.read_sql_query(con=dbConnection, sql=sql)
        
        dbConnection.close()
        return table
    dataonline_table = await dataonline_table()
    print('date_date', dataonline_table['date_date'][0])
    print('usercount', dataonline_table['usercount'][0])
    try:    
        online_labels = dataonline_table['date_date'][0]
        online_data = dataonline_table['usercount'][0]
    except:
        online_labels = ''
        online_data = 0
        
    # plot data offline
    async def dataoffline_table(eventid = id):
        engine = create_engine(f'postgresql://{c.user}:{c.password}@{c.host}:{c.port}/{c.database}') 
        dbConnection = engine.connect()
        sql = f'''                
                select date, usercount 
                from(
                    select cast(t1.date as TEXT) as date, COUNT(t1.userid_count) as usercount
                    from(
                        (select date, uid as userid_count 
                        from statplayer 
                        where playing=0 
                        and uid is not null and eventid = {eventid})
                UNION ALL
                (select date, guestid as userid_count 
                from statplayer 
                where playing=0 
                and guestid is not null and eventid = {eventid})) as t1
                group by t1.date
                order by t1.date) as offline_plot
               '''
        dataoffline_table = pd.read_sql_query(con=dbConnection, sql=sql)
        
        dbConnection.close()
        return dataoffline_table
    
    dataoffline_table = await dataoffline_table()
    
    try:
        offline_data = list(dataoffline_table['usercount'])
        offline_labels = list(dataoffline_table['date'])
    except:
        offline_labels = ''
        offline_data = 0

    # offline_updated = dataoffline_table.iloc[-1]['usercount']
    
    # plot double plot Unique and offline
    async def dataset_dataunique(eventid = id):
        engine = create_engine(f'postgresql://{c.user}:{c.password}@{c.host}:{c.port}/{c.database}') 
        dbConnection = engine.connect()
        sql = f'''
                select cast(t1.date as TEXT) as date, count(t1.uid) from (
                    select uid, min(date) as date 
                    from statplayer 
                    where uid is not null and eventid = {eventid}
                    and playing=1 
                    group by uid
                UNION ALL
                select guestid, min(date) as date 
                from statplayer 
                where guestid is not null and eventid = {eventid}
                and playing=1
                
                
                group by guestid) as t1
                group by date
                order by date
               '''
        table = pd.read_sql_query(con=dbConnection, sql=sql)
        dbConnection.close()
        return table  
        
    dataunique = await dataset_dataunique()
    
    try:
        unique_data = list(dataunique['count'])
        unique_labels = list(dataunique['date'])
    except:
        unique_labels = ''
        unique_data = 0
        
    sum_uniqueusers = sum(dataunique['count'])
      
    # table for the main page (streamid, watching, avd)
    async def tablemain_dataset(eventid = id):
        engine = create_engine(f'postgresql://{c.user}:{c.password}@{c.host}:{c.port}/{c.database}') 
        dbConnection = engine.connect()
        sql1 = f'''
                SELECT COUNT(t3.userid), t3.streamid from(
                    select statplayer.guestid as userid, statplayer.streamid from statplayer
                    inner join
                    (select MAX(date) as date, streamid, guestid
                          from statplayer 
                          where guestid is not NULL and eventid = {eventid}
                          group by streamid, guestid order by streamid, date) as t1 on t1.guestid = statplayer.guestid and t1.date = statplayer.date and t1.streamid = statplayer.streamid
						  where playing=1
                    union all
                    select statplayer.uid as userid, statplayer.streamid from statplayer
                    inner join
                    (select MAX(date) as date, uid, streamid
                                            from statplayer 
                                            where uid is not NULL and eventid = {eventid}
                                            group by streamid, uid order by streamid, date) as t2 on t2.uid = statplayer.uid and t2.date = statplayer.date and t2.streamid = statplayer.streamid
                                            where playing = 1) as t3
                    group by t3.streamid
                '''
        sql2 = f'''
                select streamid,round((sum(tableavd.playbackwatch)*0.0167)/count(tableavd.uid),2) as avd
                from(
                        select uid, streamid, playbackwatch 
                        from statplayer 
                        where playing = 1 and eventid = {eventid}
                        AND uid is not null 
                    UNION ALL
                    select guestid, streamid, playbackwatch 
                    from statplayer 
                    where playing = 1 and eventid = {eventid}
                    and guestid is not null) as tableavd
                    group by streamid
                '''
        table1 = pd.read_sql_query(con=dbConnection, sql=sql1)
        table2 = pd.read_sql_query(con=dbConnection, sql=sql2)
        dbConnection.close()
        total_table=[table1,table2]
        return total_table
    try:
        total_table = await tablemain_dataset()
        table1 = total_table[0]
        table2 = total_table[1]
        table_main_page = pd.merge(right=table1, left=table2, how='inner', on='streamid')
        table_main_page = table_main_page[['streamid','count','avd']].rename(columns={'streamid':'Сессионный зал','count':'Смотрят','avd':'Среднее длительность'}).sort_values(by='Сессионный зал')
        table_main_page['Сессионный зал'] = table_main_page['Сессионный зал'].astype(str)
        table_main_page['Смотрят'] = table_main_page['Смотрят'].astype(str) + ' человек'
        
        contents_list = []
        for i,j in table_main_page.iterrows():
            contents_list.append(list(j))
    except:
        contents_list=['','','']
    return templates.TemplateResponse("event.html", {"request": request, 'title':title, 'watch':number_watching,
                                                     'pause':number_pause , 'avd':dataset_avd, 'time':time,
                                                     
                                                     'plot_online_data':online_data,
                                                     'plot_online_label':online_labels,
                                                     
                                                     'plot_offline_data':offline_data,
                                                     'plot_offline_label':offline_labels,
                                                    #  'offline_updated':offline_updated,
                                                     
                                                     'unique_labels':unique_labels,
                                                     'unique_data':unique_data,
                                                     'sum_unique':sum_uniqueusers,
                                                     
                                                     'table_main_header':list(table_main_page.columns),
                                                     'table_main_rows':contents_list,
                                                     'alldata':table_main_page, 
                                                                                                 
                                                     'id' : id                                                             
                                                     })



# _-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_- _-_-_-_-_- MAIN UPDATING TIME CARD _-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_- 



@routerMain.post('/update_time_main/', tags=['update time main'], response_class=HTMLResponse)
async def update(request:Request):
    time = datetime.datetime.now().time().strftime('%H:%M')
    return templates.TemplateResponse('update_main/updatetime.html', {'request':request, 'time':time})



# _-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_- _-_-_-_- WATCHING UPDATING TIME CARD _-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-



@routerMain.post('/card_watch_main/{id}', tags=['update time main'], response_class=HTMLResponse)
async def update(request:Request, id:int):
    async def dataset_watching(eventid=id):
            engine = create_engine(f'postgresql://{c.user}:{c.password}@{c.host}:{c.port}/{c.database}') 
            dbConnection = engine.connect()
            sql =  f'''
                        select COUNT(counttable.uid) 
                        from( select statplayer.uid 
                            from statplayer 
                            inner join 
                            (select MAX(date) as date, uid 
                            from statplayer 
                            where uid is not NULL and eventid = {eventid}
                            
                            
                            group by uid order by date) as t1 on t1.uid=statplayer.uid and t1.date=statplayer.date 
                            where playing = 1 
                        UNION ALL 
                        select statplayer.guestid 
                        from statplayer  
                        inner join
                        (select MAX(date) as date, guestid 
                        from statplayer 
                        where guestid is not NULL and eventid = {eventid}
                        
                        
                        group by guestid order by date) as t1 on t1.guestid=statplayer.guestid and t1.date=statplayer.date 
                        where playing = 1 ) as counttable
                    '''       
            table_watching = pd.read_sql_query(con=dbConnection, sql=sql)
            dbConnection.close()
            return table_watching
    try:    
        dataset_watching_org = await dataset_watching()
        number_watching = list(dataset_watching_org.iloc[0])[0]
    except:
        number_watching=0
        
    return templates.TemplateResponse('update_main/card_watch.html', {'request':request,'watch':number_watching})



# _-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_- _-_-_-_- ON PAUSE UPDATING TIME CARD _-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-



@routerMain.post('/card_pause_main/{id}', tags=['card_pause'], response_class=HTMLResponse)
async def update(request:Request, id:int):
    async def dataset_pause(eventid = id):
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
                    where uid is not NULL and eventid = {eventid}
                    
                     
                    group by uid 
                    order by date) as t1 on t1.uid=statplayer.uid and t1.date=statplayer.date 
                    where playing = 0 
                UNION ALL 
                select statplayer.guestid 
                from statplayer  
                inner join 
                (select MAX(date) as date, guestid 
                from statplayer 
                where guestid is not NULL and eventid = {eventid}
                
                 
                group by guestid 
                order by date) as t1 on t1.guestid=statplayer.guestid and t1.date=statplayer.date 
                where playing = 0 ) as counttable
               '''
                
        table_pause = pd.read_sql_query(con=dbConnection, sql=sql)
        dbConnection.close()
        return table_pause
    
    try:
        dataset_pause= await dataset_pause()
        number_pause = list(dataset_pause.iloc[0])[0]
    except:
        number_pause = 0
        
    return templates.TemplateResponse('update_main/card_pause.html', {'request':request,'pause':number_pause}) 



# _-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_- _-_-_-_- ON UNIQUE UPDATING TIME CARD _-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-



@routerMain.post('/card_unique_main/{id}', tags=['unique numbers'], response_class=HTMLResponse)
async def update(request:Request, id:int):
    async def dataset_dataunique(eventid = id):
        engine = create_engine(f'postgresql://{c.user}:{c.password}@{c.host}:{c.port}/{c.database}') 
        dbConnection = engine.connect()
        sql = f'''
                select SUBSTRING(cast(t1.date as TEXT),12) as date, count(t1.uid) from (
                    select uid, min(date) as date 
                    from statplayer 
                    where uid is not null and eventid = {eventid}
                    and playing=1 
                    group by uid
                UNION ALL
                select guestid, min(date) as date 
                from statplayer 
                where guestid is not null and eventid = {eventid}
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
        
    return templates.TemplateResponse('update_main/card_unique.html', {'request':request,'sum_unique':sum_uniqueusers}) 



# _-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_- _-_-_-_-_-_ AVD UPDATING TIME CARD _-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_- 



@routerMain.post('/avd_main/{id}', tags=['card_pause'], response_class=HTMLResponse)
async def update(request:Request, id:int):
    async def dataset_avd(eventid = id):
            engine = create_engine(f'postgresql://{c.user}:{c.password}@{c.host}:{c.port}/{c.database}') 
            dbConnection = engine.connect()
            sql =  f'''
                        select round((sum(tableavd.playbackwatch)*0.0167)/count(tableavd.uid),2) 
                        from(
                            select uid, playbackwatch 
                            from statplayer 
                            where playing = 1 
                            AND uid is not null and eventid = {eventid}
                            
                            
                        UNION ALL
                        select guestid, playbackwatch 
                        from statplayer 
                        where playing = 1 
                        and guestid is not null and eventid = {eventid}) as tableavd 
                    '''
            
            table_avd = pd.read_sql_query(con=dbConnection, sql=sql)
            dbConnection.close()
            return table_avd
    
    try:    
        dataset_avd_org = await dataset_avd()
        dataset_avd = list(dataset_avd_org.iloc[0])[0]
    except:
        dataset_avd = 0
        
    return templates.TemplateResponse('update_main/avd.html', {'request':request, 'avd':dataset_avd})



# _-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_- _-_-_-_-_-_ ONLINE-JOIN GRAPH _-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-


@routerMain.post('/dataonline_main/{id}', tags=['dataOnline Main page'], response_class=HTMLResponse)
async def update(request:Request,id:int):
    async def dataonline_table(eventid = id):
        engine = create_engine(f'postgresql://{c.user}:{c.password}@{c.host}:{c.port}/{c.database}') 
        dbConnection = engine.connect()
        sql = f'''
                select array_agg(date_date) as date_date, array_agg(usercount) as usercount 
                from(
                    select SUBSTRING(cast(t1.date as TEXT),0) as date_date, COUNT(t1.userid_count) as usercount
                    from(
                        (select date, uid as userid_count 
                        from statplayer 
                        where playing=1 
                        and uid is not null
                        and eventid = {eventid})
                UNION ALL
                (select date, guestid as userid_count 
                from statplayer 
                where playing=1 
                and guestid is not null and eventid = {eventid})) as t1
                group by t1.date
                order by t1.date) as online_plot
               '''
               
        table = pd.read_sql_query(con=dbConnection, sql=sql)
        
        dbConnection.close()
        return table
        
    dataonline_table = await dataonline_table()
    
    try:
        online_labels = dataonline_table['date_date'][0]
        online_data = dataonline_table['usercount'][0]
    except:
        online_labels = ''
        online_data = 0
    return templates.TemplateResponse("update_main/data_online.html", {'request': request, 
                                                                       'plot_online_data':online_data,
                                                                       'plot_online_label':online_labels})

# _-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_- _- OFFLINE GRAPH _-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-



@routerMain.post('/dataoffline_main/{id}', tags=['Off Main page'], response_class=HTMLResponse)
async def update(request:Request,id:int):
    async def dataoffline_table(eventid = id):
        engine = create_engine(f'postgresql://{c.user}:{c.password}@{c.host}:{c.port}/{c.database}') 
        dbConnection = engine.connect()
        sql = f'''                
                select date, usercount 
                from(
                    select cast(t1.date as TEXT) as date, COUNT(t1.userid_count) as usercount
                    from(
                        (select date, uid as userid_count 
                        from statplayer 
                        where playing=0 
                        and uid is not null and eventid = {eventid})
                UNION ALL
                (select date, guestid as userid_count 
                from statplayer 
                where playing=0 
                and guestid is not null and eventid = {eventid})) as t1
                group by t1.date
                order by t1.date) as offline_plot
               '''
        dataoffline_table = pd.read_sql_query(con=dbConnection, sql=sql)
        
        dbConnection.close()
        return dataoffline_table
    
    dataoffline_table = await dataoffline_table()
    
    try:
        offline_data = list(dataoffline_table['usercount'])
        offline_labels = list(dataoffline_table['date'])
    except:
        offline_labels = ''
        offline_data = 0
    

    
    return templates.TemplateResponse("update_main/data_offline.html", {'request': request,
                                                                       'plot_offline_data':offline_data,
                                                                       'plot_offline_label':offline_labels,})
    
    
    
# _-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_- _- UNIQUE ONLINE _-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-


@routerMain.post('/dataunique_main/{id}', tags=['Unique Main page'], response_class=HTMLResponse)
async def update(request:Request,id:int):
    # plot double plot Unique and offline
    
        
    async def dataset_dataunique(eventid = id):
        engine = create_engine(f'postgresql://{c.user}:{c.password}@{c.host}:{c.port}/{c.database}') 
        dbConnection = engine.connect()
        sql = f'''
                select cast(t1.date as TEXT) as date, count(t1.uid) from (
                    select uid, min(date) as date 
                    from statplayer 
                    where uid is not null and eventid = {eventid}
                    and playing=1 
                    group by uid
                UNION ALL
                select guestid, min(date) as date 
                from statplayer 
                where guestid is not null and eventid = {eventid}
                and playing=1
                group by guestid) as t1
                group by date
                order by date
               '''
        table = pd.read_sql_query(con=dbConnection, sql=sql)
        dbConnection.close()
        return table
    
    dataunique = await dataset_dataunique()
    
    try:
        unique_data = list(dataunique['count'])
        unique_labels = list(dataunique['date'])
    except:
        unique_labels = ''
        unique_data = 0

    # sum_uniqueusers = sum(dataunique['count'])

    return templates.TemplateResponse("update_main/data_unique.html", {'request': request,
                                                                       'unique_labels':unique_labels,
                                                                       'unique_data':unique_data})

# _-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_- _- _- _- _- _- TABLE MAIN PAGE _-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-



@routerMain.post('/tablestat_main/{id}', tags=['table status'], response_class=HTMLResponse)
async def index(request: Request, id:int):
    async def tablemain_dataset(eventid = id):
        engine = create_engine(f'postgresql://{c.user}:{c.password}@{c.host}:{c.port}/{c.database}') 
        dbConnection = engine.connect()
        sql1 = f'''
                SELECT COUNT(t3.userid), t3.streamid from(
                    select statplayer.guestid as userid, statplayer.streamid from statplayer
                    inner join
                    (select MAX(date) as date, streamid, guestid
                          from statplayer 
                          where guestid is not NULL and eventid = {eventid}
                          group by streamid, guestid order by streamid, date) as t1 on t1.guestid = statplayer.guestid and t1.date = statplayer.date and t1.streamid = statplayer.streamid
						  where playing=1
                    union all
                    select statplayer.uid as userid, statplayer.streamid from statplayer
                    inner join
                    (select MAX(date) as date, uid, streamid
                                            from statplayer 
                                            where uid is not NULL and eventid = {eventid}
                                            group by streamid, uid order by streamid, date) as t2 on t2.uid = statplayer.uid and t2.date = statplayer.date and t2.streamid = statplayer.streamid
                                            where playing = 1) as t3
                    group by t3.streamid
                '''
        sql2 = f'''
                select streamid,round((sum(tableavd.playbackwatch)*0.0167)/count(tableavd.uid),2) as avd
                from(
                        select uid, streamid, playbackwatch 
                        from statplayer 
                        where playing = 1 and eventid = {eventid}
                        AND uid is not null 
                    UNION ALL
                    select guestid, streamid, playbackwatch 
                    from statplayer 
                    where playing = 1 and eventid = {eventid}
                    and guestid is not null) as tableavd
                    group by streamid
                '''
        table1 = pd.read_sql_query(con=dbConnection, sql=sql1)
        table2 = pd.read_sql_query(con=dbConnection, sql=sql2)
        dbConnection.close()
        total_table=[table1,table2]
        return total_table
    try:
        total_table = await tablemain_dataset()
        table1 = total_table[0]
        table2 = total_table[1]
        table_main_page = pd.merge(right=table1, left=table2, how='inner', on='streamid')
        table_main_page = table_main_page[['streamid','count','avd']].rename(columns={'streamid':'Сессионный зал','count':'Смотрят','avd':'Среднее длительность'}).sort_values(by='Сессионный зал')
        table_main_page['Сессионный зал'] = table_main_page['Сессионный зал'].astype(str)
        table_main_page['Смотрят'] = table_main_page['Смотрят'].astype(str) + ' человек'
        
    except:
            table_main_page = ['','','']
    return templates.TemplateResponse("update_main/table_main.html", {'request': request,
                                                                        'alldata':table_main_page, 
                                                                        'id':id})
