from sqlalchemy.orm import Session
from . import models
from sqlalchemy import insert,update
import boto3
import gzip
import shutil
import csv
import pandas as pd
import json


def is_exist_ssp(db,ssp_id,ssp_name):
    result=db.query(models.SSP).filter(models.SSP.ssp_id==ssp_id).first()
    if result:
        return result
    else:
        db_ssp = models.SSP(
            name=ssp_name,
            ssp_id=ssp_id,
        )
        db.add(db_ssp)
        db.commit()
        db.refresh(db_ssp)
        return db_ssp

def is_exist_dsp(db,dsp_id,dsp_name):
    result=db.query(models.DSP).filter(models.DSP.dsp_id==dsp_id).first()
    if result:
        return result
    else:
        db_dsp = models.DSP(
            name=dsp_name,
            dsp_id=dsp_id,
        )
        db.add(db_dsp)
        db.commit()
        db.refresh(db_dsp)
        return db_dsp


def get_all_data(db: Session):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket('bucket')
    file_name=""
    files = bucket.objects.filter()
    files = [obj.key for obj in sorted(files, key=lambda x: x.last_modified, 
        reverse=True)]
    for obj in files:
        file_name=obj
        break

    bucket.download_file(file_name, 'result.gzip')
    df = pd.read_csv('result.gzip', compression='gzip')
    df.to_csv('result.csv', sep='\t', encoding='utf-8')
    df = df.reset_index()
    for index, row in df.iterrows():
        ssp_info = is_exist_ssp(
            db=db,
            ssp_id=row['SSP ID'],
            ssp_name=row['SSP Name']
        )
        ssp=None
        try:
            ssp=json.loads(row['Bid Request SSP'])
        except:
            pass
        obj={}
        if ssp:
            obj['lat']=0
            obj['lon']=0
            obj['country']=''
            obj['city']=''
            obj['zip']=''

            obj['device_ip']=''
            obj['device_os']=''
            obj['device_os_version']=''
            obj['device_make']=''
            obj['device_model']=''
            obj['device_carrier']=''
            obj['device_user_agent']=''

            obj['app_version']=''
            obj['app_name']=''
            obj['app_bundle']=''
            obj['app_keywords']=''
            obj['app_store_url']=''

            if "geo" in ssp['device']:
                if "lat" in ssp['device']['geo']:
                    obj['lat']=ssp['device']['geo']['lat']

                if "lon" in ssp['device']['geo']:
                    obj['lon']=ssp['device']['geo']['lon']

                if "country" in ssp['device']['geo']:
                    obj['country']=ssp['device']['geo']['country']

                if "city" in ssp['device']['geo']:
                    obj['city']=ssp['device']['geo']['city']

                if "zip" in ssp['device']['geo']:
                    obj['zip']=ssp['device']['geo']['zip']

            if "ua" in ssp['device']:
                obj['device_user_agent']=ssp['device']['ua']

            if "ip" in ssp['device']:
                obj['device_ip']=ssp['device']['ip']

            if "os" in ssp['device']:
                obj['device_os']=ssp['device']['os']

            if "osv" in ssp['device']:
                obj['device_os_version']=ssp['device']['osv']

            if "make" in ssp['device']:
                obj['device_make']=ssp['device']['make']

            if "model" in ssp['device']:
                obj['device_model']=ssp['device']['model']

            if "carrier" in ssp['device']:
                obj['device_carrier']=ssp['device']['carrier']

            if "ver" in ssp['app']:
                obj['app_version']=ssp['app']['ver']

            if "bundle" in ssp['app']:
                obj['app_bundle']=ssp['app']['bundle']

            if "name" in ssp['app']:
                obj['app_name']=ssp['app']['name']

            if "keywords" in ssp['app']:
                obj['app_keywords']=ssp['app']['keywords']
            
            if "storeurl" in ssp['app']:
                obj['app_store_url']=ssp['app']['storeurl']
            
            db_ssp_request = models.SSP_REQUEST(
                ssp_id = ssp_info.id,
                bid_floor = ssp['imp'][0]['bidfloor'],
                time_max = ssp['tmax'],
                country = obj['country'],
                city = obj['city'],
                zip_code = obj['zip'],
                app_version = obj['app_version'],
                app_name = obj['app_name'],
                app_bundle = obj['app_bundle'],
                app_keywords = obj['app_keywords'],
                app_store_url = obj['app_store_url'],
                device_make = obj['device_make'],
                device_model = obj['device_model'],
                device_carrier = obj['device_carrier'],
                device_user_agent = obj['device_user_agent'],
                device_ip = obj['device_ip'],
                device_os = obj['device_os'],
                device_os_version = obj['device_os_version'],
                location = f"POINT({obj['lat']} {obj['lon']})"
            )
            db.add(db_ssp_request)
            db.commit()
            db.refresh(db_ssp_request)

        ssp_response=None
        try:
            ssp_response=json.loads(row['SSP Bid Response'])
        except:
            pass
        obj={}
        obj['id']=None
        obj['price']=0
        obj['height']=0
        obj['weight']=0
        obj['domain']=""
        obj['url']=""
        obj['currency']=""
        if ssp_response:
            obj['id']=ssp_response['id']
            if "cur" in ssp_response:
                obj['currency']=ssp_response['cur']
            if "seatbid" in ssp_response:
                if len(ssp_response['seatbid']) == 1:
                    if len(ssp_response['seatbid'][0]['bid'])==1:
                        bid_data=ssp_response['seatbid'][0]['bid'][0]
                        if "h" in bid_data:
                            obj['height']=bid_data['h']
                        if "w" in bid_data:
                            obj['weight']=bid_data['w']
                        if "adomain" in bid_data:
                            obj['domain']=",".join(bid_data['adomain'])
                        if "iurl" in bid_data:
                            obj['price']=bid_data['iurl']
                        if "price" in bid_data:
                            obj['price']=bid_data['price']
                        

        db_ssp_response = models.SSP_RESPONSE(
             ssp_id = ssp_info.id,
             ssp_response_id= obj['id'],
             price= obj['price'],
             height= obj['height'],
             weight= obj['weight'],
             domain= obj['domain'],
             url= obj['url'],
             currency= obj['currency'],
        )
        db.add(db_ssp_response)
        db.commit()
        db.refresh(db_ssp_response)


        dsp_info = is_exist_dsp(
            db=db,
            dsp_id=row['DSP ID'],
            dsp_name=row['DSP Name']
        )
        dsp=None
        try:
            dsp=json.loads(row['Bid Request DSP'])
        except:
            pass
        obj={}
        if dsp:
            obj['lat']=0
            obj['lon']=0
            obj['country']=''
            obj['city']=''
            obj['zip']=''

            obj['device_ip']=''
            obj['device_os']=''
            obj['device_os_version']=''
            obj['device_make']=''
            obj['device_model']=''
            obj['device_carrier']=''
            obj['device_user_agent']=''

            obj['app_version']=''
            obj['app_name']=''
            obj['app_bundle']=''
            obj['app_keywords']=''
            obj['app_store_url']=''

            if "geo" in dsp['device']:
                if "lat" in dsp['device']['geo']:
                    obj['lat']=dsp['device']['geo']['lat']

                if "lon" in dsp['device']['geo']:
                    obj['lon']=dsp['device']['geo']['lon']

                if "country" in dsp['device']['geo']:
                    obj['country']=dsp['device']['geo']['country']

                if "city" in dsp['device']['geo']:
                    obj['city']=dsp['device']['geo']['city']

                if "zip" in dsp['device']['geo']:
                    obj['zip']=dsp['device']['geo']['zip']

            if "ua" in dsp['device']:
                obj['device_user_agent']=dsp['device']['ua']

            if "ip" in dsp['device']:
                obj['device_ip']=dsp['device']['ip']

            if "os" in dsp['device']:
                obj['device_os']=dsp['device']['os']

            if "osv" in dsp['device']:
                obj['device_os_version']=dsp['device']['osv']

            if "make" in dsp['device']:
                obj['device_make']=dsp['device']['make']

            if "model" in dsp['device']:
                obj['device_model']=dsp['device']['model']

            if "carrier" in dsp['device']:
                obj['device_carrier']=dsp['device']['carrier']

            if "ver" in dsp['app']:
                obj['app_version']=dsp['app']['ver']

            if "bundle" in dsp['app']:
                obj['app_bundle']=dsp['app']['bundle']

            if "name" in dsp['app']:
                obj['app_name']=dsp['app']['name']

            if "keywords" in dsp['app']:
                obj['app_keywords']=dsp['app']['keywords']
            
            if "storeurl" in dsp['app']:
                obj['app_store_url']=dsp['app']['storeurl']
            
            db_dsp_request = models.DSP_REQUEST(
                dsp_id = dsp_info.id,
                bid_floor = ssp['imp'][0]['bidfloor'],
                time_max = ssp['tmax'],
                country = obj['country'],
                city = obj['city'],
                zip_code = obj['zip'],
                app_version = obj['app_version'],
                app_name = obj['app_name'],
                app_bundle = obj['app_bundle'],
                app_keywords = obj['app_keywords'],
                app_store_url = obj['app_store_url'],
                device_make = obj['device_make'],
                device_model = obj['device_model'],
                device_carrier = obj['device_carrier'],
                device_user_agent = obj['device_user_agent'],
                device_ip = obj['device_ip'],
                device_os = obj['device_os'],
                device_os_version = obj['device_os_version'],
                location = f"POINT({obj['lat']} {obj['lon']})"
            )
            db.add(db_dsp_request)
            db.commit()
            db.refresh(db_dsp_request)
        
        dsp_response=None
        try:
            dsp_response=json.loads(row['DSP Bid Response'])
        except:
            pass
        obj={}
        obj['id']=None
        obj['price']=0
        obj['height']=0
        obj['weight']=0
        obj['domain']=""
        obj['url']=""
        obj['currency']=""
        if dsp_response:
            obj['id']=dsp_response['id']
            if "cur" in dsp_response:
                obj['currency']=dsp_response['cur']
            if "seatbid" in dsp_response:
                if len(dsp_response['seatbid']) == 1:
                    if len(dsp_response['seatbid'][0]['bid'])==1:
                        bid_data=dsp_response['seatbid'][0]['bid'][0]
                        if "h" in bid_data:
                            obj['height']=bid_data['h']
                        if "w" in bid_data:
                            obj['weight']=bid_data['w']
                        if "adomain" in bid_data:
                            obj['domain']=",".join(bid_data['adomain'])
                        if "iurl" in bid_data:
                            obj['price']=bid_data['iurl']
                        if "price" in bid_data:
                            obj['price']=bid_data['price']

        db_dsp_response = models.DSP_RESPONSE(
             dsp_id = dsp_info.id,
             dsp_response_id = obj['id'],
             price = obj['price'],
             height = obj['height'],
             weight = obj['weight'],
             domain = obj['domain'],
             url = obj['url'],
             currency = obj['currency'],
        )
        db.add(db_dsp_response)
        db.commit()
        db.refresh(db_dsp_response)

    return []    


