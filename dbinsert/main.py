import datetime
import pytz
from fastapi import Depends, Request
from .app_jwt.auth.auth_bearer import JWTBearer
from .app_jwt.auth.auth_handler import decodeJWT
from .app_jwt.model import *
from fastapi import APIRouter

routerdb = APIRouter()


@routerdb.get('/api', tags=['JWT'], dependencies=[Depends(JWTBearer())])
async def check_add(request: Request):
    token = request.headers.get('Authorization')
    token = token.split(" ")[1]
    data = decodeJWT(token)
    
    check = ['event','stream','playing','playbackTime','playbackWatch','expires']
    checkuser = ['uid','guest']

    if data == 'expired':
        return {"error":"expired"},401

    if all(i in list(data.keys()) for i in check) and any(i in list(data.keys()) for i in checkuser):
        if data == None:
            return {"error": "Invalid token"}, 401

        try:
            _eventid = data['event']
            _streamid  = data['stream']  
            _playing = data['playing']
            _playbackTime = data['playbackTime']
            _playbackWatch = data['playbackWatch']
                
            if 'uid' in data.keys():
                _uid = data['uid']
                mestumdata.create(
                                    date = datetime.datetime.now(pytz.timezone('Europe/Moscow')).strftime('%m-%d-%Y %H:%M'),
                                    eventid = _eventid,
                                    streamid = _streamid,
                                    uid = _uid,
                                    playing = _playing,
                                    playbackTime = _playbackTime,
                                    playbackWatch = _playbackWatch
                                )

            if 'guest' in data.keys():
                _guestid = data['guest']
                
                mestumdata.create(
                                    date = datetime.datetime.now(pytz.timezone('Europe/Moscow')).strftime('%m-%d-%Y %H:%M'),
                                    eventid = _eventid,
                                    streamid = _streamid,
                                    guestid = _guestid,
                                    playing = _playing,
                                    playbackTime = _playbackTime,
                                    playbackWatch = _playbackWatch
                                )
        except:
            return {'msg':'Missing value'}
        return data
    # otherwise will be safed to jsondata table that saves the received data as json in db
    else:  
        print(data)
        if data == None:
            return {"error": "Invalid token"}, 401
        try:
            _date  = datetime.datetime.now(pytz.timezone('Europe/Moscow')).strftime('%m-%d-%Y %H:%M')
            _jsondata = data
        
        except:
            return {'msg':'Missing value'} 
        jsondata.create(
            date = _date,
            jsondata = _jsondata,
        )
        return data
