from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse
 
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from datetime import datetime 
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.contrib.auth.views import logout
from django.db import connection
from django.conf import settings
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.sessions.models import Session
from django.contrib import messages
import json
from django.http import JsonResponse
from django.core.mail import send_mail
from django.core.mail import send_mail, BadHeaderError
from django.core.mail import EmailMultiAlternatives
import os ,subprocess
from .models import *
# from apscheduler.schedulers.blocking import BlockingScheduler

def S3__Upload(file,path):
    import tinys3
    conn = tinys3.Connection(settings.S3_ACCESS_KEY_ID,settings.S3_SECRET_KEY,tls=True)
    f100 = open(str(settings.MEDIA_ROOT)+'/'+str(file),'rb')
    conn.upload(str('/media/')+str(file),f100,settings.S3_BUCKET) 
    return 1       

def S3_app_Upload(file,path):
    import tinys3
    print(file)
    conn = tinys3.Connection(settings.S3_ACCESS_KEY_ID,settings.S3_SECRET_KEY,tls=True)
    f100 = open(str(settings.MEDIA_ROOT)+'/'+str(file),'rb')
    conn.upload(str('/media/')+str(file),f100,settings.S3_BUCKET) 
    return 1   

def PointTransaction(user_id,method,point_type):
    
    #temp = ''.join(x for x in user_id if x.isdigit())
   # user_id=int(temp)
    cursor = connection.cursor()
    args=[method]
    point=[]

    cursor.execute("SELECT * from rango_pointallotment where is_active='1' and allotment_method  like %s",args)
    result = cursor.fetchall()
    x = cursor.description
    for r in result:
        i = 0
        d = {}
        while i < len(x):
            d[x[i][0]] = r[i]
            i = i+1
        point.append(d)
    if point:
        pnt=Point_transaction()
        pnt.user_id=int(user_id)
        pnt.pa_id=point[0]['id']
        pnt.allotment_name=point[0]['allotment_name']
        pnt.allotment_method=point[0]['allotment_method']
        pnt.is_active=1
        pnt.added_date=datetime.strftime(datetime.now(), '%Y-%m-%d')
        if point_type == str('earn'):
            pnt.earn_value=point[0]['allotment_value']
        else:
            pnt.spent_value=point[0]['allotment_value']
        pnt.save()
    return point
   # return HttpResponse(JsonResponse(point, safe=False), content_type='application/json')

def PointTransactionWithOtherDescription(user_id,method,point_type,model_name,model_value,product_request_id):
    import datetime
    from datetime import datetime
    import time
    args=[model_value]
    cursor = connection.cursor()
    prargs=[product_request_id]
    pr_request=[]
    cursor.execute("SELECT rldp.PEnhancer_point from rango_product_request pr left join rango_loanfor_day_product rldp on pr.loanforday_product_id=rldp.id where pr.id = %s",prargs)
    result = cursor.fetchall()
    x = cursor.description
    for r in result:
        i = 0
        d = {}
        while i < len(x):
            d[x[i][0]] = r[i]
            i = i+1
        pr_request.append(d)

    product= get_product_detail(model_value)
    lender_detail   =   getusername(product[0]['product_added_by_user_id'])
    if lender_detail[0]['gender'] == str('Male'):
        gender='his'
    else:
        gender='her'

    if method == 'borrow-product':
        pnt=Point_transaction()
        pnt.user_id=int(user_id)
        pnt.pa_id=63
        pnt.allotment_name='Borrow '+product[0]['brand_name']+ ' ' +product[0]['model_name']
        pnt.allotment_method=method
        pnt.is_active=1
        pnt.added_date=datetime.strftime(datetime.now(), '%Y-%m-%d')
        pnt.model_name=model_name
        pnt.model_value=model_value
        pnt.spent_value=int(pr_request[0]['PEnhancer_point'])
        pnt.save()
        send_notification(user_id,'Product','You just sent '+str(pr_request[0]['PEnhancer_point']) +' point to '+str(lender_detail[0]['first_name'])+' '+str(lender_detail[0]['last_name'])+ ' to borrow '+gender+' '+str(product[0]['product_name']))
    if method == 'lend-product':
        pnt=Point_transaction()
        pnt.user_id=int(product[0]['product_added_by_user_id'])
        pnt.pa_id=64
        pnt.allotment_name='Lend '+product[0]['brand_name']+ ' ' +product[0]['model_name']
        pnt.allotment_method=method
        pnt.is_active=1
        pnt.added_date=datetime.strftime(datetime.now(), '%Y-%m-%d')
        pnt.model_name=model_name
        pnt.model_value=model_value
        pnt.earn_value=int(pr_request[0]['PEnhancer_point'])
        pnt.save()
        send_notification(user_id,'Product',pr_request[0]['PEnhancer_point']+ 'Point Added for '+str(product[0]['product_name'])+' Shipping')
    if method == 'withdrawn-product':
        pnt=Point_transaction()
        pnt.user_id=int(user_id)
        pnt.pa_id=63
        pnt.allotment_name='Withdrawn '+product[0]['brand_name']+ ' ' +product[0]['model_name']
        pnt.allotment_method=method
        pnt.is_active=1
        pnt.added_date=datetime.strftime(datetime.now(), '%Y-%m-%d')
        pnt.model_name=model_name
        pnt.model_value=model_value
        pnt.earn_value=int(pr_request[0]['PEnhancer_point'])
        pnt.save()
        send_notification(user_id,'Product',str(pr_request[0]['PEnhancer_point']) + ' Point return for '+str(product[0]['model_name']) + ' Shipping')
    return pnt
def get_category_list(max_results=0, starts_with=''):
    cat_list = []
    if starts_with:
        cat_list = Category.objects.filter(name__startswith=starts_with)
    else:
        cat_list = Category.objects.all()

    if max_results > 0:
        if (len(cat_list) > max_results):
            cat_list = cat_list[:max_results]

    return cat_list
def getcategory(pid=0):
    category=[]
    args=[pid]
    cursor = connection.cursor()
    cursor.execute('SELECT * from blog_category where is_active = 1 and pid=%s ',args)
    result = cursor.fetchall()

    x = cursor.description
    for r in result:
        i = 0
        d = {}
        while i < len(x):
            d[x[i][0]] = r[i]
            i = i+1
        category.append(d)
    return category
def newstotallike(news_id=0):
    like=[]
    args=[news_id]
    cursor = connection.cursor()
    cursor.execute('SELECT COALESCE(SUM(`like`),0) as totlike, COALESCE(SUM(`dislike`),0)as totdislike  from rango_newslike where news_id=%s ',args)
    result = cursor.fetchall()
    #print(result)
    x = cursor.description
    for r in result:
        i = 0
        d = {}
        while i < len(x):
            d[x[i][0]] = r[i]
            i = i+1
        like.append(d)

    return like
def reviewtotallike(id=0):
    like=[]
    args=[id]
    cursor = connection.cursor()
    cursor.execute('SELECT COALESCE(SUM(`like`),0) as totlike, COALESCE(SUM(`dislike`),0)as totdislike  from rango_productreview_like where Product_review_id = %s ',args)
    result = cursor.fetchall()
    #print(result)
    x = cursor.description
    for r in result: 
        i = 0
        d = {}
        while i < len(x):
            d[x[i][0]] = r[i]
            i = i+1
        like.append(d)

    return like
def check_user_for_review(Product_review_id=0,product_id=0,user_id=0):
    like=[]
    args=[Product_review_id,product_id,user_id]
    cursor = connection.cursor()
    cursor.execute('SELECT `like`,`dislike` from rango_productreview_like where Product_review_id = %s and product_id = %s and user_id= %s',args)
    result = cursor.fetchall()
    #print(result)
    x = cursor.description
    for r in result: 
        i = 0
        d = {}
        while i < len(x):
            d[x[i][0]] = r[i]
            i = i+1
        like.append(d)

    return like
def newstotalcommentlike(comment_id=0):
    like=[]
    args=[comment_id]
    cursor = connection.cursor()
    cursor.execute('SELECT COALESCE(SUM(`like`),0) as totlike, COALESCE(SUM(`dislike`),0)as totdislike   from rango_newscomment_like where comment_id=%s ',args)
    result = cursor.fetchall()
    #print(result)
    x = cursor.description
    for r in result:
        i = 0
        d = {}
        while i < len(x):
            d[x[i][0]] = r[i]
            i = i+1
        like.append(d)

    return like
def commentreply(comment_id=0,user_id=0):
    reply=[]
    args=[comment_id]
    cursor = connection.cursor()
    cursor.execute('SELECT nc.* , u.first_name,u.last_name,up.picture from rango_newscomment nc inner join auth_user u on u.id=nc.user_id left join rango_userprofile up on u.id=up.user_id  where nc.comment_type="reply" and nc.p_comment_id=%s order by nc.id desc',args)
    result = cursor.fetchall()
    x = cursor.description
    for r in result:
        i = 0
        d = {}
        while i < len(x):
            d[x[i][0]] = r[i]
            i = i+1
        totlike=newstotalcommentlike(d['id']);
        d['check_user_comment_like']=check_user_for_commentlike(d['id'],user_id) 
        d['like']=totlike 
        reply.append(d)
    return reply
