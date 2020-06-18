from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import HttpResponse,redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate ,login ,logout
from polls.models import UserFollowing,QuestionTable,Groupcode
from django.http import HttpResponseRedirect


from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from .tokens import account_activation_token
from django.core.mail import EmailMessage
# Create your views here.


def index(request):
    if request.user.is_authenticated:
        following = UserFollowing.objects.filter(user__exact = request.user).count()
        followers = UserFollowing.objects.filter(following__exact = request.user).count()
        params = {
            'followers':followers,
            'following':following
        }
        return render(request,'index.html',params)
    else:
        return render(request,'index.html')

def passreset(request):
    return render(request,'passreset.html')

def signup(request):
    if request.method == 'POST':
        username = request.POST['susername']
        firstname = request.POST['sfirstname']
        lastname =request.POST['slastname']
        email =request.POST['semail']
        password =request.POST['spassword']
        password2 = request.POST['spassword2']

        try:
            user = User.objects.get(username__exact = username)
            messages.error(request,"Username should be unique.")
            return redirect('home')
        except:
            pass
        try:
            email = User.objects.get(email__exact = email)
            messages.error(request,"This email id is already in use")
            return redirect('home')
        except:
            pass
        # add parameters checking prog   
        if len(username) > 10:
            messages.error(request,"Username must be under 10 characters")
            return redirect('home')
        

        if password != password2:
            messages.error(request,"passwords do not match")
            return redirect('home')
        
        # make user 
        myuser = User.objects.create_user(username ,email ,password)
        myuser.first_name = firstname
        myuser.last_name = lastname
        myuser.is_active = False
        myuser.save()
        messages.success(request, 'Profile is created.')

        current_site = get_current_site(request)

        body_msg = render_to_string('acc_active_email.html', {
                'user':myuser, 'domain':current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),
                'token': account_activation_token.make_token(myuser),
            })
        
        # Sending activation link in terminal
        # user.email_user(subject, message)
        mail_subject = 'Activate your voting account.'
        # to_email = form.cleaned_data.get('email')
        send_email = EmailMessage(mail_subject, body_msg, to=[email])
        send_email.send()


        return redirect('home')
    else:
        return HttpResponse("Error 404")

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        messages.success(request,"Email verified!!!. Succesfully logged in.")
        return redirect('home')
    else:
        return HttpResponse('Activation link is invalid!')
        
def handlelogin(request):
    if request.method == 'POST':
        password = request.POST['lpassword']
        email = request.POST['lemail']
        try:
            username = User.objects.get(email=email.lower()).username
            user_active = User.objects.get(email=email.lower()).is_active
            
            if user_active is False:
                messages.error(request,"Please confirm your email. Email verification link has sent to your account.")
                return redirect('home')
            
            user = authenticate(username = username, password = password)

            if user is not None:
                login(request, user)
                messages.success(request,"succesfully logged in.")
                return redirect('home')
            
            else:
                messages.error(request, "Invalid Credentials , please try again")
                return redirect('home')
        except:
            messages.error(request, "Invalid Credentials , please try again")
            return redirect('home')
                
def handlelogout(request):
    logout(request)
    messages.success(request, "Logout Succesfully.")
    return redirect('home')

def search(request):
    if request.user.is_authenticated:
        query = request.GET['search']
        querysearch = User.objects.filter(username__icontains = query).exclude(username__exact = request.user).all()
        following = UserFollowing.objects.filter(user__exact = request.user).count()
        followers = UserFollowing.objects.filter(following__exact = request.user).count()
        params = {
            'result': querysearch,
            'following':following,
            'followers':followers,
        }
        return render(request,'search.html',params)
    else:
        return HttpResponse('pela member ban bhai')

    
def following(request):
    try:
        followingnum = UserFollowing.objects.filter(user__exact = request.user).count()
        followers = UserFollowing.objects.filter(following__exact = request.user).count()
        following = UserFollowing.objects.filter(user__exact = request.user).all()
        params = {
            'result':following,
            'following':followingnum,
            'followers':followers,
        }
        return render(request,"following.html",params)
    except:
        return render(request,"following.html")
    

def followers(request):
    try:
        followingnum = UserFollowing.objects.filter(user__exact = request.user).count()
        followersnum = UserFollowing.objects.filter(following__exact = request.user).count()
        followers = UserFollowing.objects.filter(following__exact = request.user).all()
        params = {
            'result':followers,
            'following':followingnum,
            'followers':followersnum,
        }
        return render(request,"followers.html",params)
    except:
        followingnum = UserFollowing.objects.filter(user__exact = request.user).count()
        followers = UserFollowing.objects.filter(following__exact = request.user).count()

        params = {
            'following':followingnum,
            'followers':followers,
        }
        return render(request,"followers.html",params)

