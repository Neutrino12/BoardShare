# Create your views here.
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from app_boardShare.models import Board, Pin, UserDetails, Comments
from PIL import Image as PImage
from django.utils.html import strip_tags
from shutil import move
from django.conf import settings
import urllib

def boardShare_main(request):
    context = {'error': ''}
    username = strip_tags(request.POST.get('user'))
    password = strip_tags(request.POST.get('pwd'))
    if (not request.POST):
        return render(request, 'login.html', context)
    if((username=='') and (password=='')):
        return render(request, 'login.html', context)

    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
            return redirect('front')
        else:
            context = {'error': 'You have been logged out!'}
    else:
        context = {'error':'Invalid Username or Password!'}

    return render(request, 'login.html', context)

def register_new_user(request):
    context = {'error':''}

    if (not request.POST):
        return render(request, 'registration.html', context)
    first_name = strip_tags(request.POST.get('firstName'))
    last_name = strip_tags( request.POST.get('lastName'))
    username = strip_tags(request.POST.get('userName'))
    email = strip_tags(request.POST.get('emailAddress'))
    confirm_email = strip_tags(request.POST.get('confirmEmail'))
    password = strip_tags(request.POST.get('password'))
    confirm_password = strip_tags(request.POST.get('confirmPassword'))
    gender = strip_tags(request.POST.get('sex'))

    # Check for form completeness
    if((not first_name) and (not last_name) and (not email) and (not confirm_email) and (not username) and (not password) and (not confirm_password)):
        return render(request,'registration.html')
    if (not first_name):
        return render(request, 'registration.html', {'error':'Please enter Full name'})
    if (not last_name):
        return render(request, 'registration.html', {'error':'Please enter Full name'})
    if (not username):
        return render(request, 'registration.html', {'error':'Please enter username'})
    if (not email):
        return render(request, 'registration.html', {'error':'Please enter an Email Address'})
    if (not password):
        return render(request, 'registration.html', {'error':'Please enter a password'})
    if (not gender):
        return render(request, 'registration.html', {'error':'You need to specify your gender'})
    if(email!=confirm_email):
        return render(request, 'registration.html', {'error':'Email Addresses do not match'})
    if(password!=confirm_password):
        return render(request, 'registration.html', {'error':'Passwords do not match'}) 

    try:	 
    # create new user
        user = User.objects.create_user(username, email, password)
        user.first_name = first_name
        user.last_name = last_name
        if gender == 'male':
            uploaded_file = 'http://www.clker.com/cliparts/5/9/4/c/12198090531909861341man%20silhouette.svg.med.png'
        else:
            uploaded_file = 'http://www.clker.com/cliparts/0/4/3/4/12198090302006169125female%20silhouette.svg.med.png'
        curr_user_details = UserDetails(user=user, gender=gender, about_me='I am awesome' , data_local=uploaded_file)    
        user.userdetails = curr_user_details
        curr_user_details.save()
        user.save()
    except:
        context = {'error':'User already registered!'}
        return render(request, 'register.html', context)

    context = {}
    return render(request, 'login.html', context)

def display_front_page(request):
    if not request.user.is_authenticated():
        context = {'error':'You need to login first!'}
        return render(request, 'login.html', context)

    return redirect('allpins')

def display_search(request):
    if not request.user.is_authenticated():
        context = {'error':'You need to login first!'}
        return render(request, 'search.html', context)

    return render(request, 'search.html') 

def display_personal_page(request):

    if not request.user.is_authenticated():
        context = {'error':'You need to login first!'}
        return render(request, 'login.html', context)
        
    return redirect('myboards')