def recentactivity(activity='',meta_key='',metavalue=0,user_id=0):
    cursor = connection.cursor()

    parent_meta         = str(activity)
    parent_metavalue    = str(metavalue)
    args=[metavalue]
    if activity == 'newscomment':
        cursor.execute("SELECT news_id from rango_newscomment where id=%s",args)
        result=cursor.fetchone()
        parent_metavalue = result[0]
        parent_meta='news'
    if activity == 'newscomment_reply':
        cursor.execute("SELECT news_id from rango_newscomment where id=%s",args)
        result=cursor.fetchone()
        parent_metavalue = result[0]
        parent_meta='news'
    if activity == 'product_review':
        cursor.execute("SELECT product_id from rango_product_review where id=%s",args)
        result=cursor.fetchone()
        parent_metavalue = result[0]
        parent_meta='product'

    ra=recent_activity()
    ra.user_id=int(user_id)
    ra.activity= activity
    ra.meta_key= str(meta_key)
    ra.metavalue= str(metavalue)
    ra.parent_meta= str(parent_meta)
    ra.parent_metavalue= str(parent_metavalue)
    ra.date=datetime.strftime(datetime.now(), '%Y-%m-%d')
    ra.save()
   # return HttpResponse(JsonResponse(ra, safe=False), content_type='application/json')
def delete_recentactivity(activity='',meta_key='',metavalue=0):
    parent_meta         = str(activity)
    parent_metavalue    = str(metavalue)
    args=[metavalue]
    if activity == 'newscomment':
        cursor.execute("SELECT news_id from rango_newscomment where id=%s",args)
        result=cursor.fetchone()
        if result:
            parent_metavalue = result[0]
            parent_meta='news'
            instance = recent_activity.objects.get(parent_meta=parent_meta,meta_key='id',parent_metavalue=parent_metavalue)
            instance.delete()

    elif activity == 'newscomment_reply':
        cursor.execute("SELECT news_id from rango_newscomment where id=%s",args)
        result=cursor.fetchone()
        if result:
            parent_metavalue = result[0]
            parent_meta='news'
            instance = recent_activity.objects.get(parent_meta=parent_meta,meta_key='id',parent_metavalue=parent_metavalue)
            instance.delete()
    elif activity == 'product_review':
        cursor.execute("SELECT product_id from rango_product_review where id=%s",args)
        result=cursor.fetchone()
        if result:
            parent_metavalue = result[0]
            parent_meta='product'
            instance = recent_activity.objects.get(parent_meta=parent_meta,meta_key='id',parent_metavalue=parent_metavalue)
            instance.delete()
    else:
        # instance = recent_activity.objects.get(parent_meta=parent_meta,meta_key='id',parent_metavalue=parent_metavalue)
        # instance.delete()
        return 0
    
    return 1

def addbrand_lib(brandothername=''):
    #brand_name=' '.join(brandothername.split())
    cursor = connection.cursor()
    args=[brandothername]
    brand=[]
    cursor.execute("SELECT * from rango_brand  where brand_name  like %s",args)
    result = cursor.fetchall()
    x = cursor.description
    for r in result:
        i = 0
        d = {}
        while i < len(x):
            d[x[i][0]] = r[i]
            i = i+1
        brand.append(d)
    if not brand:
        pnt=Brand()
        pnt.brand_name=brandothername
        pnt.is_active='0'
        pnt.save()
        brand_id = cursor.execute('SELECT last_insert_id()')
        brand_id =cursor.fetchone()
        for r in brand_id:
            bid=r
    else:
        bid=brand[0]['id']
    return bid
    #return HttpResponse(JsonResponse(bid, safe=False), content_type='application/json')

def notifcation(user_id=0):
    args=[user_id]
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) from djangoChat_message where is_read=0 AND reciver_user_id=%s",args)
    result=cursor.fetchone()
    return result[0]

def sender_unread(sender_user_id=0,reciver_user_id=0):
    args=[reciver_user_id,sender_user_id]
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) from djangoChat_message where is_read=0 AND reciver_user_id=%s AND sender_user_id=%s",args)
    result=cursor.fetchone()
    return result[0]

def getusername(user_id=0):
    print("asdhgjhasdbjhasdgjasvdgasvdgasvdgasvdjasj")
    args=[user_id]
    user=[]
    cursor = connection.cursor()
    print("SELECT * ,id as profile_id from auth_user where id= %s",args)
    cursor.execute("SELECT * ,id as profile_id from auth_user where id= %s",args)
    # cursor.execute("SELECT u.id,u.is_active,u.username,u.first_name, u.last_name, u.email, u.date_joined,up.picture,up.contact_number,up.dob,up.location, up.gender,up.address1,up.address2,up.city,up.state,up.country,up.country_code,up.state_code,up.zip_code, up.category,up.id as profile_id,up.login_type from auth_user u left join rango_userprofile up on u.id = up.user_id where up.user_id= %s",args)
    result = cursor.fetchall()
    x = cursor.description
    for r in result:
        i = 0
        d = {}
        while i < len(x):
            d[x[i][0]] = r[i]
            i = i+1
        user.append(d)
    if not user:
        cursor.execute("SELECT * ,id as profile_id from auth_user where id= %s",args)
        result = cursor.fetchall()
        x = cursor.description
        for r in result:
            i = 0
            d = {}
            while i < len(x):
                d[x[i][0]] = r[i]
                i = i+1
            user.append(d)

    return user
def getusername_from_username(username=''):
    args=[username]
    user=[]
    cursor = connection.cursor()
    cursor.execute("SELECT u.id,u.is_active,u.username,u.first_name, u.last_name, u.email, u.date_joined,up.picture,up.contact_number,up.dob,up.location, up.gender,up.address1,up.address2,up.city,up.state,up.country,up.country_code,up.state_code,up.zip_code, up.category,up.id as profile_id ,up.login_type from auth_user u left join rango_userprofile up on u.id = up.user_id where u.username= %s",args)
    result = cursor.fetchall()
    x = cursor.description
    for r in result:
        i = 0
        d = {}
        while i < len(x):
            d[x[i][0]] = r[i]
            i = i+1
        user.append(d)
    return user
def addmodel_lib(brand_id=0,model_name='',model_picture='',description='',user_id=0):
    cursor = connection.cursor()
    args=[model_name,brand_id]
    model=[]
    cursor.execute("SELECT * from rango_product_model  where model_name  like %s and  brand_id=%s",args)
    result = cursor.fetchall()
    x = cursor.description
    for r in result:
        i = 0
        d = {}
        while i < len(x):
            d[x[i][0]] = r[i]
            i = i+1
        model.append(d)
    if not model:
        pmt = product_model()
        pmt.model_name=model_name
        pmt.brand_id=brand_id
        pmt.model_picture=model_picture
        # pmt.model_price=model_price
        pmt.description=description
        pmt.user_id=user_id
        pmt.date=datetime.strftime(datetime.now(), '%Y-%m-%d')
        pmt.save()
        brand_id = cursor.execute('SELECT last_insert_id()')
        brand_id =cursor.fetchone()
        for r in brand_id:
            bid=r
    else:
        bid=model[0]['id']
    return bid
def get_product_detail(product_id):
    cursor = connection.cursor()
    args=[product_id]
    product=[]
    cursor.execute("SELECT p.id, p.title as product_name ,p.picture,p.product_added_by_user_id,b.brand_name, m.model_name,m.model_price,p.loanforday_id,p.description,p.product_model_id,p.product_weight,p.product_height,p.product_width,p.product_length FROM rango_product p LEFT JOIN rango_brand b ON b.id = p.brand_id LEFT JOIN rango_product_model m ON m.id = p.product_model_id WHERE p.id =%s ",args)
    result = cursor.fetchall()
    x = cursor.description
    for r in result:
        i = 0
        d = {}
        while i < len(x):
            d[x[i][0]] = r[i]
            i = i+1
        d['PEnhancer_point']=get_minimum_PEnhancer_point(d['id'])
        product.append(d)
    if not product:
        product=[]
    return product
def get_loanforday(loanforday_id):
    cursor = connection.cursor()
    args=[loanforday_id]
    loan=[]
    cursor.execute("SELECT number_days from rango_loan_for_day WHERE id =%s ",args)
    result = cursor.fetchall()
    x = cursor.description
    for r in result:
        i = 0
        d = {}
        while i < len(x):
            d[x[i][0]] = r[i]
            i = i+1
        loan.append(d)
    if loan[0]['number_days']:
        return loan[0]['number_days']
    else:
        return 0
def block_user(borrow_user_id,lender_id):
    import datetime
    from datetime import datetime
    jsonresult = {}
    bluser=Lender_block_user()
    bluser.borrow_user_id=borrow_user_id
    bluser.lend_user_id=lender_id
    bluser.date =   datetime.strftime(datetime.now(), '%Y-%m-%d')
    bluser.save()
    return bluser

# def ship_dwc(borrow_user_id,lender_id,dwc_status,product_id,product_request_id)
#     import datetime
#     from datetime import datetime

#     bluser                      =   shipping_dwc()
#     bluser.borrow_user_id       =   borrow_user_id
#     bluser.lend_user_id         =   lender_id
#     bluser.dwc_status           =   dwc_status
#     bluser.product_id           =   product_id
#     bluser.product_request_id   =   product_request_id
#     bluser.date                 =   datetime.strftime(datetime.now(), '%Y-%m-%d')
#     bluser.save()
#     cursor = connection.cursor()
#     ship_id = cursor.execute('SELECT last_insert_id()')
#     ship_id =cursor.fetchone()
#     for r in ship_id:
#         sid=r
#     return sid
    