def profile(request):
    userinfo = User.objects.filter(username__exact = request.user).get()
    params = {
        'result':userinfo,
    }
    return render(request,"profile3.html",params)

def follow(request):
    if request.method== 'POST':
        tofollow = request.POST["followname"]
        myid = request.user

        finfollow = User.objects.get(username__exact = tofollow)
        addfollowing = UserFollowing(user = myid, following = finfollow)

        addfollowing.save()
        
        return redirect('userprofile',username =tofollow)
    else:
        return HttpResponse('404 Error')


def unfollow(request):
    if request.method == 'POST':
        tounfollow = request.POST["unfollowuser"]
        myid = request.user
        finunfollow = User.objects.filter(username__exact = tounfollow).get()
        obj = UserFollowing.objects.get(user = myid,following = finunfollow)
        obj.delete()

        return redirect('userprofile',username = tounfollow)
    else:
        return HttpResponse('404 Error')

def askquestion(request):

    followingnum = UserFollowing.objects.filter(user__exact = request.user).count()
    followers = UserFollowing.objects.filter(following__exact = request.user).count()
    params = {
        'following':followingnum,
        'followers':followers,
    }
    return render(request,"askque.html",params)

def removeuser(request):
    if request.method == 'POST':
        toremove = request.POST["removeusername"]
        finalremove = User.objects.filter(username__exact = toremove).get()
        myrid = request.user
        name = UserFollowing.objects.get(user =finalremove ,following = myrid)
        name.delete()
        return redirect("followers")
    else:
        return HttpResponse('404 error')

def userprofile(request,username):
    
    if request.method == 'POST':
        userprofile = request.POST['profilename']
        idofuser = request.POST['idofuser']
        everyinfos = User.objects.filter(username__exact = userprofile).get()
        try:
            jem = UserFollowing.objects.filter(user__exact = request.user,following__exact = idofuser).get()        
            followingnum = UserFollowing.objects.filter(user__exact = request.user).count()
            followers = UserFollowing.objects.filter(following__exact = request.user).count()
            userfollowing = UserFollowing.objects.filter(user__exact = everyinfos).count()
            userfollowers = UserFollowing.objects.filter(following__exact = everyinfos).count()
            text = 'Unfollow'
            params = {
                'result':everyinfos,
                'following':followingnum,
                'followers':followers,
                'userfollowing':userfollowing,
                'userfollowers':userfollowers,
                'text':text,
            }
            return render(request,"profile3.html",params)
        except:

            everyinfos = User.objects.filter(username__exact = userprofile).get()
            followingnum = UserFollowing.objects.filter(user__exact = request.user).count()
            followers = UserFollowing.objects.filter(following__exact = request.user).count()
            userfollowing = UserFollowing.objects.filter(user__exact = everyinfos).count()
            userfollowers = UserFollowing.objects.filter(following__exact = everyinfos).count()
            text='Follow'
            params = {
                'result':everyinfos,
                'following':followingnum,
                'followers':followers,
                'userfollowing':userfollowing,
                'userfollowers':userfollowers,
                'text':text,
            }
            return render(request,"profile3.html",params)
        

    else:
        everyinfos = User.objects.filter(username__exact = username).get()
        idofuser = everyinfos.id
        try:
            jem = UserFollowing.objects.filter(user__exact = request.user,following__exact = idofuser).get()  
            followingnum = UserFollowing.objects.filter(user__exact = request.user).count()
            followers = UserFollowing.objects.filter(following__exact = request.user).count()
            userfollowing = UserFollowing.objects.filter(user__exact = everyinfos).count()
            userfollowers = UserFollowing.objects.filter(following__exact = everyinfos).count()
            text = 'Unfollow'
            params = {
                'result':everyinfos,
                'following':followingnum,
                'followers':followers,
                'userfollowing':userfollowing,
                'userfollowers':userfollowers,
                'text':text,
            }
            return render(request,"profile3.html",params)

        except:
            followingnum = UserFollowing.objects.filter(user__exact = request.user).count()
            followers = UserFollowing.objects.filter(following__exact = request.user).count()
            userfollowing = UserFollowing.objects.filter(user__exact = everyinfos).count()
            userfollowers = UserFollowing.objects.filter(following__exact = everyinfos).count()
            text='Follow'
            params = {
                'result':everyinfos,
                'following':followingnum,
                'followers':followers,
                'userfollowing':userfollowing,
                'userfollowers':userfollowers,
                'text':text,
            }
            return render(request,"profile3.html",params)
        