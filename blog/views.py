from django.shortcuts import render
from django.views.generic import ListView, DetailView
from . models import Post, Client, Membership, MembershipClient

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
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
from .library import *
from django.core.mail import send_mail
from django.core.mail import send_mail, BadHeaderError
from django.core.mail import EmailMultiAlternatives
from django.template.defaultfilters import slugify
import json
from django.http import JsonResponse
from django.db import connection
from django.conf import settings
from . forms import UserForm, UserProfileForm
import simplejson as json
# Create your views here.


@login_required(login_url="/login/")
def index(request):
    context = RequestContext(request)
    context_dict = {}
    if request.user.is_authenticated:
        return HttpResponseRedirect('/dashboard/')
    else:
        return HttpResponseRedirect('/login/')
    current_user = request.user
    # context_dict['unread_chat'] = notifcation(int(current_user.id))
    # context_dict['media_url'] = settings.S3_MEDIA_URL
    return render_to_response('login.html', context_dict, context)


@csrf_exempt
def user_login(request):
    # print("success")
    # Obtain our request's context.
    context = RequestContext(request)
    # cat_list = get_category_list()
    context_dict = {}
    # context_dict['cat_list'] = cat_list
    print(request.user.is_authenticated)
    if request.user.is_authenticated:
        return HttpResponseRedirect('/dashboard/')
    print(request.method)
    # If HTTP POST, pull out form data and process it.
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # Attempt to log the user in with the supplied credentials.
        # A User object is returned if correct - None if not.
        user = authenticate(username=username, password=password)
        print(user)
        # A valid user logged in?
        current_user = request.user
        if user is not None:
            # Check if the account is active (can be used).
            # If so, log the user in and redirect them to the homepage.
            if user.is_active == 1:
                login(request, user)
                # cursor = connection.cursor()
                # commnet_id = cursor.execute('SELECT last_insert_id()')
                # commnet_id =cursor.fetchone()
                # for r in commnet_id:
                #     cid=r
                print(current_user.id)
                user_recent = getusername(current_user.id)
                user_name = str(user.first_name+' '+user.last_name)
                # user_recent[0]['first_name'])+' ' + str(user_recent[0]['last_name'])
                user_activity(user_name + 'Login',
                              user.id, 'User', user.id)
                return HttpResponseRedirect('/dashboard/')
            # The account is inactive; tell by adding variable to the template context.
            else:
                context_dict['bad_details'] = True
                return render_to_response('login.html', context_dict, context)
                # return HttpResponseRedirect('/dashboard/')
        # Invalid login details supplied!
        else:
            # current_user = request.user
            # getusername(current_user.id)
            print("Invalid login details: " + username + password)
            context_dict['bad_details'] = True
            return render_to_response('login.html', context_dict, context)
            # return HttpResponseRedirect('/dashboard/')
    # Not a HTTP POST - most likely a HTTP GET. In this case, we render the login form for the user.
    else:
        return render_to_response('login.html', context_dict, context)