def shipping_label_generate(borrow_user_id,lend_user_id,service_code,weight_val,weight_unit,package_code,dimensions_unit,dimensions_length,dimensions_width,dimensions_height,product_id,product_request_id,ship_for,estimated_delivery_date,damage_protected):
    import json
    import requests
    import datetime
    from datetime import datetime
    import time
    jsonresult={}
    payload={}
    shipto={}
    shipform={}
    ship={}
    return_ship=[]
    cursor = connection.cursor()
    import requests
    if ship_for=='lender_to_borrower':
        ship_to = getusername(borrow_user_id)
        ship_form = getusername(lend_user_id)
    elif ship_for=='borrower_to_lender':
        ship_to = getusername(lend_user_id)
        ship_form = getusername(borrow_user_id)

   
    form_download=''
    insurance_claim ='' 
    voided_at =''
    url = "https://api.shipengine.com/v1/labels"
    headers = {'content-type': 'application/json','api-key':'P2u8d78bodWtgE4TPIhECxdJLpCAFqXKQs1icT5s5HE'}
    payload = "{\"shipment\":{\"service_code\":\""+service_code+"\",\"ship_to\":{\"name\":\""+ship_to[0]['first_name']+" "+ship_to[0]['last_name']+"\","
    payload +="\"phone\":\""+ship_to[0]['contact_number']+"\",\"company_name\":\""+ship_to[0]['first_name']+"\",\"address_line1\":\""+ship_to[0]['address1']+"\",\"address_line2\":\""+ship_to[0]['address2']+"\",\"city_locality\":\""+ship_to[0]['city']+"\",\"state_province\":\""+ship_to[0]['state_code']+"\",\"postal_code\":\""+ship_to[0]['zip_code']+"\","
    payload +="\"country_code\":\""+ship_to[0]['country_code']+"\",\"address_residential_indicator\":\"Yes\"},\"ship_from\":{\"name\":\""+ship_form[0]['first_name']+" "+ship_form[0]['last_name']+"\","
    payload +="\"phone\":\""+ship_form[0]['contact_number']+"\",\"company_name\":\""+ship_form[0]['first_name']+"\",\"address_line1\":\""+ship_form[0]['address1']+"\","
    payload +="\"address_line2\":\""+ship_form[0]['address2']+"\",\"city_locality\":\""+ship_form[0]['city']+"\",\"state_province\":\""+ship_form[0]['state_code']+"\",\"postal_code\":\""+ship_form[0]['zip_code']+"\","
    payload +="\"country_code\":\""+ship_to[0]['country_code']+"\",\"address_residential_indicator\":\"No\"},\"packages\":[{\"package_code\":\""+package_code+"\",\"weight\":{\"value\":\""+weight_val+"\",\"unit\":\""+weight_unit+"\"},"
    payload +="\"dimensions\":{\"unit\":\""+dimensions_unit+"\",\"length\":\""+dimensions_length+"\",\"width\":\""+dimensions_width+"\",\"height\":\""+dimensions_height+"\"}}]},\"label_format\":\"pdf\",\"test_label\":\"false\"}"
    jsonresult = {}
    import requests
    headers = {'content-type': 'application/json','api-key':'P2u8d78bodWtgE4TPIhECxdJLpCAFqXKQs1icT5s5HE'}
    url = "https://api.shipengine.com/v1/labels"
    response = requests.request("POST", url, data=payload,headers=headers)
    getres=response.json()
   
    if getres.has_key("errors"):
        label_id                =   '' 
        status                  =   getres['errors'][0]['message']
        shipment_id             =   ''
        ship_date               =   ''  
        created_at              =   '' 
        shipment_currency       =   '' 
        shipment_amount         =   '0.00'
        insurance_cost_currency =   ''
        insurance_cost_amount   =   '0.00'
        tracking_number         =   ''
        is_return_label         =   ''
        is_international        =   ''
        batch_id                =   ''
        carrier_id              =   ''
        service_code            =   ''
        package_code            =   ''
        voided                  =   ''
        label_format            =   ''
        label_layout            =   ''
        trackable               =   ''
        carrier_code            =   ''
        
        tracking_status         =   ''
        label_download          =   ''
        ship['errors']=getres['errors'][0]['message']
    else: 
        label_id                =   getres['label_id']
        status                  =   getres['status']
        shipment_id             =   getres['shipment_id']
        ship_date               =   getres['ship_date']
        created_at              =   getres['created_at']

        shipment_currency       =   getres['shipment_cost']['currency']
        shipment_amount         =   getres['shipment_cost']['amount']

        insurance_cost_currency =   getres['insurance_cost']['currency']
        insurance_cost_amount   =   getres['insurance_cost']['amount']

        tracking_number         =   getres['tracking_number']
        is_return_label         =   getres['is_return_label']
        is_international        =   getres['is_international']
        batch_id                =   getres['batch_id']
        carrier_id              =   getres['carrier_id']
        service_code            =   getres['service_code']
        package_code            =   getres['package_code']
        voided                  =   getres['voided']
        
        label_format            =   getres['label_format']
        label_layout            =   getres['label_layout']
        trackable               =   getres['trackable']
        carrier_code            =   getres['carrier_code']
        tracking_status         =   getres['tracking_status']
        label_download          =   getres['label_download']['href']
        if getres['form_download'] != None:
            form_download== getres['form_download']
        else:
            form_download=  ''
        if getres['insurance_claim']:
            insurance_claim=    getres['insurance_claim']
        else:
            insurance_claim =''     
        if getres['voided_at']:
            voided_at = getres['voided_at']
        else:
            voided_at =''               
    borrow_user_id          =   borrow_user_id
    lend_user_id            =   lend_user_id
    date                    =   time.strftime('%Y-%m-%d %H:%M:%S')
    product_id              =   product_id
    product_request_id      =   product_request_id
    shipping = shipping_detail()
    shipping.label_id                   =   label_id
    shipping.status                     =   status
    shipping.shipment_id                =   shipment_id
    shipping.ship_date                  =   ship_date
    shipping.created_at                 =   created_at
    shipping.shipment_currency          =   shipment_currency
    shipping.shipment_amount            =   shipment_amount
    shipping.insurance_cost_currency    =   insurance_cost_currency
    shipping.insurance_cost_amount      =   insurance_cost_amount
    shipping.tracking_number            =   tracking_number
    shipping.is_return_label            =   is_return_label
    shipping.is_international           =   is_international
    shipping.batch_id                   =   batch_id
    shipping.carrier_id                 =   carrier_id
    shipping.service_code               =   service_code
    shipping.package_code               =   package_code
    shipping.voided                     =   voided
    shipping.voided_at                  =   voided_at
    shipping.label_format               =   label_format
    shipping.label_layout               =   label_layout
    shipping.trackable                  =   trackable
    shipping.carrier_code               =   carrier_code
    shipping.tracking_status            =   tracking_status
    shipping.label_download             =   label_download
    shipping.form_download              =   form_download
    shipping.insurance_claim            =   insurance_claim
    shipping.borrow_user_id             =   borrow_user_id
    shipping.lend_user_id               =   lend_user_id
    shipping.date                       =   date
    shipping.product_id                 =   product_id
    shipping.product_request_id         =   product_request_id
    shipping.ship_for                   =   ship_for
    shipping.damage_protected           =   damage_protected
    shipping.estimated_delivery_date   =   estimated_delivery_date
    shipping.save()
    ship_id = cursor.execute('SELECT last_insert_id()')
    ship_id =cursor.fetchone()
    for r in ship_id:
        shiping_id=r
    ship['shiping_id']=shiping_id
    ship['status']=status
    return ship

    #return HttpResponse(response)
def sendlabel_to_user(user_id,ship_id):
    user= getusername(user_id)
    args=[ship_id]
    res=[]
    cursor = connection.cursor()
    cursor.execute("SELECT label_download,status from rango_shipping_detail where id=%s",args)
    result=cursor.fetchall()
    x = cursor.description
    for r in result:
        i = 0
        d = {}
        while i < len(x):
            d[x[i][0]] = r[i]
            i = i+1
        res.append(d)
   
    #print(res)
    subject = 'Shipping Label Generated'
    from_email = settings.EMAIL_HOST_USER
    to = user[0]['email']
    html_content = 'Dear '+user[0]['first_name']+' '+user[0]['last_name']
    if res[0]['label_download']:
        html_content +=',<br/> New Label has been Generated ,Please download this PDF <br/>'
        html_content += '<a href="'+ res[0]['label_download']+'" target="_blank">' + res[0]['label_download'] + '</a>'
    else:
        html_content +=',<br/> Your Shipping Label Not generate due to  <br/>'
        html_content += '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<b>' + res[0]['status'] + '</b>'
    html_content += '<br/>Thanks Regards,<br/> PEnhancer Team'
    if to and from_email:
        try:
            text_content = '<br/>Thanks Regards,<br/> PEnhancer Team'
            msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            return 'label Send'
        except BadHeaderError:
            return 'Due to some technical problem we are unable to send otp to your mail id'