def modify_settings(request):
    context = {'error':''}
    if not request.user.is_authenticated():
        context = {'error':'You need to login first!'}
        return render(request, 'login.html', context)

    if (not request.POST):
        return render(request,'settings.html')

    email = strip_tags(request.POST.get('emailAddress'))
    gender = strip_tags(request.POST.get('sex'))
    first_name = strip_tags(request.POST.get('firstName'))
    last_name = strip_tags(request.POST.get('lastName'))
    about_me = strip_tags(request.POST.get('aboutMe'))

    curr_user = User.objects.get(username=request.user.username)
    curr_user_details = UserDetails.objects.get(user=curr_user)
    if email:
        curr_user.email = email
    if first_name:
        curr_user.first_name = first_name
    if last_name:
        curr_user.last_name = last_name
    if gender:
        curr_user_details.gender = gender
    if about_me:
        curr_user_details.about_me = about_me
    if gender == 'male':
        curr_user_details.data_local = 'http://www.clker.com/cliparts/5/9/4/c/12198090531909861341man%20silhouette.svg.med.png'
    if gender == 'female':
        curr_user_details.data_local = 'http://www.clker.com/cliparts/0/4/3/4/12198090302006169125female%20silhouette.svg.med.png'
	
	# get the uploaded file	
    # uploaded_file = request.FILES.get('profpic')
    # print uploaded_file
    # if (uploaded_file.size>(10**6)):
        # context = {'error':'BoardShare does not permit image sizes over 1MB - Sorry!','boardContent':'1','boards':boards}
        # return render(request, 'settings.html', context)

    # if the image file cannot be open, then it is not a valid image; image is stored in media root
    # try:
        # im = PImage.open( uploaded_file )
    # except:
        # context = {'error':'Uploaded profile image is not a valid type - Please Try Again!','boardContent':'1','boards':boards}
        # return render(request, 'settings.html', context)
    # curr_user_details.data_local = uploaded_file 

    curr_user_details.save()
    curr_user.save()
    
    #return render(request,'settings.html')
    return redirect('personal')
    
def add_new_pin(request):
    context = {'error':''}
    if not request.user.is_authenticated():
        context = {'error':'You need to login first!'}
        return render(request, 'login.html', context)
		
    curr_user = User.objects.get(username=request.user)
    boards = Board.objects.filter(user= curr_user)
    if len(boards)<1:
        context = {'error':'You do not have any boards => Please create a board!'}
    #    return redirect('addboard')

    context = {'boardContent':'1','boards':boards}
	
    if (not request.POST):
        return render(request,'addpin.html', context)

    description = strip_tags(request.POST.get('description'))
    if not description:
        context = {'error':'Please enter a description for your pin!','boardContent':'1','boards':boards}
        return render(request, 'addpin.html', context)

    board = request.POST.get('board')
    if not board:
        context = {'error':'You need to specify a board','boardContent':'1','boards':boards}
        return render(request, 'uploadpin.html', context)
		
    link = strip_tags(request.POST.get('link'))
    if not link:
        # Add this as a text note #
        pin = Pin(data_type='text', num_likes=1, data_text=description)
    else:
        pin = Pin(data_type='media', num_likes=1, data_local=link, data_text=description)
		
    try:
        fd = urllib.urlopen(link)
    except:
        context = {'error':'Please input a valid url!','boardContent':'1','boards':boards}
        return render(request, 'addpin.html', context)

    if not ( str(link).endswith('.png') or str(link).endswith('.jpg') or str(link).endswith('.gif') ):
        context = {'error':'Image type not supported.','boardContent':'1','boards':boards}
        return render(request, 'addpin.html', context)
    try:
        curr_user = User.objects.get(username=request.user.username)
        curr_board = Board.objects.get(pk=board);
        curr_user_details = UserDetails.objects.get(user=curr_user)
        curr_user_details.num_pins = curr_user_details.num_pins + 1
        curr_user_details.save()
        pin = Pin(data_type='image', num_likes=1, user=curr_user, board_title=curr_board.title, data_local = link, data_text=description)
        pin.save()
        pin.board.add(curr_board)
    except:
        context = {'error':'Url length exceeded.!','boardContent':'1','boards':boards}
        return render(request, 'addpin.html', context)
		
    return redirect('personal')
	