@csrf_exempt
# @login_required(login_url="login/")
def adduser(request):
    # Request the context.
    context = RequestContext(request)
    # cat_list = get_category_list()
    context_dict = {}
    registered = False
    password = ''
 
    # If HTTP POST, we wish to process form data and create an account.
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        # Two valid forms?
        if user_form.is_valid():
            # Save the user's form data. That one is easy.

            user = user_form.save()
            password = user.password
            user.set_password(user.password)
            user.username = request.POST['username']
            user.save()
            messages.success(request, 'User Added Successfully')
            registered = True
            userprofile = UserProfile()
            userprofile.user_id = user.id
            userprofile.industry_id = '1'
            clients = request.POST.getlist('client')
            userprofile.login_type = '0'
            userprofile.membership_id = '1'

          
            userprofile.contact_number = "contact_number"
            userprofile.gender = "gender"
            userprofile.save()
            messages.success(request, 'Profile Saved Successfully')  
            # subject = 'Welcome to PEnhancer'
            # from_email = settings.EMAIL_HOST_USER
            # to = user.email
            # html_content = 'Dear '+user.first_name+',<br/>Welcome to  PEnhancer<br/> Your Detail given Bellow<br/><br/>Name: '+user.first_name+'&nbsp;'+user.last_name + \
            #     '<br>Email-'+user.email+'<br/>Password:-'+password + \
            #     '<br/><br/>For More Detail Please contact to Admin Team<br/><br/><br/>Thanks Regards,<br/> PEnhancer Team'
            # if to and from_email:
            #     try:
            #         text_content = '<br/><h2>Thanks<h2>,<br/><b> PEnhancer Team</b>'
            #         # msg = EmailMultiAlternatives(
            #         #     subject, text_content, from_email, [to])
            #         # msg.attach_alternative(html_content, "text/html")
            #         # msg.send()
            #     except BadHeaderError:
            #         messages.error(
            #             request, 'Due to some technical problem we are unable to send otp to your mail id')
        else:
            print (user_form.errors)
            messages.error(request, user_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()
        context_dict['user_form'] = user_form
        context_dict['registered'] = registered
        current_user = request.user
        industry = []
        cursor = connection.cursor()
        cursor.execute("SELECT * from blog_industry")
        result = cursor.fetchall()
        x = cursor.description
        for r in result:
            i = 0
            d = {}
            while i < len(x):
                d[x[i][0]] = r[i]
                i = i+1
            industry.append(d)
        context_dict['industry_list'] = industry
    # context_dict['unread_chat'] = notifcation(int(current_user.id))
    # context_dict['media_url'] = settings.S3_MEDIA_URL
    if(registered):
        return HttpResponseRedirect('/dashboard/')
    else:
        return render_to_response('register.html', context_dict, context)



@csrf_exempt
# @login_required(login_url="login/")
def register(request):
    # Request the context.
    context = RequestContext(request)
    # cat_list = get_category_list()
    context_dict = {}
    registered = False
    password = ''
    # If HTTP POST, we wish to process form data and create an account.
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        # Two valid forms?
        if user_form.is_valid():
            # Save the user's form data. That one is easy.

            user = user_form.save()
            password = user.password
            user.set_password(user.password)
            # user.username = "testuser122"
            user.save()
            messages.success(request, 'User Added Successfully')
            registered = True

            userprofile = UserProfile()
            userprofile.user_id = user.id
            userprofile.industry_id = request.POST['industry']

            client = request.POST['client']
            input_industry = request.POST['industry']

            userprofile.login_type = '1'

            storeClient = Client()
            storeClient.user_id = user.id
            storeClient.client_name = client
            storeClient.industry_id = input_industry
            storeClient.save()

            membership = Membership()
            membership.user_id = user.id
            membership.subscription_level = request.POST['accounttype']
            membership.user_company = ""
            membership.save()

            userprofile.membership_id = membership.id

            membershipClient = MembershipClient()
            membershipClient.client_id = storeClient.id
            membershipClient.membership_id = membership.id
            membershipClient.save()

            userprofile.contact_number = "contact_number"
            userprofile.gender = "gender"
            userprofile.save()

            messages.success(request, 'Profile Saved Successfully')  
            # subject = 'Welcome to PEnhancer'
            # from_email = settings.EMAIL_HOST_USER
            # to = user.email
            # html_content = 'Dear '+user.first_name+',<br/>Welcome to  PEnhancer<br/> Your Detail given Bellow<br/><br/>Name: '+user.first_name+'&nbsp;'+user.last_name + \
            #     '<br>Email-'+user.email+'<br/>Password:-'+password + \
            #     '<br/><br/>For More Detail Please contact to Admin Team<br/><br/><br/>Thanks Regards,<br/> PEnhancer Team'
            # if to and from_email:
            #     try:
            #         text_content = '<br/><h2>Thanks<h2>,<br/><b> PEnhancer Team</b>'
            #         # msg = EmailMultiAlternatives(
            #         #     subject, text_content, from_email, [to])
            #         # msg.attach_alternative(html_content, "text/html")
            #         # msg.send()
            #     except BadHeaderError:
            #         messages.error(
            #             request, 'Due to some technical problem we are unable to send otp to your mail id')
        else:
            print (user_form.errors)
            messages.error(request, user_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()
        context_dict['user_form'] = user_form
        context_dict['registered'] = registered
        current_user = request.user
        industry = []
        cursor = connection.cursor()
        cursor.execute("SELECT * from blog_industry")
        result = cursor.fetchall()
        x = cursor.description
        for r in result:
            i = 0
            d = {}
            while i < len(x):
                d[x[i][0]] = r[i]
                i = i+1
            industry.append(d)
        context_dict['industry_list'] = industry
    # context_dict['unread_chat'] = notifcation(int(current_user.id))
    # context_dict['media_url'] = settings.S3_MEDIA_URL
    if(registered):
        return HttpResponseRedirect('/login/')
    else:
        return render_to_response('signup.html', context_dict, context)

def get_clients(request, uid):
    args = [uid]
    clients = []
    context = RequestContext(request)
    cursor = connection.cursor()
    cursor.execute("SELECT * from blog_client where industry_id = %s",args)
    # cursor.execute("SELECT * from blog_client c left join blog_industry i on c.industry_id = i.id order by c.id desc")
    result = cursor.fetchall()
    x = cursor.description
    for r in result:
        i = 0
        d = {}
        while i < len(x):
            d[x[i][0]] = r[i]
            i = i+1
        clients.append(d) 
        
    return HttpResponse(json.dumps(clients), content_type="application/json")

def get_assessment(request, uid):
    args = [uid]
    assessments = []
    context = RequestContext(request)
    cursor = connection.cursor()
    cursor.execute("SELECT * from blog_assessment where client_id = %s",args)
    # cursor.execute("SELECT * from blog_client c left join blog_industry i on c.industry_id = i.id order by c.id desc")
    result = cursor.fetchall()
    x = cursor.description
    for r in result:
        i = 0
        d = {}
        while i < len(x):
            d[x[i][0]] = r[i]
            i = i+1
        assessments.append(d) 
        
    return HttpResponse(json.dumps(assessments), content_type="application/json")

@login_required(login_url="/login/")
def user_logout(request):
    context_dict = {}
    logout(request)
    context = RequestContext(request)
    # return render_to_response('rango/login.html', context_dict, context)
    # context_dict['media_url'] = settings.S3_MEDIA_URL
    return HttpResponseRedirect('/login/?next=/login/')


@login_required(login_url="login/")
def dashboard(request):
    # Request the context.
    # point=PointTransaction(1,31,1)
    # return HttpResponse(point)
    #rand = random_with_N_digits(5)
    context = RequestContext(request)
    context_dict = {}
    # cat_list = " "
    # # context_dict['cat_list'] = cat_list
    # total_user = User.objects.count()
    # total_category = Category.objects.count()
    # total_news = News.objects.count()
    # total_feature_lend = Product.objects.filter(is_feature=1).count()
    # total_product = Product.objects.count()
    # total_model = product_model.objects.count()
    # total_brand = Brand.objects.count()
    # context_dict = {'total_product': total_product, 'total_user': total_user -
    #                 1, 'total_category': total_category, 'total_brand': total_brand}
    # count = request.session.get('visits', 0)
    # context_dict['visit_count'] = count
    # context_dict['total_news'] = total_news
    # context_dict['total_feature_lend'] = total_feature_lend
    # context_dict['total_model'] = total_model

    # total_lend = Product_request.objects.count()
    # context_dict['total_lend'] = total_lend

    # total_damage = damage_protection_charge.objects.count()
    # context_dict['total_damage'] = total_damage

    # total_review = Product_review.objects.count()
    # context_dict['total_review'] = total_review

    # total_cc = Creditcard_detail.objects.count()
    # context_dict['total_cc'] = total_cc

    # total_shipping = shipping_detail.objects.count()
    # context_dict['total_shipping'] = total_shipping

    current_user = request.user
    # context_dict['unread_chat'] = notifcation(int(current_user.id))
    # # Return and render the response, ensuring the count is passed to the template engine.
    # context_dict['media_url'] = settings.S3_MEDIA_URL
    # context_dict['rand'] = rand
    return render_to_response('dashboard.html', context_dict, context)


@login_required(login_url="/login/")
def profile(request, uid):
    context_dict = {}
    user = []
    category = []
    catlist = ''
    uploaded_product = []
    point_detail = []
    context = RequestContext(request)
    count = UserProfile.objects.filter(user_id=uid).count()
    cursor = connection.cursor()
    args = [uid]
    if count > 0:
        #cursor.execute("SELECT u.id,u.is_active,u.username,u.first_name, u.last_name, u.email, u.date_joined,up.picture,up.contact_number,up.dob,up.address1,up.address2,up.city,up.zip_code, up.gender, up.category,c.country_name,s.state_name from auth_user u inner join rango_userprofile up on u.id = up.user_id left join rango_country c on up.country_id = c.id left join rango_state s on s.id=up.state_id where up.user_id= %s",args)
        cursor.execute("SELECT u.id,u.is_active,u.username,u.first_name, u.last_name, u.email, u.date_joined,up.picture,up.contact_number,up.dob, up.gender,up.address1,up.address2,up.city,up.state,up.country,up.country_code,up.state_code,up.zip_code, up.category,up.id as profile_id,up.login_type from auth_user u left join blog_userprofile up on u.id = up.user_id where up.user_id= %s", args)

    else:
        # do something else
        cursor.execute(
            "SELECT  u.id,u.is_active,u.username,u.first_name, u.last_name, u.email, u.date_joined from auth_user u where u.id= %s", args)
    result = cursor.fetchall()
    x = cursor.description
    for r in result:
        i = 0
        d = {}
        while i < len(x):
            d[x[i][0]] = r[i]
            i = i+1
        user.append(d)
    context_dict['user_list'] = user
    # if ("category" in user[0]):
    #     newcat = user[0]['category'].split(',')
    #     for nc in newcat:
    #         cat = [nc]
    #         category = []
    #         cursor.execute(
    #             "SELECT  category_name from rango_category WHERE id = %s", cat)
    #         result = cursor.fetchall()
    #         x = cursor.description
    #         for r in result:
    #             i = 0
    #             d = {}
    #             while i < len(x):
    #                 d[x[i][0]] = r[i]
    #                 i = i+1
    #             category.append(d)
    #             catlist += category[0]['category_name'] + ','+' '
    #     context_dict['seelct_category'] = catlist.rstrip(', ')

    #cursor.execute("SELECT  * from rango_product where product_added_by_user_id = %s",args)
    # cursor.execute("SELECT  p.* ,c.category_name ,b.brand_name,l.title as lendforday ,u.username from rango_product p left join rango_category c on p.category_id = c.id left join rango_brand b on b.id=p.brand_id Left join rango_loan_for_day l on l.id=p.loanforday_id left join auth_user u on u.id=p.product_added_by_user_id where p.product_added_by_user_id= %s", args)
    # result = cursor.fetchall()
    # x = cursor.description
    # for r in result:
    #     i = 0
    #     d = {}
    #     while i < len(x):
    #         d[x[i][0]] = r[i]
    #         i = i+1
    #     uploaded_product.append(d)
    # context_dict['uploaded_product'] = uploaded_product
    # u_id = [uid]
    # cursor.execute(
    #     "SELECT  pt.*,u.username from rango_point_transaction pt left join auth_user u on u.id=pt.user_id where pt.user_id = %s", u_id)
    # result = cursor.fetchall()
    # x = cursor.description
    # for r in result:
    #     i = 0
    #     d = {}
    #     while i < len(x):
    #         d[x[i][0]] = r[i]
    #         i = i+1
    #     point_detail.append(d)
    # context_dict['point_detail'] = point_detail

    # ------------------------------------------Borrow Product By User--------------------------------------------
    # product=[]
    # bruid=[uid]
    # cursor.execute("SELECT pr . * , p.id as product_id, p.title as product_name ,p.picture,p.product_added_by_user_id,b.brand_name, m.model_name FROM rango_product_request pr LEFT JOIN rango_product p ON p.id = pr.product_id LEFT JOIN rango_brand b ON b.id = p.brand_id LEFT JOIN rango_product_model m ON m.id = p.product_model_id WHERE pr.status !='success' and pr.borrow_user_id =%s ",bruid)
    # result = cursor.fetchall()
    # x = cursor.description
    # for r in result:
    #     i = 0
    #     d = {}
    #     while i < len(x):
    #         d[x[i][0]] = r[i]
    #         i = i+1
    #     product.append(d)
    # context_dict['borrow_request_list']=product

    # --------------------------------------Lend Product By User-------------------------------------------------

    # args=[uid]
    # product=[]
    # cursor.execute("SELECT product_id, count(product_id) as total_request FROM rango_product_request WHERE status !='success' and lend_user_id =%s group by product_id ",args)
    # result = cursor.fetchall()
    # x = cursor.description
    # for r in result:
    #     i = 0
    #     d = {}
    #     while i < len(x):
    #         d[x[i][0]] = r[i]
    #         i = i+1
    #     prod=get_product_detail(d['product_id'])
    #     d['product_detail']=prod
    #     product.append(d)
    # context_dict['lend_request_list']=product
    # lendscore = getlendscore(uid)
    # context_dict['lendscore']=lendscore
    # current_user = request.user
    # context_dict['unread_chat'] =notifcation(int(current_user.id))
    # context_dict['media_url'] = settings.S3_MEDIA_URL
    return render_to_response('profile.html', context_dict, context)

@csrf_exempt
@login_required(login_url="/login/")    
def edituser(request,uid):
    context_dict = {}
    user=[]
    if request.POST:
        #USER TABLE
        pre_picture         =   request.POST['pre_picture']
        if not request.FILES.get('picture', None):
            picture             =   pre_picture
        else:
            picture             =   request.FILES['picture']
        user_id     =   request.POST['user_id']
        email       =   request.POST['email']
        first_name  =   request.POST['first_name']
        last_name   =   request.POST['last_name']
        address1    =   request.POST['address1']
        address2    =   request.POST['address2']
        city        =   request.POST['city']
        country     =   request.POST['country']
        state       =   request.POST['state']
        country_code =   request.POST['country_code']
        state_code   =   request.POST['state_code']
        zip_code    =   request.POST['zip_code']
        user_update = User.objects.filter(id=user_id).update(email=email, first_name=first_name,last_name=last_name)
        #return HttpResponseRedirect('/userlist/') 
        #User Profile
        current_user = request.user
        user_recent = getusername(current_user.id)
        edit_user = getusername(user_id)
        desc=user_recent[0]['first_name']+' '+ user_recent[0]['last_name']+' Edit User Profile of '+edit_user[0]['first_name']+' '+edit_user[0]['last_name']
        user_activity(str(desc),int(current_user.id),'User',int(user_id))
        count=UserProfile.objects.filter(user_id=user_id).count()
        import datetime
        dob =   datetime.datetime.strptime(request.POST['dob'], "%m-%d-%Y").strftime("%Y-%m-%d")
        contact_number = request.POST['contact_number']
        #dob = request.POST['dob']
        gender = request.POST['gender']
        category = request.POST['category']
       # picture = request.FILES['picture']
        pid = request.POST['id']
        if count >0:
            userprofile                 = UserProfile.objects.get(pk=pid)
            userprofile.dob             = dob
            userprofile.contact_number  = contact_number
            userprofile.gender          = gender
            userprofile.category        =category
            userprofile.picture         = picture
            userprofile.user_id         = user_id
            userprofile.address1        = address1
            userprofile.address2        = address2
            userprofile.city            = city
            userprofile.country         = country
            userprofile.state           = state
            userprofile.country_code    = country_code
            userprofile.state_code      = state_code
            userprofile.zip_code        = str(zip_code)
            userprofile.save()
            # S3__Upload(str(userprofile.picture),'profile_images')
            # user = UserProfile.objects.get(pk=pid)
            # newdoc = UserProfile(user_id=user_id,contact_number=contact_number, dob=dob, location=location, gender=gender, category=category,picture=picture,instnce=user)
            # newdoc.save()
            #userprofile_update = UserProfile.objects.filter(id=pid).update(contact_number=contact_number, dob=dob, location=location, gender=gender, category=category,picture=picture)
        else:
            userprofile                 = UserProfile()
            userprofile.dob             = dob
            userprofile.contact_number  = contact_number
            userprofile.gender          = gender
            userprofile.category        = category
            userprofile.picture         = picture
            userprofile.user_id         = user_id
            userprofile.address1        = address1
            userprofile.address2        = address2
            userprofile.city            = city
            userprofile.country         = country
            userprofile.state           = state
            userprofile.country_code    = country_code
            userprofile.state_code      = state_code
            userprofile.zip_code        = str(zip_code)
            userprofile.login_type      = 'standard'
            userprofile.save()
            # S3__Upload(str(userprofile.picture),'profile_images')
        messages.success(request, 'Profile Saved Successfully')  
        current_user = request.user
        # context_dict['unread_chat'] =notifcation(int(current_user.id))
        # context_dict['media_url'] = settings.S3_MEDIA_URL

        return HttpResponseRedirect('/userlist/') 
    else: 
        context_dict = {}
        user=[]
        context = RequestContext(request)
        country=[]
        state=[]
        category=[]
        countries=[]
        clist=''
        selst='<select name="state_id" id="state_id" class="form-control">'
        count=UserProfile.objects.filter(user_id=uid).count()
        cursor = connection.cursor()
        args=[uid]
        if count >0:
            cursor.execute("SELECT u.id,u.is_active,u.username,u.first_name, u.last_name, u.email, u.date_joined,up.picture,up.contact_number,up.dob, up.gender,up.address1,up.address2,up.city,up.state,up.country,up.country_code AS country_iso,up.state_code AS state_iso,up.zip_code, up.category,up.id as profile_id from auth_user u left join blog_userprofile up on u.id = up.user_id where up.user_id= %s",args)
        else:
        #do something else
            cursor.execute("SELECT  u.id,u.is_active,u.username,u.first_name, u.last_name, u.email, u.date_joined from auth_user u where u.id= %s",args)

        result = cursor.fetchall()
        x = cursor.description
        for r in result:
            i = 0
            d = {}
            while i < len(x):
                d[x[i][0]] = r[i]
                i = i+1
            user.append(d)
        context_dict['user_list'] = user  
        cactive=[1]
        cursor.execute("SELECT iso_code from blog_country where is_active=%s",cactive)
        result = cursor.fetchall()
        x = cursor.description
        for r in result:
            i = 0
            d = {}
            while i < len(x):
                d[x[i][0]] = r[i]
                i = i+1
            country.append(d)
        for cnt in country:
            countries.append(cnt['iso_code'])
        clist = ','.join(countries)
        context_dict['country_list'] = clist
        category=[]
        getlevel1=[]
        getlevel2=[]
        usercat=[]
        context = RequestContext(request)
        category=getcategory(0)
        selcat=''
        # if ("category" in user[0]):
        #     usercat=user[0]['category'].split(",")
        # #print(usercat)
        # for cat in category:
        #     if str(cat['id']) in usercat:
        #         #print(catid)
        #         selectc=' selected = "select" '
        #     else:
        #         selectc=''
        #     getlevel1=getcategory(cat['id'])

        #     if len(getlevel1) > 0:
        #         selcat+=str('<optgroup label="')+str(cat['category_name'])+str('"></optgroup>')
        #     else:
        #         selcat+=str('<option value="') + str(cat['id']) + str('"')+ str(selectc) +str('>')+ str(cat['category_name']) + str('</option>')
        #     for cat1 in getlevel1:

        #         #if str(cat1['id']) == str(product[0]['category_id']):
        #         if str(cat1['id']) in usercat:
        #             selectc=' selected = "select" '
        #         else:
        #             selectc=''
        #         getlevel2=getcategory(cat1['id'])
        #         if len(getlevel2) > 0:
        #             selcat+=str('<optgroup label="')+str(' -- ')+str(cat1['category_name'])+str('"></optgroup>')
        #         else:
                    
        #             selcat +=str('<option value="') + str(cat1['id']) +  str('"') + str(selectc) +str('>') + str(' -- ')+str(cat1['category_name']) + str('</option>')
             
        #         for cat2 in getlevel2:
        #             #if str(cat2['id']) == str(product[0]['category_id']):
        #             if str(cat2['id']) in usercat:
        #                 #print(cat2['id'])
        #                 selectc=' selected = "select" '
        #             else:
        #                 selectc=''
        #             selcat +=str('<option value="') + str(cat2['id']) +  str('"') + str(selectc) +str('>') + str(' -- -- ')+str(cat2['category_name']) + str('</option>')
        # context_dict['category_list'] = selcat
        # if ("country_id" in user[0]):
        #     stargs=[user[0]['country_id']]
        #     cursor.execute("SELECT  * from blog_state where country_id = %s",stargs)
        #     result = cursor.fetchall()
        #     x = cursor.description
        #     for r in result:
        #         i = 0
        #         d = {}
        #         while i < len(x):
        #             d[x[i][0]] = r[i]
        #             i = i+1
        #         state.append(d)
        # for st in state:
        #     selst +=str('<option value="') + str(st['id']) +  str('"') +str('>')+str(st['state_name']) + str('</option>')
        # selst +='</select>'
        # context_dict['state_list'] = selst
        current_user = request.user
        # context_dict['unread_chat'] =notifcation(int(current_user.id))
        return render_to_response('edituser.html', context_dict, context)

@login_required(login_url="/login/")
def userlist(request):
    context = RequestContext(request)
    user_list = []
    context_dict={}
    if request.POST:
        is_active = request.POST['is_active']
        uid=request.POST['id']
        prnt = User.objects.get(id=uid)
        if is_active == '1':
           # to_update = User.objects.filter(id=uid).update(is_active=False)
            prnt.is_active = 1
        else:
            #to_update = User.objects.filter(id=uid).update(is_active=True)
            prnt.is_active = 0
        prnt.save()  # <---- here
    cursor = connection.cursor()
    cursor.execute("SELECT u.id,u.is_active,u.username,u.first_name, u.last_name, u.email, u.date_joined,up.picture,up.contact_number,up.login_type from auth_user u left join blog_userprofile up on u.id = up.user_id where u.is_superuser = 0 order by u.id desc")
    result = cursor.fetchall()
    x = cursor.description
    for r in result:
        i = 0
        d = {}
        while i < len(x):
            d[x[i][0]] = r[i]
            i = i+1
        user_list.append(d)
   # print(user_list)
    context_dict['user_list'] = user_list
    # Render and return the rendered response back to the user.
    current_user = request.user
    # context_dict['unread_chat'] =notifcation(int(current_user.id))
    # context_dict['media_url'] = settings.S3_MEDIA_URL
    return render_to_response('userlist.html',context_dict, context)

@csrf_exempt
@login_required(login_url="/login/")
def createassessment(request):
    context = RequestContext(request)
    context_dict = {}
    registered = False
    # password = ''
    if request.method == 'POST':
        assessment = Assessment()
        assessment.business_score = request.POST['businessScore']
        assessment.finance_score = request.POST['financeScore']
        assessment.marketing_score = request.POST['marketingScore']
        assessment.human_score = request.POST['humanScore']
        assessment.technology_score = request.POST['technologyScore']
        assessment.total_score = request.POST['totalScore']
        user = request.user
        assessment.user_id = user.id
        assessment.client_id = request.POST['client']
        assessment.membership_id = "1"
        assessment.save()
        messages.success(request, 'Assessment Saved Successfully')  
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()
        context_dict['user_form'] = user_form
        context_dict['registered'] = registered
        current_user = request.user
        industry = []
        cursor = connection.cursor()
        cursor.execute("SELECT * from blog_client")
        result = cursor.fetchall()
        x = cursor.description
        for r in result:
            i = 0
            d = {}
            while i < len(x):
                d[x[i][0]] = r[i]
                i = i+1
            industry.append(d)
        context_dict['client_list'] = industry
    # if(registered):
    #     return HttpResponseRedirect('dashboard/')
    # else:
    #     return render_to_response('signup.html', context_dict, context)
    return render_to_response('createassessment.html',context_dict, context)

@csrf_exempt
@login_required(login_url="/login/")
def viewassessment(request):
    context = RequestContext(request)
    context_dict = {}
    registered = False
    # password = ''
    if request.method == 'POST': 
        assessment=[] 
        cursor = connection.cursor()
        args=[request.POST['client']]
        cur.execute("SELECT * from blog_assessment where client_id = %s",args)
        result = cursor.fetchall()
        x = cursor.description
        for r in result:
            i = 0
            d = {}
            while i < len(x):
                d[x[i][0]] = r[i]
                i = i+1
            assessment.append(d)
        context_dict['assessment_list'] = assessment
        assessment = Assessment()
        assessment.business_score = request.POST['businessScore']
        assessment.finance_score = request.POST['financeScore']
        assessment.marketing_score = request.POST['marketingScore']
        assessment.human_score = request.POST['humanScore']
        assessment.technology_score = request.POST['technologyScore']
        assessment.total_score = request.POST['totalScore']
        user = request.user
        assessment.user_id = user.id
        assessment.client_id = request.POST['client']
        assessment.membership_id = "1"
        assessment.save()
        messages.success(request, 'Assessment Saved Successfully')  
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()
        context_dict['user_form'] = user_form
        context_dict['registered'] = registered
        current_user = request.user
        industry = []
        cursor = connection.cursor()
        cursor.execute("SELECT * from blog_client")
        result = cursor.fetchall()
        x = cursor.description
        for r in result:
            i = 0
            d = {}
            while i < len(x):
                d[x[i][0]] = r[i]
                i = i+1
            industry.append(d)
        context_dict['client_list'] = industry
    # if(registered):
    #     return HttpResponseRedirect('dashboard/')
    # else:
    #     return render_to_response('signup.html', context_dict, context)
    return render_to_response('viewassessment.html',context_dict, context)

@csrf_exempt
@login_required(login_url="/login/")
def compareassessment(request):
    context = RequestContext(request)
    context_dict = {}
    registered = False
    # password = ''
    if request.method == 'POST': 
        assessment=[] 
        cursor = connection.cursor()
        args=[request.POST['client']]
        cur.execute("SELECT * from blog_assessment where client_id = %s",args)
        result = cursor.fetchall()
        x = cursor.description
        for r in result:
            i = 0
            d = {}
            while i < len(x):
                d[x[i][0]] = r[i]
                i = i+1
            assessment.append(d)
        context_dict['assessment_list'] = assessment
        assessment = Assessment()
        assessment.business_score = request.POST['businessScore']
        assessment.finance_score = request.POST['financeScore']
        assessment.marketing_score = request.POST['marketingScore']
        assessment.human_score = request.POST['humanScore']
        assessment.technology_score = request.POST['technologyScore']
        assessment.total_score = request.POST['totalScore']
        user = request.user
        assessment.user_id = user.id
        assessment.client_id = request.POST['client']
        assessment.membership_id = "1"
        assessment.save()
        messages.success(request, 'Assessment Saved Successfully')  
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()
        context_dict['user_form'] = user_form
        context_dict['registered'] = registered
        current_user = request.user
        industry = []
        cursor = connection.cursor()
        cursor.execute("SELECT * from blog_client")
        result = cursor.fetchall()
        x = cursor.description
        for r in result:
            i = 0
            d = {}
            while i < len(x):
                d[x[i][0]] = r[i]
                i = i+1
            industry.append(d)
        context_dict['client_list'] = industry
    # if(registered):
    #     return HttpResponseRedirect('dashboard/')
    # else:
    #     return render_to_response('signup.html', context_dict, context)
    return render_to_response('compareassessment.html',context_dict, context)

@csrf_exempt
@login_required(login_url="/login/")
def country(request):
    context_dict={}
    country=[]
    context = RequestContext(request)
    cursor = connection.cursor()
    cursor.execute("SELECT * from blog_country order by id desc")
    result = cursor.fetchall()
    x = cursor.description
    for r in result:
        i = 0
        d = {}
        while i < len(x):
            d[x[i][0]] = r[i]
            i = i+1
        country.append(d)
    context_dict['country_list'] = country
    if request.POST:
        opt=request.POST['opt']
        if opt == "Add":
            country_name = request.POST['country_name']
            iso_code = request.POST['iso_code']
            country = Country()
            country.country_name = country_name
            country.iso_code = iso_code
            country.save()
            return HttpResponseRedirect('/country/')
        elif opt == "Edit":
            country_name = request.POST['country_name']
            iso_code = request.POST['iso_code']
            cid=request.POST['id']
            to_update = Country.objects.filter(id=cid).update(country_name=country_name, iso_code=iso_code )  
            return HttpResponseRedirect('/country/')
        elif opt == "ChangeStatus":
            is_active = request.POST['is_active']
            cid=request.POST['id']
            to_update = Country.objects.filter(id=cid).update(is_active=is_active) 
           #print (to_update) 
            return HttpResponseRedirect('/country/')
        elif opt == "Delete":
            cid=request.POST['id']
            instance = Country.objects.get(id=cid)
            instance.delete()
            return HttpResponseRedirect('/country/')
    current_user = request.user
    # context_dict['unread_chat'] =notifcation(int(current_user.id))
    # context_dict['media_url'] = settings.S3_MEDIA_URL
    return render_to_response('country.html', context_dict, context)

@csrf_exempt
@login_required(login_url="/login/")
def industry(request):
    context_dict={}
    industry=[]
    context = RequestContext(request)
    cursor = connection.cursor()
    cursor.execute("SELECT * from blog_industry order by id desc")
    result = cursor.fetchall()
    x = cursor.description
    for r in result:
        i = 0
        d = {}
        while i < len(x):
            d[x[i][0]] = r[i]
            i = i+1
        industry.append(d)
    context_dict['industry_list'] = industry
    if request.POST:
        opt=request.POST['opt']
        if opt == "Add":
            industry_name = request.POST['industry_name']
            # iso_code = request.POST['iso_code']
            industry = Industry()
            industry.industry_name = industry_name
            industry.save()
            return HttpResponseRedirect('/industry/')
        elif opt == "Edit":
            industry_name = request.POST['industry_name']
            # iso_code = request.POST['iso_code']
            cid=request.POST['id']
            to_update = Industry.objects.filter(id=cid).update(industry_name=industry_name )  
            return HttpResponseRedirect('/industry/')
        elif opt == "ChangeStatus":
            is_active = request.POST['is_active']
            cid=request.POST['id']
            to_update = Industry.objects.filter(id=cid).update(is_active=is_active) 
           #print (to_update) 
            return HttpResponseRedirect('/industry/')
        # elif opt == "ChangeStatus":
        #     is_active = request.POST['is_active']
        #     cid=request.POST['id']
        #     to_update = Country.objects.filter(id=cid).update(is_active=is_active) 
        #    #print (to_update) 
        #     return HttpResponseRedirect('/country/')
        elif opt == "Delete":
            cid=request.POST['id']
            instance = Industry.objects.get(id=cid)
            instance.delete()
            return HttpResponseRedirect('/industry/')
    current_user = request.user
    # context_dict['unread_chat'] =notifcation(int(current_user.id))
    # context_dict['media_url'] = settings.S3_MEDIA_URL
    return render_to_response('industry.html', context_dict, context)

@login_required(login_url="/login/")
def editindustry(request,cid):
    context_dict={}
    industry=[]
    updatedata=[]
    context = RequestContext(request)
    cursor = connection.cursor()
    cursor.execute("SELECT * from blog_industry")
    result = cursor.fetchall()
    x = cursor.description
    for r in result:
        i = 0
        d = {}
        while i < len(x):
            d[x[i][0]] = r[i]
            i = i+1
        industry.append(d)
    context_dict['industry_list'] = industry
    context_dict['opt'] = "Edit"
    cur = connection.cursor()
    args=[cid]
    cur.execute("SELECT * from blog_industry where id = %s",args)
    editresult = cur.fetchall()
    x = cursor.description
    for r in editresult:
        i = 0
        d = {}
        while i < len(x):
            d[x[i][0]] = r[i]
            i = i+1
        updatedata.append(d)
    #print(editresult)
    context_dict['editindustry'] = updatedata
    current_user = request.user
    # context_dict['unread_chat'] =notifcation(int(current_user.id))
    # context_dict['media_url'] = settings.S3_MEDIA_URL
    return render_to_response('industry.html', context_dict, context)

@csrf_exempt
@login_required(login_url="/login/")
def changeindustryaction(request):
    context_dict = {}
    context = RequestContext(request)
    newid   =   request.POST['ids']
    if request.POST:
        opt=request.POST['opt']
        ids=json.loads(newid)
        if opt == "Delete":
            for pid in ids:
                instance = Industry.objects.get(id=pid)
                instance.delete()
            messages.success(request, 'Delete Record Successfully')   
            return HttpResponseRedirect('/industry/')
        elif opt == "Disable":
            for pid in ids:
                industry = Industry.objects.get(id=pid)
                industry.is_active = 0
                industry.save()  
            messages.success(request, 'Status Deactive Successfully')    
            return HttpResponseRedirect('/industry/')
        elif opt == "Enable":
            for pid in ids:
                industry = Industry.objects.get(id=pid)
                industry.is_active = 1
                industry.save()  
            messages.success(request, 'Status Active Successfully')    
            return HttpResponseRedirect('/industry/')
    current_user = request.user
    # context_dict['unread_chat'] =notifcation(int(current_user.id))
    # context_dict['media_url'] = settings.S3_MEDIA_URL
    return HttpResponseRedirect('/industry/')


@csrf_exempt
@login_required(login_url="/login/")
def client(request):
    context_dict={}
    client=[]
    industry=[]
    context = RequestContext(request)
    cursor = connection.cursor()
    cursor.execute("SELECT * from blog_client c left join blog_industry i on c.industry_id = i.id where c.user_id = "+ str(request.user.id) +" order by c.id desc")
    result = cursor.fetchall()
    x = cursor.description
    for r in result:
        i = 0
        d = {}
        while i < len(x):
            d[x[i][0]] = r[i]
            i = i+1
        client.append(d)
    context_dict['client_list'] = client
    cursor = connection.cursor()
    cursor.execute("SELECT * from blog_industry")
    result = cursor.fetchall()
    x = cursor.description
    for r in result:
        i = 0
        d = {}
        while i < len(x):
            d[x[i][0]] = r[i]
            i = i+1
        industry.append(d)
    context_dict['industry_list'] = industry 
    if request.POST:
        opt=request.POST['opt']
        if opt == "Add":
            client_name = request.POST['client_name'] 
            industry_id = request.POST['industry']
            client = Client()
            client.user_id = request.user.id
            client.client_name = client_name
            client.industry_id = industry_id
            client.save()

            membershipClient = MembershipClient()
            membershipClient.client_id = client.id
            membershipClient.membership_id = Membership.objects.get(user_id=request.user.id).id
            membershipClient.save()

            return HttpResponseRedirect('/client/')
        elif opt == "Edit":
            client_name = request.POST['client_name']
            industry_id = request.POST['industry']
            # iso_code = request.POST['iso_code']
            cid=request.POST['id']
            to_update = Client.objects.filter(id=cid).update(client_name=client_name, industry_id= industry_id )  
            return HttpResponseRedirect('/client/')
        elif opt == "ChangeStatus":
            is_active = request.POST['is_active']
            cid=request.POST['id']
            to_update = Client.objects.filter(id=cid).update(is_active=is_active) 
           #print (to_update) 
            return HttpResponseRedirect('/client/')
        # elif opt == "ChangeStatus":
        #     is_active = request.POST['is_active']
        #     cid=request.POST['id']
        #     to_update = Country.objects.filter(id=cid).update(is_active=is_active) 
        #    #print (to_update) 
        #     return HttpResponseRedirect('/country/')
        elif opt == "Delete":
            cid=request.POST['id']
            instance = Client.objects.get(id=cid)
            instance.delete()
            return HttpResponseRedirect('/client/')
    current_user = request.user
    # context_dict['unread_chat'] =notifcation(int(current_user.id))
    # context_dict['media_url'] = settings.S3_MEDIA_URL
    return render_to_response('client.html', context_dict, context)

@login_required(login_url="/login/")
def editclient(request,cid):
    context_dict={}
    client=[]
    industry=[]
    updatedata=[]
    context = RequestContext(request)
    cursor = connection.cursor()
    # cursor.execute("SELECT c.id as id, c.client_name as client_name, i.industry_name = industry_name, i.id = industry_id from blog_client c left join blog_industry i on c.industry_id = i.id order by c.id desc")
    cursor.execute("SELECT * from blog_client")
    result = cursor.fetchall()
    x = cursor.description
    for r in result:
        i = 0
        d = {}
        while i < len(x):
            d[x[i][0]] = r[i]
            i = i+1
        client.append(d)
    context_dict['client_list'] = client
    context_dict['opt'] = "Edit"
    cur = connection.cursor()
    args=[cid]
    cur.execute("SELECT * from blog_client where id = %s",args)
    editresult = cur.fetchall()
    x = cursor.description
    for r in editresult:
        i = 0
        d = {}
        while i < len(x):
            d[x[i][0]] = r[i]
            i = i+1
        updatedata.append(d)
    print(editresult)
    context_dict['editclient'] = updatedata
    current_user = request.user
    cursor = connection.cursor()
    cursor.execute("SELECT * from blog_industry")
    result = cursor.fetchall()
    x = cursor.description
    for r in result:
        i = 0
        d = {}
        while i < len(x):
            d[x[i][0]] = r[i]
            i = i+1
        industry.append(d)
    context_dict['industry_list'] = industry 
    # context_dict['unread_chat'] =notifcation(int(current_user.id))
    # context_dict['media_url'] = settings.S3_MEDIA_URL
    return render_to_response('client.html', context_dict, context)

@csrf_exempt
@login_required(login_url="/login/")
def changeclientaction(request):
    context_dict = {}
    context = RequestContext(request)
    newid   =   request.POST['ids']
    if request.POST:
        opt=request.POST['opt']
        ids=json.loads(newid)
        if opt == "Delete":
            for pid in ids:
                instance = Client.objects.get(id=pid)
                instance.delete()
            messages.success(request, 'Delete Record Successfully')   
            return HttpResponseRedirect('/client/')
        elif opt == "Disable":
            for pid in ids:
                client = Client.objects.get(id=pid)
                client.is_active = 0
                client.save()  
            messages.success(request, 'Status Deactive Successfully')    
            return HttpResponseRedirect('/client/')
        elif opt == "Enable":
            for pid in ids:
                client = Client.objects.get(id=pid)
                client.is_active = 1
                client.save()  
            messages.success(request, 'Status Active Successfully')    
            return HttpResponseRedirect('/client/')
    current_user = request.user
    # context_dict['unread_chat'] =notifcation(int(current_user.id))
    # context_dict['media_url'] = settings.S3_MEDIA_URL
    return HttpResponseRedirect('/client/')


@login_required(login_url="/login/")
def editcountry(request,cid):
    context_dict={}
    country=[]
    updatedata=[]
    context = RequestContext(request)
    cursor = connection.cursor()
    cursor.execute("SELECT * from blog_country")
    result = cursor.fetchall()
    x = cursor.description
    for r in result:
        i = 0
        d = {}
        while i < len(x):
            d[x[i][0]] = r[i]
            i = i+1
        country.append(d)
    context_dict['country_list'] = country
    context_dict['opt'] = "Edit"
    cur = connection.cursor()
    args=[cid]
    cur.execute("SELECT * from blog_country where id = %s",args)
    editresult = cur.fetchall()
    x = cursor.description
    for r in editresult:
        i = 0
        d = {}
        while i < len(x):
            d[x[i][0]] = r[i]
            i = i+1
        updatedata.append(d)
    #print(editresult)
    context_dict['editcountry'] = updatedata
    current_user = request.user
    # context_dict['unread_chat'] =notifcation(int(current_user.id))
    # context_dict['media_url'] = settings.S3_MEDIA_URL
    return render_to_response('country.html', context_dict, context)

@login_required(login_url="/login/")
def changecountryaction(request):
    context_dict = {}
    context = RequestContext(request)
    newid   =   request.POST['ids']
    if request.POST:
        opt=request.POST['opt']
        ids=json.loads(newid)
        if opt == "Delete":
            for pid in ids:
                instance = Country.objects.get(id=pid)
                instance.delete()
            messages.success(request, 'Delete Record Successfully')   
            return HttpResponseRedirect('/country/')
        elif opt == "Disable":
            for pid in ids:
                country = Country.objects.get(id=pid)
                country.is_active = 0
                country.save()  
            messages.success(request, 'Status Deactive Successfully')    
            return HttpResponseRedirect('/country/')
        elif opt == "Enable":
            for pid in ids:
                country = Country.objects.get(id=pid)
                country.is_active = 1
                country.save()  
            messages.success(request, 'Status Active Successfully')    
            return HttpResponseRedirect('/country/')
    current_user = request.user
    # context_dict['unread_chat'] =notifcation(int(current_user.id))
    # context_dict['media_url'] = settings.S3_MEDIA_URL
    return HttpResponseRedirect('/country/')


class BlogListView(ListView):
    model = Post
    template_name = 'home.html'


class BlogDetailView(DetailView):
    model = Post
    template_name = 'post_detail.html'