def request_product_status(prid,status,reason=''):
    import datetime
    from datetime import datetime
    import time
    jsonresult = {}
    pr=[]
    cursor = connection.cursor()
    args=[prid]
    cursor.execute("SELECT * from rango_product_request where id = %s",args)
    result = cursor.fetchall()
    x = cursor.description
    for r in result:
        i = 0
        d = {}
        while i < len(x):
            d[x[i][0]] = r[i]
            i = i+1
        pr.append(d)
   #buyer_id = pr[0]['borrow_user_id']
    #lender_id = pr[0]['lend_user_id'] 
    ship_detail=get_ship_detail(prid)
    product_detail=get_product_detail(pr[0]['product_id'])
    buyer_id = pr[0]['borrow_user_id']
    lender_id = pr[0]['lend_user_id']
    lender_detail   =   getusername(lender_id)
    borrower_detail =   getusername(buyer_id)
    if not borrower_detail:
        borrower_detail=[]
    if not lender_detail:
        lender_detail=[]
    if not product_detail:
        product_detail=[]
    if not ship_detail:
        ship_detail=[]

    if reason == 'blocked by lender':
        block_user(buyer_id,lender_id)
    if status == 'denied':
        send_notification(buyer_id,'Denied','Sorry. Your request was denied by the lender. But we can still be friends.')
        to_update = Product_request.objects.filter(id=prid).update(status=status,reason=str(reason),denied_date=time.strftime('%Y-%m-%d %H:%M:%S'),modify_date=time.strftime('%Y-%m-%d %H:%M:%S'))
    elif status == 'withdrawn':
        
        PointTransactionWithOtherDescription(buyer_id,'withdrawn-product','earn','Product',pr[0]['product_id'],prid)
        send_notification(buyer_id,'Withdrawn Borrower','You withdrew your request. I can`t say it makes me happy, but it`s cool. It`s cool.')
        send_notification(lender_id,'Withdrawn Lender', str(borrower_detail[0]['first_name']) +' '+ str(borrower_detail[0]['last_name']) + ' has withdrawn {his/her} request to borrow your' + str(product_detail[0]['brand_name']) + ' ' + str(product_detail[0]['model_name']) + '.')

        to_update = Product_request.objects.filter(id=prid).update(status=status,reason=reason,withdrawn_date=time.strftime('%Y-%m-%d %H:%M:%S'),modify_date=time.strftime('%Y-%m-%d %H:%M:%S'))
    elif status == 'approved':
        
        send_notification(buyer_id,'Approved','Huzzah! Your borrow request was just approved by '+str(lender_detail[0]['first_name'])+' '+str(lender_detail[0]['last_name'])+'.')
        to_update = Product_request.objects.filter(id=prid).update(status=status,reason=reason,approved_date=time.strftime('%Y-%m-%d %H:%M:%S'),modify_date=time.strftime('%Y-%m-%d %H:%M:%S'))
    elif status == 'pointsent':
        PointTransactionWithOtherDescription(buyer_id,'borrow-product','spent','Product',pr[0]['product_id'],prid)
        
        to_update = Product_request.objects.filter(id=prid).update(status=status,reason=reason,pointsent_date=time.strftime('%Y-%m-%d %H:%M:%S'),modify_date=time.strftime('%Y-%m-%d %H:%M:%S'))
    elif status == 'labelgenerated':
        send_notification(buyer_id,'Product','Label Generate of request Product')
        send_notification(lender_id,'Product','Ship Ship Hooray! Your shipping label has been sent to '+str(lender_detail[0]['email'])+' and is ready for printing. ')
        to_update = Product_request.objects.filter(id=prid).update(status=status,reason=reason,labelgenerated_date=time.strftime('%Y-%m-%d %H:%M:%S'),modify_date=time.strftime('%Y-%m-%d %H:%M:%S'))
    elif status == 'shippingtoborrower':
        send_notification(buyer_id,'Product','Ship to borrower of request Product')
        send_notification(lender_id,'Product','SHIPPING NOTIFICATION:'+str(product_detail[0]['product_name'])+' has just been shipped to '+str(borrower_detail[0]['first_name'])+' '+str(borrower_detail[0]['last_name'])+' via '+str(ship_detail[0][''])+'.')
        to_update = Product_request.objects.filter(id=prid).update(status=status,reason=reason,shippingtoborrower_date=time.strftime('%Y-%m-%d %H:%M:%S'),modify_date=time.strftime('%Y-%m-%d %H:%M:%S'))
    elif status == 'deliveredtoborrower':
        send_notification(buyer_id,'Product','Delivered to ' + str(product_detail[0]['product_name'])+' Product')
        send_notification(lender_id,'Product','SHIPPING NOTIFICATION: ' + str(product_detail[0]['product_name']) + ' was just delivered to ' + str(borrower_detail[0]['first_name'])+' '+str(borrower_detail[0]['last_name'])+'.')
        PointTransactionWithOtherDescription(lender_id,'lend-product','earn','Product',pr[0]['product_id'],prid)
        to_update = Product_request.objects.filter(id=prid).update(status=status,reason=reason,deliveredtoborrower_date=time.strftime('%Y-%m-%d %H:%M:%S'),modify_date=time.strftime('%Y-%m-%d %H:%M:%S'))
    elif status == 'returnlabelgenerated':
        send_notification(buyer_id,'Product','Ship Ship Hooray! Your shipping label has been sent to '+str(borrower_detail[0]['email'])+' and is ready for printing.' )
        send_notification(lender_id,'Product','Return Label Generated of request Product')
        to_update = Product_request.objects.filter(id=prid).update(status=status,reason=reason,returnlabelgenerated_date=time.strftime('%Y-%m-%d %H:%M:%S'),modify_date=time.strftime('%Y-%m-%d %H:%M:%S'))
    elif status == 'shippingtolender':
        send_notification(buyer_id,'Product','SHIPPING NOTIFICATION:'+str(product_detail[0]['product_name'])+' has just been shipped to '+str(lender_detail[0]['first_name'])+' '+str(lender_detail[0]['last_name'])+' via '+str(ship_detail[0][''])+'.')
        send_notification(lender_id,'Product','SHIPPING NOTIFICATION:'+str(product_detail[0]['product_name'])+' has just been shipped to '+str(lender_detail[0]['first_name'])+' '+str(lender_detail[0]['last_name'])+' via '+str(ship_detail[0][''])+'.')
        to_update = Product_request.objects.filter(id=prid).update(status=status,reason=reason,shippingtolender_date=time.strftime('%Y-%m-%d %H:%M:%S'),modify_date=time.strftime('%Y-%m-%d %H:%M:%S'))
    elif status == 'complete':
        send_notification(buyer_id,'Product','SHIPPING NOTIFICATION:'+str(product_detail[0]['product_name'])+' has just been Deliver to '+str(lender_detail[0]['first_name'])+' '+str(lender_detail[0]['last_name'])+'.')
        send_notification(lender_id,'Product','SHIPPING NOTIFICATION:'+str(product_detail[0]['product_name'])+' has just been Deliver to '+str(lender_detail[0]['first_name'])+' '+str(lender_detail[0]['last_name'])+'.')
        to_update = Product_request.objects.filter(id=prid).update(status=status,reason=reason,complete_date=time.strftime('%Y-%m-%d %H:%M:%S'),modify_date=time.strftime('%Y-%m-%d %H:%M:%S'))

        #------------------Add Point Transaction For Product Request------------------------------------------
        countlender=Product_request.objects.filter(lend_user_id=int(lender_id),status='complete').count()
        countborrower=Product_request.objects.filter(borrow_user_id=int(buyer_id),status='complete').count()

        # if countlender == 5:
        #     PointTransaction(lender_id,'five-completed-loans-lender','earn')
        #     if getpoint:
        #     send_notification(lender_id,'Earn','five completed loans lender')
        # if countlender == 10:
        #     PointTransaction(lender_id,'ten-completed-loans-lender','earn')
        #     send_notification(lender_id,'Earn','ten completed loans lender')
        # if countlender == 25:
        #     PointTransaction(lender_id,'twenty-five-completed-loans-lender','earn')
        #     send_notification(lender_id,'Earn','Twenty Five completed loans lender')
        # if countlender == 100:
        #     PointTransaction(lender_id,'100-completed-loans-lender','earn')
        #     send_notification(lender_id,'Earn','100 completed loans lender')
        # if countborrower == 5:
        #     PointTransaction(buyer_id,'five-completed-borrows-borrower','earn')
        #     send_notification(buyer_id,'Earn','Five completed loans Borrower')
        # if countborrower == 10:
        #     PointTransaction(buyer_id,'ten-completed-borrows-borrower','earn')
        #     send_notification(buyer_id,'Earn','ten completed loans Borrower')
        # if countborrower == 25:
        #     PointTransaction(buyer_id,'twenty-five-completed-borrows-borrower','earn')
        #     send_notification(buyer_id,'Earn','Twenty Five completed loans Borrower')
        # if countborrower == 100:
        #     PointTransaction(buyer_id,'100-completed-borrows-borrower','earn')
        #     send_notification(buyer_id,'Earn','100 completed loans Borrower')
        if countlender == 5:
            getpoint = PointTransaction(lender_id,'five-completed-loans-lender','earn')
            if getpoint:
                send_notification(lender_id,'Earn','That was your fifth completed load. You earned '+ str(getpoint[0]['allotment_value'])+' PEnhancer Points!')

        if countlender == 10:
            getpoint = PointTransaction(lender_id,'ten-completed-loans-lender','earn')
            if getpoint:
                send_notification(lender_id,'Earn','You`ve completed 10 loans? Whoa. You grow up so fast. Here`s '+ str(getpoint[0]['allotment_value'])+' PEnhancer Points!')

        if countlender == 25:
            getpoint = PointTransaction(lender_id,'twenty-five-completed-loans-lender','earn')
            if getpoint:
                send_notification(lender_id,'Earn','25 completed loans??? Drop. That. Mic. You just earned yourself '+ str(getpoint[0]['allotment_value'])+' more PEnhancer Points')

        if countlender == 100:
            getpoint = PointTransaction(lender_id,'100-completed-loans-lender','earn')
            if getpoint:
                send_notification(lender_id,'Earn','That was your 100th completed loan!!! Here`s '+ str(getpoint[0]['allotment_value'])+' more PEnhancer points. You`ve earned it!')

        if countborrower == 5:
            getpoint = PointTransaction(buyer_id,'five-completed-borrows-borrower','earn')
            if getpoint:
                send_notification(buyer_id,'Earn','That was your fifth completed borrow. You earned '+ str(getpoint[0]['allotment_value'])+' PEnhancer Points!')

        if countborrower == 10:
            getpoint = PointTransaction(buyer_id,'ten-completed-borrows-borrower','earn')
            if getpoint:
                send_notification(buyer_id,'Earn','You`ve completed 10 borrows? Whoa. You grow up so fast. Here`s '+ str(getpoint[0]['allotment_value'])+' PEnhancer Points!')

        if countborrower == 25:
            getpoint = PointTransaction(buyer_id,'twenty-five-completed-borrows-borrower','earn')
            if getpoint:
                send_notification(buyer_id,'Earn','25 completed borrows??? Drop. That. Mic. you just earned yourself '+ str(getpoint[0]['allotment_value'])+' more PEnhancer Points')

        if countborrower == 100:
            getpoint = PointTransaction(buyer_id,'100-completed-borrows-borrower','earn')
            if getpoint:
                send_notification(buyer_id,'Earn','That was your 100th completed borrow!!! Here`s '+ str(getpoint[0]['allotment_value'])+' more PEnhancer points. You`ve earned it!')

    return 1