def edit_board(request):
    context = {'error':''}
    if not request.user.is_authenticated():
        context = {'error':'You need to login first!'}
        return render(request, 'login.html', context)

    boards = Board.objects.all()  
    categories = []
    for b in boards:
        categories.append(b.category)
    categories = list(set(categories))  
    context = {'categories':categories}
    
    if (not request.POST):
        return render(request,'editboard.html', context)

    title = strip_tags(request.POST.get('title'))
    category = strip_tags(request.POST.get('category'))
    description = strip_tags(request.POST.get('description'))

    if not title:
        context = {'error':'You need to specify a title'}
        return render(request, 'editboard.html', context)
    if not category:
        context = {'error':'You need to specify a category'}
        return render(request, 'editboard.html', context)
    if not description:
        context = {'error':'You need to specify a description'}
        return render(request, 'editboard.html', context)
    
    curr_user = User.objects.get(username=request.user.username)
    
    board = Board(title=title, description=description, category=category, user=curr_user)
    board.save()
    
    return render('personal')


def upload_new_pin(request):
    context = {'error':''}
    if not request.user.is_authenticated():
        context = {'error':'You need to login first!'}
        return render(request, 'login.html', context)
    
    curr_user = User.objects.get(username=request.user)
    boards = Board.objects.filter(user= curr_user)
    if len(boards)<1:
        context = {'error':'You do not have any boards => Please create a board!'}
        #return redirect('addboard')

    context = {'boardContent':'1','boards':boards}

    if (not request.POST):
		return render(request,'uploadpin.html',context)

    # get description fromm form check description validity
    description = strip_tags(request.POST.get('description'))
    if not description:
        context = {'error':'Please enter a description for your pin!','boardContent':'1','boards':boards}
        return render(request, 'uploadpin.html', context)

    # get the board to get to
    board = request.POST.get('board')
    if not board:
        context = {'error':'You need to specify a board','boardContent':'1','boards':boards}
        return render(request, 'uploadpin.html', context)
	
    # get the uploaded file	
    uploaded_file = request.FILES.get('pinfile')
    if (uploaded_file.size>(10**6)):
        context = {'error':'BoardShare does not permit Pin sizes over 1MB - Sorry!','boardContent':'1','boards':boards}
        return render(request, 'uploadpin.html', context)

    # if the image file cannot be open, then it is not a valid image; image is stored in media root
    try:
        im = PImage.open( uploaded_file )
    except:
        context = {'error':'Uploaded File is not a valid image type - Please Try Again!','boardContent':'1','boards':boards}
        return render(request, 'uploadpin.html', context)

    # update userdetail with number of pins
    curr_user = User.objects.get(username=request.user.username)
    curr_board = Board.objects.get(pk=board);
    curr_user_details = UserDetails.objects.get(user=curr_user)
    curr_user_details.num_pins = curr_user_details.num_pins + 1
    curr_user_details.save()

    ## move pin to static folder for rendering ##

    pin = Pin(data_type='uploaded_image', num_likes=1, user=curr_user, board_title=curr_board.title, data_local = uploaded_file, data_text=description)
    pin.save()
    pin.board.add(curr_board)

    return redirect('personal')


def add_new_board(request):
    context = {'error':''}
    if not request.user.is_authenticated():
        context = {'error':'You need to login first!'}
        return render(request, 'login.html', context)

    #categories = Category.objects.all()#get(user = request.user)
    #context = {'categories':categories}
    
    if (not request.POST):
        return render(request,'addboard.html', context)
    title = strip_tags(request.POST.get('title'))
    category = strip_tags(request.POST.get('category'))
    description = strip_tags(request.POST.get('description'))

    if not title:
        context = {'error':'You need to specify a title'}
        return render(request, 'addboard.html', context)
    if not description:
        context = {'error':'You need to specify a description'}
        return render(request, 'addboard.html', context)
    if not category:
        context = {'error':'You need to specify a category'}
        return render(request, 'addboard.html', context)
    
    curr_user = User.objects.get(username=request.user.username)
    curr_user_details = UserDetails.objects.get(user=curr_user)
    curr_user_details.num_boards = curr_user_details.num_boards + 1
    curr_user_details.save()	
    board = Board(title=title, description=description, category=category, user=curr_user)
    board.save()
    return redirect('personal')