def convert_json_date_format(date='0000-00-00T07:00:00Z'):
    import dateutil.parser
    return dateutil.parser.parse(date)
def get_review_rating_userwise(user_id,product_id):
    args=[user_id,product_id]
    review_rating=[]
    cursor = connection.cursor()
    cursor.execute("SELECT pr.review,pr.date,r.star,r.point from rango_product_review pr inner join rango_master_rating r on pr.master_rating_id= r.id  where pr.user_id= %s and pr.product_id=%s",args)
    result = cursor.fetchall()
    x = cursor.description
    for r in result:
        i = 0
        d = {}
        while i < len(x):
            d[x[i][0]] = r[i]
            i = i+1
        review_rating.append(d)
    return review_rating
def get_product_rating(product_id):
    args=[product_id]
    review_rating=[]
    cursor = connection.cursor()
    cursor.execute("SELECT count(r.star) as total_count , sum(r.star) as total_sum from rango_product_review pr inner join rango_master_rating r on pr.master_rating_id= r.id  where pr.product_id=%s group by r.star",args)
    result = cursor.fetchall()
    x = cursor.description
    for r in result:
        i = 0
        d = {}
        while i < len(x):
            d[x[i][0]] = r[i]
            i = i+1
        review_rating.append(d)
    tot_count=0
    tot_sum=0
    for row in review_rating:
        tot_sum     = tot_sum + int(row['total_sum'])
        tot_count   = tot_count + int(row['total_count'])
    if tot_count == 0:
        return 0
    else:
        return float(tot_sum / tot_count)
def get_model_rating(model_id):
    args=[model_id]
    review_rating=[]
    cursor = connection.cursor()
    cursor.execute("SELECT count(r.star) as total_count , sum(r.star) as total_sum from rango_discussions pr inner join rango_master_rating r on pr.master_rating_id= r.id  where pr.product_model_id=%s group by r.star",args)
    result = cursor.fetchall()
    x = cursor.description
    for r in result:
        i = 0
        d = {}
        while i < len(x):
            d[x[i][0]] = r[i]
            i = i+1
        review_rating.append(d)
    tot_count=0
    tot_sum=0
    for row in review_rating:
        tot_sum     = tot_sum + int(row['total_sum'])
        tot_count   = tot_count + int(row['total_count'])
    if tot_count == 0:
        return 0
    else:
        return float(tot_sum / tot_count)

def check_user_for_newslike(news_id=0,user_id=0):
    like=[]
    args=[news_id,user_id]
    cursor = connection.cursor()
    cursor.execute('SELECT `like`,`dislike` from rango_newslike where news_id = %s and user_id= %s',args)
    result = cursor.fetchall()
    #print(result)
    x = cursor.description
    for r in result: 
        i = 0
        d = {}
        while i < len(x):
            d[x[i][0]] = r[i]
            i = i+1
        like.append(d)

    return like
def check_user_for_commentlike(comment_id=0,user_id=0):
    like=[]
    args=[comment_id,user_id]
    cursor = connection.cursor()
    cursor.execute('SELECT `like`,`dislike` from rango_newscomment_like where comment_id = %s and user_id= %s',args)
    result = cursor.fetchall()
    #print(result)
    x = cursor.description
    for r in result: 
        i = 0
        d = {}
        while i < len(x):
            d[x[i][0]] = r[i]
            i = i+1
        like.append(d)

    return like
# def GetMasterPoint(point_id):
#     args=[rating_id]
#     review_rating=[]
#     cursor = connection.cursor()
#     cursor.execute("SELECT * from rango_master_rating where `id` = %s",args)
#     result = cursor.fetchall()
#     x = cursor.description
#     for r in result:
#         i = 0
#         d = {}
#         while i < len(x):
#             d[x[i][0]] = r[i]
#             i = i+1
#         review_rating.append(d)
#     return review_rating
def getrating(rating_id):
    rating=[]
    args=[rating_id]
    cursor = connection.cursor()
    cursor.execute("SELECT `point` from rango_master_rating where id=%s",args)
    result = cursor.fetchall()
    x = cursor.description
    for r in result:
        i = 0
        d = {}
        while i < len(x):
            d[x[i][0]] = r[i]
            i = i+1
        rating.append(d)
    return rating
def get_rating(rating_id):
    args=[rating_id]
    review_rating=[]
    cursor = connection.cursor()
    cursor.execute("SELECT * from rango_master_rating where `id` = %s",args)
    result = cursor.fetchall()
    x = cursor.description
    for r in result:
        i = 0
        d = {}
        while i < len(x):
            d[x[i][0]] = r[i]
            i = i+1
        review_rating.append(d)
    return review_rating
def number_of_day_remaining(product_request_id):
    import datetime
    from datetime import datetime
    import time
    args=[product_request_id]
    tot_queue=0
    queue=[]
    tot_day=0
    cursor = connection.cursor()
   
    sql="SELECT product_id,status,loanforday_product_id,loanforday_id,DATE_FORMAT( created_date, '%d/%m/%Y' ) AS created_date, DATE_FORMAT( approved_date, '%d/%m/%Y' ) AS approved_date, DATE_FORMAT( pointsent_date, '%d/%m/%Y' ) AS pointsent_date, DATE_FORMAT( labelgenerated_date, '%d/%m/%Y' ) AS labelgenerated_date, DATE_FORMAT( shippingtoborrower_date, '%d/%m/%Y' ) AS shippingtoborrower_date, DATE_FORMAT( deliveredtoborrower_date, '%d/%m/%Y' ) AS deliveredtoborrower_date, DATE_FORMAT( returnlabelgenerated_date, '%d/%m/%Y' ) AS returnlabelgenerated_date, DATE_FORMAT( shippingtolender_date, '%d/%m/%Y' ) AS shippingtolender_date, DATE_FORMAT( complete_date, '%d/%m/%Y' ) AS complete_date FROM rango_product_request WHERE id =" + str(product_request_id) +""
    cursor.execute(sql)
    result = cursor.fetchall()
    x = cursor.description
    for r in result:
        i = 0
        d = {}
        while i < len(x):
            d[x[i][0]] = r[i]
            i = i+1
        if d['loanforday_id']:
            days=get_loanforday(d['loanforday_id'])
            date1=datetime.strftime(datetime.now(), '%d/%m/%Y')
            d1 = datetime.strptime(date1, "%d/%m/%Y")
            if d['deliveredtoborrower_date']:
                d2 =  datetime.strptime(d['deliveredtoborrower_date'], "%d/%m/%Y")
                returndate = abs((d1 - d2).days)
                tot_day = int(days) - int(returndate)
        queue.append(d)
    return tot_day;

def get_queue_old_29_8_17(product_id):
    import datetime
    from datetime import datetime
    import time
    args=[product_id]
    tot_queue=0
    queue=[]
    tot_day=0
    cursor = connection.cursor()
    #cursor.execute("SELECT SELECT product_id,STATUS , DATE_FORMAT( created_date, '%Y-%m-%d') AS created_date, DATE_FORMAT( approved_date, '%Y-%m-%d') AS approved_date, DATE_FORMAT( pointsent_date, '%Y-%m-%d') AS pointsent_date, DATE_FORMAT( labelgenerated_date, '%Y-%m-%d') AS labelgenerated_date, DATE_FORMAT( shippingtoborrower_date, '%Y-%m-%d') AS shippingtoborrower_date, DATE_FORMAT( deliveredtoborrower_date, '%Y-%m-%d') AS deliveredtoborrower_date, DATE_FORMAT( returnlabelgenerated_date, '%Y-%m-%d') AS returnlabelgenerated_date, DATE_FORMAT( shippingtolender_date, '%Y-%m-%d') AS shippingtolender_date, DATE_FORMAT( complete_date, '%Y-%m-%d') AS complete_date FROM rango_product_request WHERE status NOT IN('pending','denied','withdrawn') and created_date <= %s and product_id = %s ",args)
    sql="SELECT product_id,status,loanforday_product_id,loanforday_id,DATE_FORMAT( created_date, '%d/%m/%Y' ) AS created_date, DATE_FORMAT( approved_date, '%d/%m/%Y' ) AS approved_date, DATE_FORMAT( pointsent_date, '%d/%m/%Y' ) AS pointsent_date, DATE_FORMAT( labelgenerated_date, '%d/%m/%Y' ) AS labelgenerated_date, DATE_FORMAT( shippingtoborrower_date, '%d/%m/%Y' ) AS shippingtoborrower_date, DATE_FORMAT( deliveredtoborrower_date, '%d/%m/%Y' ) AS deliveredtoborrower_date, DATE_FORMAT( returnlabelgenerated_date, '%d/%m/%Y' ) AS returnlabelgenerated_date, DATE_FORMAT( shippingtolender_date, '%d/%m/%Y' ) AS shippingtolender_date, DATE_FORMAT( complete_date, '%d/%m/%Y' ) AS complete_date FROM rango_product_request WHERE status NOT IN('pending','denied','withdrawn') and product_id =" + str(product_id) +""
    cursor.execute(sql)
    result = cursor.fetchall()
    x = cursor.description
    for r in result:
        i = 0
        d = {}
        while i < len(x):
            d[x[i][0]] = r[i]
            i = i+1
        if d['loanforday_id']:
            days=get_loanforday(d['loanforday_id'])
        else:
            days=0
       
        if d['status'] == 'deliveredtoborrower':
            tot_day=0
            date1=datetime.strftime(datetime.now(), '%d/%m/%Y')
            d1 = datetime.strptime(date1, "%d/%m/%Y")
            d2 =  datetime.strptime(d['deliveredtoborrower_date'], "%d/%m/%Y")
            returndate = abs((d2 - d1).days)
            tot_day = int(days) - int(returndate)
            tot_queue=tot_queue+tot_day
        else:
            tot_queue=tot_queue+days
        queue.append(d)
    return tot_queue;
def get_queue(product_id,borrow_user_id):
    import datetime
    from datetime import datetime
    import time
    args=[product_id]
    tot_queue=0
    queue=[]
    tot_day=0
    cursor = connection.cursor()
    #cursor.execute("SELECT SELECT product_id,STATUS , DATE_FORMAT( created_date, '%Y-%m-%d') AS created_date, DATE_FORMAT( approved_date, '%Y-%m-%d') AS approved_date, DATE_FORMAT( pointsent_date, '%Y-%m-%d') AS pointsent_date, DATE_FORMAT( labelgenerated_date, '%Y-%m-%d') AS labelgenerated_date, DATE_FORMAT( shippingtoborrower_date, '%Y-%m-%d') AS shippingtoborrower_date, DATE_FORMAT( deliveredtoborrower_date, '%Y-%m-%d') AS deliveredtoborrower_date, DATE_FORMAT( returnlabelgenerated_date, '%Y-%m-%d') AS returnlabelgenerated_date, DATE_FORMAT( shippingtolender_date, '%Y-%m-%d') AS shippingtolender_date, DATE_FORMAT( complete_date, '%Y-%m-%d') AS complete_date FROM rango_product_request WHERE status NOT IN('pending','denied','withdrawn') and created_date <= %s and product_id = %s ",args)
    sql="SELECT borrow_user_id,lend_user_id,product_id,status,loanforday_product_id,loanforday_id,DATE_FORMAT( created_date, '%d/%m/%Y' ) AS created_date, DATE_FORMAT( approved_date, '%d/%m/%Y' ) AS approved_date, DATE_FORMAT( pointsent_date, '%d/%m/%Y' ) AS pointsent_date, DATE_FORMAT( labelgenerated_date, '%d/%m/%Y' ) AS labelgenerated_date, DATE_FORMAT( shippingtoborrower_date, '%d/%m/%Y' ) AS shippingtoborrower_date, DATE_FORMAT( deliveredtoborrower_date, '%d/%m/%Y' ) AS deliveredtoborrower_date, DATE_FORMAT( returnlabelgenerated_date, '%d/%m/%Y' ) AS returnlabelgenerated_date, DATE_FORMAT( shippingtolender_date, '%d/%m/%Y' ) AS shippingtolender_date, DATE_FORMAT( complete_date, '%d/%m/%Y' ) AS complete_date FROM rango_product_request WHERE status NOT IN('pending','denied','withdrawn','complete') and product_id =" + str(product_id) +" order by approved_date asc "
    #print(sql);
    cursor.execute(sql)
    result = cursor.fetchall()
    x = cursor.description
    for r in result:
        i = 0
        d = {}
        while i < len(x):
            d[x[i][0]] = r[i]
            i = i+1
        queue.append(d)
    for que in queue:
        if que['loanforday_id']:
            days=get_loanforday(que['loanforday_id'])
        else:
            days=0
       
        if str(que['status']) == str('deliveredtoborrower'):
            tot_day=0
            date1=datetime.strftime(datetime.now(), '%d/%m/%Y')
            d1 = datetime.strptime(date1, "%d/%m/%Y")
            d2 =  datetime.strptime(que['deliveredtoborrower_date'], "%d/%m/%Y")
            returndate = abs((d2 - d1).days)
            tot_day = int(days) - int(returndate)
            tot_queue=tot_queue+tot_day
            # print(tot_day)
            # print('------------')
            # print(tot_queue)
            # print('-------------------------------------------------------------------------------')

        elif str(que['borrow_user_id'])!= str(borrow_user_id):
            tot_queue=tot_queue+days
            # print('***************************************************************')
            # print(tot_queue)
            # print('*****************************************************************************************')
        else:
            return tot_queue
 
    return tot_queue;
def get_queue_product(product_id,borrow_user_id):
    import datetime
    from datetime import datetime
    import time
    args=[product_id]
    tot_queue=0
    queue=[]
    tot_day=0
    cursor = connection.cursor()
    sql="SELECT borrow_user_id,lend_user_id,product_id,status,loanforday_product_id,loanforday_id,approved_date FROM rango_product_request WHERE status NOT IN('pending','denied','withdrawn','complete') and product_id =" + str(product_id) +" order by approved_date asc "
    #print(sql)
    cursor.execute(sql)
    result = cursor.fetchall()
    x = cursor.description
    for r in result:
        i = 0
        d = {}
        while i < len(x):
            d[x[i][0]] = r[i]
            i = i+1
        queue.append(d)
    for que in queue:
        if str(que['status']) == str('complete'):
            tot_day=0
            tot_queue=tot_queue+tot_day
            # print(tot_day)
            # print('------------')
            # print(tot_queue)
            # print('-------------------------------------------------------------------------------')

        if str(que['borrow_user_id'])!= str(borrow_user_id):
            tot_queue=tot_queue+1
            # print('***************************************************************')
            # print(tot_queue)
            # print('*****************************************************************************************')
        else:
            return tot_queue
    return tot_queue;
def get_queue_model(product_model_id):
    import datetime
    from datetime import datetime
    import time
    product=[]
    queue=[]
    mrgs=[product_model_id]
    cursor = connection.cursor()
    cursor.execute("SELECT id FROM rango_product  WHERE product_model_id =%s",mrgs)
    result = cursor.fetchall()
    x = cursor.description
    for r in result:
        i = 0
        d = {}
        while i < len(x):
            d[x[i][0]] = r[i]
            i = i+1
        product.append(d['id'])
    all_prod = ','.join(map(str, product))
    # print(all_prod)
    # print("--")
    # print(product_model_id)
    # print("------------------------************************-------------------------")
    sql="SELECT count(product_id) as cnt FROM rango_product_request WHERE status NOT IN('pending','denied','withdrawn','complete') and product_id IN(" + str(all_prod) +")"
    cursor.execute(sql)
    result = cursor.fetchall()
    x = cursor.description
    for r in result:
        i = 0
        d = {}
        while i < len(x):
            d[x[i][0]] = r[i]
            i = i+1
        queue.append(d)
    return queue[0]['cnt'];
    
def get_product_point(product_id):
    args=[product_id]
    queue=[]
    cursor = connection.cursor()
    cursor.execute("SELECT lfd.number_days FROM rango_loan_for_day lfd left join rango_product p on p.loanforday_id = lfd.id WHERE  p.id = %s ",args)
    result = cursor.fetchall()
    x = cursor.description
    for r in result:
        i = 0
        d = {}
        while i < len(x):
            d[x[i][0]] = r[i]
            i = i+1
        queue.append(d)
    return queue[0]['number_days'];