def repin(request):
    context = {'error':''}
    if not request.user.is_authenticated():
        context = {'error':'You need to login first!'}
        return render(request, 'login.html', context)

    curr_user = User.objects.get(username = request.user)
    
    pin_id = request.POST.get('pin_id')
    if not pin_id:
        return redirect('all_pins')

    board_id = request.POST.get('board_id')
    if not board_id:
        boards = Board.objects.filter(user = curr_user)
        context = {'pin_id': pin_id, 'boards': boards}
        return render(request, 'repin.html', context)

    board = Board.objects.get(pk=board_id)  
    pin = Pin.objects.get(pk=pin_id)
    pin.board.add(board)
    curr_user_details = UserDetails.objects.get(user=curr_user)
    curr_user_details.num_pins = curr_user_details.num_pins + 1
    curr_user_details.save()
    return redirect('personal')


def like(request):
    context = {'error':''}
    if not request.user.is_authenticated():
        context = {'error':'You need to login first!'}
        return render(request, 'login.html', context)
    pin_id = request.POST.get('pin_id')
    if not pin_id:
        return redirect('all_pins')
    pin = Pin.objects.get(pk=pin_id)
    pin.num_likes = pin.num_likes+1
    pin.save()
    return redirect('allpins')		

def front_comment(request):
    context = {'error':''}
    if not request.user.is_authenticated():
        context = {'error':'You need to login first!'}
        return render(request, 'login.html', context)
    pin_id = request.POST.get('pin_id')
    if not pin_id:
        return redirect('all_pins')
    pin = Pin.objects.get(pk=pin_id)
    curr_user = User.objects.get(username = request.user)
    content = request.POST.get('content')
    comment = Comments(user=curr_user, pin=pin, content=content)
    comment.save()
    return redirect('allpins')		

def my_pins(request):
    context = {'error':''}
    if not request.user.is_authenticated():
        context = {'error':'You need to login first!'}
        return render(request, 'login.html', context)
    
    curr_user = User.objects.get(username = request.user)
    boards = Board.objects.filter(user = curr_user)
    
    gender = 1
    curr_userdetails = UserDetails.objects.get(user = curr_user)
    if curr_userdetails.gender == 'male':
        gender = 0

    pins = Pin.objects.all()
    pins_n = []
    relations = {}
    for board in boards:
        pins_in_board = Pin.objects.filter(board=board)
        for pin_in_board in pins_in_board:
            pins_n.append(pin_in_board)
    context = {'pinContent':'1','boards':boards,'pins':pins_n, 'gender':gender,'userdetails':curr_userdetails,'relations':relations,'num_pins':len(pins_n),'num_boards':len(boards)}
    return render(request,'personalpage.html', context)

def all_pins(request):
    context = {'error':''}
    if not request.user.is_authenticated():
        context = {'error':'You need to login first!'}
        return render(request, 'login.html', context)
        
    pins = Pin.objects.all()
    boards = Board.objects.all()
    categories = []
    for b in boards:
        categories.append(b.category)
    categories = list(set(categories))
    
    curr_user_details = UserDetails.objects.get(user=request.user)
    comments = Comments.objects.all()

    context = {'pins':pins, 'categories':categories, 'userdetails':curr_user_details, 'comments':comments,'userdetails':curr_user_details}
    return render(request,'frontpage.html', context)
	
def category_pins(request):
    context = {'error':''}
    if not request.user.is_authenticated():
        context = {'error':'You need to login first!'}
        return render(request, 'login.html', context)
        
    category = request.GET.get('category')
    boards = Board.objects.all()       
    #pins = Pin.objects.filter(board = boards)

    categories = []
    for b in boards:
        categories.append(b.category)
    
    categories = list(set(categories))   

    categorized_boards = Board.objects.filter(category = category)
    pins = []
    for cb in categorized_boards:
        cb_pins = Pin.objects.filter(board = cb)
        for cb_pin in cb_pins:
            pins.append(cb_pin)
    curr_user_details = UserDetails.objects.get(user=request.user)
    comments = Comments.objects.all()
    context = {'pins':pins, 'categories':categories, 'comments':comments,'userdetails':curr_user_details}
    return render(request,'frontpage.html', context)
	
def pop_pins(request):
    context = {'error':''}
    if not request.user.is_authenticated():
        context = {'error':'You need to login first!'}
        return render(request, 'login.html', context)
        
    pins = Pin.objects.all()
    pins = pins.extra(order_by = ['num_likes']);
    pins = pins.reverse()
	
    boards = Board.objects.all()
    categories = []
    for b in boards:
        categories.append(b.category)
    categories = set(categories)   
    curr_user_details = UserDetails.objects.get(user=request.user)
    comments = Comments.objects.all()
    context = {'pins':pins, 'categories':categories,'comments':comments,'userdetails':curr_user_details}

    return render(request,'frontpage.html', context)

## Filter results with current user ##
def my_boards(request):
    context = {'error':''}
    if not request.user.is_authenticated():
        context = {'error':'You need to login first!'}
        return render(request, 'login.html', context)
    
    curr_user = User.objects.get(username = request.user)
    boards = Board.objects.filter(user = curr_user)
    
    gender = 1
    curr_userdetails = UserDetails.objects.get(user = curr_user)
    if curr_userdetails.gender == 'male':
        gender = 0

    pins = Pin.objects.all()
    relations = {}
    for board in boards:
        pins_in_board = Pin.objects.filter(board=board)
        for pin_in_board in pins_in_board:
            relations.update({pin_in_board:board})
    context = {'boardContent':'1','boards':boards,'pins':pins, 'gender':gender,'userdetails':curr_userdetails,'relations':relations,'num_pins':len(pins),'num_boards':len(boards)}
    return render(request,'personalpage.html', context)

def all_boards(request):
    context = {'error':''}
    if not request.user.is_authenticated():
        context = {'error':'You need to login first!'}
        return render(request, 'login.html', context)
        
    boards = Board.objects.all()
    context = {'boardContent':'1','boards':boards}
    return render(request,'frontpage.html', context)

def search_pins(request):
    context = {'error':''}
    if not request.user.is_authenticated():
        context = {'error':'You need to login first!'}
        return render(request, 'login.html', context)
        
    keyword = str(request.GET.get('query'))

    boards = Board.objects.all()       
    pins_temp = Pin.objects.all()
    
    pins = []
    for pin in pins_temp:
        s = str(pin.data_text)
        if keyword in s:
            pins.append(pin)
	
    categories = []
    for b in boards:
        categories.append(b.category)

    categories = list(set(categories))   
    comments = Comments.objects.all()
    context = {'pinContent':'1','pins':pins, 'categories':categories,'keyword':keyword,'comments':comments}

    return render(request,'search.html', context)

def search_boards(request):
    context = {'error':''}
    if not request.user.is_authenticated():
        context = {'error':'You need to login first!'}
        return render(request, 'login.html', context)
        
    keyword = str(request.GET.get('query'))

    boards = Board.objects.all()       
    pins_temp = Pin.objects.all()
    
    boards_response = []
    for board in boards:
        s = str(board.description)
        if keyword in s:
            boards_response.append(board)
	
    categories = []
    for b in boards:
        categories.append(b.category)

    categories = list(set(categories))   
    pins = Pin.objects.all()
    relations = {}
    for board in boards:
        pins_in_board = Pin.objects.filter(board=board)
        for pin_in_board in pins_in_board:
            relations.update({pin_in_board:board})
    context = {'boardContent':'1','boards':boards_response,'pins':pins, 'categories':categories,'relations':relations,'keyword':keyword}
    return render(request,'search.html', context)

def search_pinners(request):
    return render(request,'search.html')

def change_password(request):
    context = {'error':''}
    if not request.user.is_authenticated():
        context = {'error':'You need to login first!'}
        return render(request, 'login.html', context)

    if (not request.POST):
        return render(request,'resetpassword.html')

    pw = strip_tags(request.POST.get('Password'))
    conpw = strip_tags(request.POST.get('ConfirmPassword'))
    if pw != conpw:
        context = {'error':'Password not consistent!'}
        return render(request,'resetpassword.html')

    curr_user = User.objects.get(username=request.user.username)
    curr_user.password = pw

    curr_user.save()
    
    #return render(request,'settings.html')
    return redirect('changepassword')