def send_notification(user_id,msg_title,msg_description):
    import sys
    reload(sys)
    sys.setdefaultencoding('utf-8')
    msg_description = msg_description.decode('unicode-escape')
    import datetime
    # from datetime import datetime
    # import time
    format = "%a %b %d %H:%M:%S %Y"
    today = datetime.datetime.today()
    from pyfcm import FCMNotification
    if user_id:
        args=[user_id]
    else:
        args=[0]
    user=[]
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM rango_user_device_info WHERE  user_id = %s ",args)
    result = cursor.fetchall()
    x = cursor.description
    for r in result:
        i = 0
        d = {}
        while i < len(x):
            d[x[i][0]] = r[i]
            i = i+1
        user.append(d)
    for row in user:
        if row['device_token'] != '':
            push_service = FCMNotification(api_key="AAAAKzHbzic:APA91bGbFoJR_uBVUiMfAegqORyMlUSsK6R98rOzQqFivnqoIa1fel8NBAoGdbUxtkaP75dESnto2Rnm9JCP5JFwDUyxfjzGrrpO4RnMuEnwo1-LRMnSWeaKmtW7VbKHGOrP-0OpK-UR")
            registration_id = row['device_token']
            message_title = msg_title
            message_body = msg_description
            result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title, message_body=message_body,sound='default')
    if msg_title != str('Message'):
        udi=notification()
        udi.user_id         =   user_id
        udi.msg_title       =   msg_title
        udi.msg_description =   msg_description
        udi.is_read         =   0
        udi.date            =   today
        udi.save()         
    return result
def get_order_detail(product_request_id):
    order=[]
    args=[product_request_id]
    cursor = connection.cursor()
    cursor.execute("SELECT  o.* from rango_order_detail o where product_request_id=%s ",args)
    result = cursor.fetchall()
    x = cursor.description
    for r in result:
        i = 0
        d = {}
        while i < len(x):
            d[x[i][0]] = r[i]
            i = i+1
        order.append(d)
    return order
def get_ship_detail(product_request_id):
    ship=[]
    args=[product_request_id]
    cursor = connection.cursor()
    cursor.execute("SELECT  s.* from rango_shipping_detail s where product_request_id=%s ",args)
    result = cursor.fetchall()
    x = cursor.description
    for r in result:
        i = 0
        d = {}
        while i < len(x):
            d[x[i][0]] = r[i]
            i = i+1
        ship.append(d)
    return ship
def getlendscore(user_id):
    jsonresult = {}
    rating=[]
    avg_review_point=0
    tot_rating=0
    review=0
    prod_user=[]
    cursor = connection.cursor()
    args=[user_id]
    master_point=[]
    all_user= "0"
    cursor.execute("SELECT id from rango_product where product_added_by_user_id=%s",args)
    result = cursor.fetchall()
    x = cursor.description
    for r in result:
        i = 0
        d = {}
        while i < len(x):
            d[x[i][0]] = r[i]
            i = i+1
        prod_user.append(d['id'])
    if prod_user:
        all_user = ','.join(map(str, prod_user))

    tot_transaction = Product_request.objects.filter(lend_user_id=user_id,status='complete').count()
    get_point_master="SELECT * FROM `rango_transaction_point_master`WHERE "+str(tot_transaction)+" <= `max_point` AND "+str(tot_transaction)+" >= `min_point`"
    cursor.execute(get_point_master)
    point_result = cursor.fetchall()
    x = cursor.description
    for p in point_result:
        i = 0
        d = {}
        while i < len(x):
            d[x[i][0]] = p[i]
            i = i+1
        master_point.append(d)
    point_value=master_point[0]['point_value']  

    qry="SELECT count(master_rating_id) as total_rating,master_rating_id FROM rango_product_review where product_id IN("+ all_user +") group by master_rating_id"
    cursor.execute(qry)
    result = cursor.fetchall()
    x = cursor.description
    for r in result:
        i = 0
        d = {}
        while i < len(x):
            d[x[i][0]] = r[i]
            i = i+1
        rating.append(d)

    for row in rating:
        rval=get_rating(row['master_rating_id'])
        review      =   review + (int(rval[0]['point']) * int(row['total_rating']))
        tot_rating  =   tot_rating+int(row['total_rating'])
        avg_review_point    =   round(review / tot_rating)

    score= round(float(point_value) * float(avg_review_point))

    PEnhancer_score=round(score / 2)
    return PEnhancer_score

def get_product_number_of_days(model_id):
    cursor = connection.cursor()
    pargs=[model_id]
    product=[]
    cursor.execute("SELECT p.id,lfd.number_days FROM rango_product p left join rango_loan_for_day lfd on lfd.id=p.loanforday_id WHERE p.product_model_id=%s",pargs)
    new_result = cursor.fetchall()
    x = cursor.description
    for r in new_result:
        i = 0
        d = {}
        while i < len(x):
            d[x[i][0]] = r[i]
            i = i+1
        product.append(d)
    return product
def get_loanforday_product(product_id):
    cursor = connection.cursor()
    lfdp=[product_id]
    lendforday=[]
    cursor.execute("SELECT * from rango_loanfor_day_product where is_active='1' and product_id=%s",lfdp)
    result = cursor.fetchall()
    x = cursor.description
    for r in result:
        i = 0
        d = {}
        while i < len(x):
            d[x[i][0]] = r[i]
            i = i+1
        lendforday.append(d)
    return lendforday
def get_minimum_PEnhancer_point(product_id):
    days=[]
    cursor = connection.cursor()
    #cursor.execute("SELECT SELECT product_id,STATUS , DATE_FORMAT( created_date, '%Y-%m-%d') AS created_date, DATE_FORMAT( approved_date, '%Y-%m-%d') AS approved_date, DATE_FORMAT( pointsent_date, '%Y-%m-%d') AS pointsent_date, DATE_FORMAT( labelgenerated_date, '%Y-%m-%d') AS labelgenerated_date, DATE_FORMAT( shippingtoborrower_date, '%Y-%m-%d') AS shippingtoborrower_date, DATE_FORMAT( deliveredtoborrower_date, '%Y-%m-%d') AS deliveredtoborrower_date, DATE_FORMAT( returnlabelgenerated_date, '%Y-%m-%d') AS returnlabelgenerated_date, DATE_FORMAT( shippingtolender_date, '%Y-%m-%d') AS shippingtolender_date, DATE_FORMAT( complete_date, '%Y-%m-%d') AS complete_date FROM rango_product_request WHERE status NOT IN('pending','denied','withdrawn') and created_date <= %s and product_id = %s ",args)
    sql="SELECT MIN(PEnhancer_point) as PEnhancer_point FROM rango_loanfor_day_product WHERE is_active = '1' and product_id =" + str(product_id) +""
    cursor.execute(sql)
    result = cursor.fetchall()
    x = cursor.description
    for r in result:
        i = 0
        d = {}
        while i < len(x):
            d[x[i][0]] = r[i]
            i = i+1
            days.append(d)
    return days[0]['PEnhancer_point'];
def model_discussion_totallike(discussion_id=0,review_id=0):
    like=[]
    args=[discussion_id,review_id]
    cursor = connection.cursor()
    cursor.execute('SELECT COALESCE(SUM(`like`),0) as totlike, COALESCE(SUM(`dislike`),0)as totdislike  from rango_model_review_like where discussion_id=%s and  review_id=%s',args)
    result = cursor.fetchall()
    #print(result)
    x = cursor.description
    for r in result:
        i = 0
        d = {}
        while i < len(x):
            d[x[i][0]] = r[i]
            i = i+1
        like.append(d)

    return like
def check_user_for_model_discussion(discussion_id=0,review_id=0,user_id=0):
    like=[]
    args=[discussion_id,review_id,user_id]
    cursor = connection.cursor()
    cursor.execute('SELECT `like`,`dislike` from rango_model_review_like where discussion_id = %s and review_id = %s and user_id= %s',args)
    result = cursor.fetchall()
    #print(result)
    x = cursor.description
    for r in result: 
        i = 0
        d = {}
        while i < len(x):
            d[x[i][0]] = r[i]
            i = i+1
        like.append(d)

    return like
def discussioncommentreply(discussion_id=0,user_id=0):
    reply=[]
    args=[discussion_id]
    cursor = connection.cursor()
    cursor.execute('SELECT nc.* , u.first_name,u.last_name,up.picture from rango_model_review nc inner join auth_user u on u.id=nc.user_id left join rango_userprofile up on u.id=up.user_id  where nc.discussion_id=%s order by nc.id desc',args)
    result = cursor.fetchall()
    x = cursor.description
    for r in result:
        i = 0
        d = {}
        while i < len(x):
            d[x[i][0]] = r[i]
            i = i+1
        totlike=model_discussion_totallike(discussion_id,d['id']);
        d['check_user_comment_like']=check_user_for_model_discussion(discussion_id,d['id'],user_id) 
        d['like']=totlike 
        reply.append(d)
    return reply
def get_product_number_of_days_minimum(product_id):
    cursor = connection.cursor()
    pargs=[product_id]
    product=[]
    cursor.execute("SELECT MIN(lfd.number_days) as num_day FROM rango_loanfor_day_product p left join rango_loan_for_day lfd on lfd.id= p.loanforday_id WHERE p.product_id=%s",pargs)
    new_result = cursor.fetchall()
    x = cursor.description
    for r in new_result:
        i = 0
        d = {}
        while i < len(x):
            d[x[i][0]] = r[i]
            i = i+1
        product.append(d)
    return product[0]['num_day']
def get_model_detail(model_id):
    model=[]
    cursor = connection.cursor()
    args=[model_id]
    cursor.execute("SELECT  m.* ,b.brand_name,u.username from rango_product_model m left join rango_brand b on b.id=m.brand_id left join auth_user u on u.id=m.user_id where m.id=%s",args)
    result = cursor.fetchall()
    x = cursor.description
    for r in result:
        i = 0
        d = {}
        while i < len(x):
            d[x[i][0]] = r[i]
            i = i+1
        model.append(d)
    return model
def check_product_on_request(product_id):
    product=[]
    cursor = connection.cursor()
    args=[product_id]
    cursor.execute("SELECT count(*) as count FROM rango_product_request WHERE status NOT IN('complete','denied','withdrawn') and product_id = %s ",args)
    result = cursor.fetchall()
    x = cursor.description
    for r in result:
        i = 0
        d = {}
        while i < len(x):
            d[x[i][0]] = r[i]
            i = i+1
        product.append(d)
    return product[0]['count']
def check_product_lend_status(product_id):
    product=[]
    cursor = connection.cursor()
    args=[product_id]
    cursor.execute("SELECT id FROM rango_product_request WHERE status IN('labelgenerated','shippingtoborrower','deliveredtoborrower','returnlabelgenerated','shippingtolender') and product_id = %s ",args)
    result = cursor.fetchall()
    x = cursor.description
    for r in result:
        i = 0
        d = {}
        while i < len(x):
            d[x[i][0]] = r[i]
            i = i+1
        product.append(d)
    if product:
        return product[0]['id']
    else:
        return 0
def ship_track():
    jsonresult = []
    import requests
    import datetime
    from datetime import datetime
    import time
    import json
    shipdetail=[]
    arr=[]
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM rango_shipping_detail WHERE label_id !='' and  tracking_number !='' and tracking_status !='Delivered'")
    result = cursor.fetchall()
    x = cursor.description
    for r in result:
        i = 0
        d = {}
        while i < len(x):
            d[x[i][0]] = r[i]
            i = i+1
        shipdetail.append(d)
        for ship in shipdetail:
            flag=0
            url = "https://api.shipengine.com/v1/tracking/?carrier_code="+ship['carrier_code']+"&tracking_number="+ship['tracking_number']
            headers = {'content-type': 'application/json','api-key':'P2u8d78bodWtgE4TPIhECxdJLpCAFqXKQs1icT5s5HE'}
            response = requests.request("GET", url,headers=headers)
            getres = response.json()
            jsonresult.append(getres)
            if 'status_code' in getres:
                status_code = getres['status_code']
                flag=1
            else:
                status_code = ''
                flag=0
            if 'tracking_number' in getres:
                tracking_number = getres['tracking_number']
                flag=1
            else:
                tracking_number = ''
                flag=0

            if 'status_description' in getres:
                status_description = getres['status_description']
                flag=1
            else:
                status_description = ''
                flag=0

            if 'ship_date' in getres:
                shipped_date = getres['ship_date']
                flag=1
            
            if 'estimated_delivery_date' in getres:
                estimated_delivery_date = getres['estimated_delivery_date']
                flag=1
            

            if 'actual_delivery_date' in getres:
                actual_delivery_date = getres['actual_delivery_date']
                flag=1
                
        

            # status_code='AC'
            # tracking_number='9999999999999'
            # status_description='Accepted'

            # shipped_date="2017-07-30T07:58:41.509Z"   
            # estimated_delivery_date="2017-07-31T07:58:41.509Z"
            # actual_delivery_date="2017-07-31T07:58:41.509Z"
            if actual_delivery_date:
                actual_delivery_date = actual_delivery_date[:10]
            else:
                actual_delivery_date=time.strftime('%Y-%m-%d %H:%M:%S')
            
            if shipped_date:
                shipped_date = shipped_date[:10]
            else:
                shipped_date=time.strftime('%Y-%m-%d %H:%M:%S')
            if estimated_delivery_date:
                estimated_delivery_date = estimated_delivery_date[:10]
            else:
                estimated_delivery_date=time.strftime('%Y-%m-%d %H:%M:%S')          
            
            if flag == 1:

                if ship['ship_for'] == 'lender_to_borrower':
                    #print( ship['ship_for'])
                    if status_code == 'AC' or status_code == 'IT':
                        from datetime import datetime
                        import time
                        to_update = Product_request.objects.filter(id=ship['product_request_id']).update(status='shippingtoborrower',shippingtoborrower_date=shipped_date,modify_date=time.strftime('%Y-%m-%d %H:%M:%S'))
                    elif status_code == 'DE':
                        to_update = Product_request.objects.filter(id=ship['product_request_id']).update(status='deliveredtoborrower',deliveredtoborrower_date=actual_delivery_date,shippingtoborrower_date=shipped_date,modify_date=time.strftime('%Y-%m-%d %H:%M:%S'))
                    to_update = shipping_detail.objects.filter(id=ship['id']).update(status=status_description,tracking_status=status_description,estimated_delivery_date=estimated_delivery_date,actual_delivery_date=actual_delivery_date)
                    to_update = order_detail.objects.filter(shipping_id=ship['id']).update(order_status=status_description)

                if ship['ship_for'] == 'borrower_to_lender':
                    
                    if status_code == 'AC' or status_code == 'IT':
                        from datetime import datetime
                        import time
                        to_update = Product_request.objects.filter(id=ship['product_request_id']).update(status='shippingtolender',shippingtolender_date=shipped_date,modify_date=time.strftime('%Y-%m-%d %H:%M:%S'))
                    elif status_code == 'DE':
                        to_update = Product_request.objects.filter(id=ship['product_request_id']).update(status='complete',complete_date=actual_delivery_date,modify_date=time.strftime('%Y-%m-%d %H:%M:%S'))
                    to_update = shipping_detail.objects.filter(id=ship['id']).update(status=status_description,tracking_status=status_description,estimated_delivery_date=estimated_delivery_date,actual_delivery_date=actual_delivery_date)
                    to_update = order_detail.objects.filter(shipping_id=ship['id']).update(order_status=status_description)
    return 1
def get_total_point(user_id):
    point=[]
    total=0
    cursor = connection.cursor()
    args=[user_id]
    cursor.execute("SELECT COALESCE(SUM(`earn_value`),0) as totearn, COALESCE(SUM(`spent_value`),0) as totspeant FROM rango_point_transaction where user_id=%s",args)
    result = cursor.fetchall()
    x = cursor.description
    for r in result:
        i = 0
        d = {}
        while i < len(x):
            d[x[i][0]] = r[i]
            i = i+1
        point.append(d)
        total=point[0]['totearn']-point[0]['totspeant']
    return int(total)     
def item_return_notification():
    requser=[]
    cursor = connection.cursor()
    args=[uid]
    cursor.execute("SELECT * from rango_product_request WHERE STATUS like 'deliveredtoborrower'")
    result = cursor.fetchall()
    x = cursor.description
    for r in result:
        i = 0
        d = {}
        while i < len(x):
            d[x[i][0]] = r[i]
            i = i+1
        product_detail=get_product_detail(product_id)
        lender_detail   =   getusername(borrow_user_id)
        if lender_detail[0]['gender'] == str('Male'):
            gender='him'
        else:
            gender='her'
        val=number_of_day_remaining(d['id'])
        if val != 0:
            send_notification(user_id,'Info','PAGING MR. HERMAN: It`s time to get '+ str(lender_detail[0]['first_name'])+' '+str(lender_detail[0]['last_name'])+ '`s' + str(product_detail[0]['brand_name']) + ' ' + str(product_detail[0]['model_name']) +'  back to ' + gender + ' . Only ' + val + ' days left.')
        else:
            send_notification(user_id,'Info','TIME IS UP! Please pack up the ' + str(product_detail[0]['brand_name']) + ' ' + str(product_detail[0]['model_name']) +' , create a shipping label, and send it back.')
        requser.append(d)
def send_unread_chat_notification(reciver_user_id,sender_user_id):
    jsonresult = {}
    #uid         =   request.GET.get('user_id')
    args=[reciver_user_id,sender_user_id]
    notification=[]
    cursor = connection.cursor()
    cursor.execute("SELECT sender_user_id , COUNT(*) as cnt  from djangoChat_message where is_read=0 AND reciver_user_id=%s and sender_user_id=%s",args)
    result = cursor.fetchall()
    x = cursor.description
    for r in result:
        i = 0
        d = {}
        while i < len(x):
            d[x[i][0]] = r[i]
            i = i+1
        notification.append(d)

    for noti in notification:   
        if noti['cnt'] > 1:
           # print(noti)
            user_detail=getusername(noti['sender_user_id'])
            send_notification(reciver_user_id,'Chat',str(user_detail[0]['first_name'])+' '+str(user_detail[0]['last_name'])+' Post new message to you. Check it out!')
    return 1
def random_with_N_digits(n):   
    from random import randint
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end) 
def ship_hook_track():
    # import json
    # import requests
    # response = request.form
    # print(response)
    #data = response.json()
    # subject = 'Testing mail'
    # from_email = settings.EMAIL_HOST_USER
    # to = 'rabinarayan81@gmail.com'

    html_content = 'Testing this mail...'
    if to and from_email:
        try:
            text_content = 'This is an important message.'
            msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.send()

            print('mail sent .....')
        except BadHeaderError:
            print('mail not sent ...')
    print("Please Refresh For More Update")
    print("---------------------------------")
    
    return 1

def user_activity(description,user_id,meta_key,metavalue):
    import datetime
    from datetime import datetime
    import time
    jsonresult = {}
    pnt=user_audit()
    pnt.user_id             =   int(user_id)
    pnt.description         =   description
    pnt.meta_key            =   meta_key
    pnt.metavalue           =   metavalue
    pnt.date          =   datetime.now()
    pnt.save()
    return 1