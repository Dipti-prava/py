import base64
import logging
import os
import uuid
from datetime import datetime, timedelta

import pyotp
from django.core.files.base import ContentFile
from django.core.mail import send_mail
from django.http import HttpResponse
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from ..models import User, OTP
from ..serializer.department import UserSerializer
from ..utils.TOTPUtils import verify_otp
from ..utils.common import get_file_extension, create_unique_name
from ..utils.decoraters import IsAuthenticated, AllowAll
from ..utils.forms import LoginForm, generate_captcha, generate_captcha_image, store_captcha_with_identifier, \
    get_captcha_from_storage
from ..utils.validators import validate_phone_number, validate_email

logger = logging.getLogger(__name__)

logger.setLevel(logging.INFO)


@api_view(['POST'])
def send_otp(request):
    email = request.data.get('email')
    if not email:
        return Response({'statusCode': '0', 'error': 'Please provide email'}, status=400)
    print("email", email)
    is_valid = validate_email(email)
    if is_valid:
        return Response({'statusCode': '0', 'error': is_valid}, status=400)

    secret = pyotp.random_base32()
    totp = pyotp.TOTP(secret)
    otp = totp.now()
    print(otp)
    logger.info("OTP: %s", otp)
    # Send OTP via email
    subject = 'Verification OTP'
    message = f'''Your OTP is: {otp}
    It is valid for 10 minutes.
    
    WARNING: Please do not share this OTP with anyone.'''
    try:
        result = send_mail(subject, message, None, [email])
        print(result)
        if result == 1:
            save_otp_db(email, secret, otp)
            return Response({'statusCode': '1', 'message': 'OTP sent to your email'}, status=200)
        else:
            return Response({'statusCode': '0', 'error': 'Something Went Wrong!'}, status=400)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
def otp_verification(request):
    email = request.data.get('email')
    otp = request.data.get('otp')
    if not email:
        return Response({'statusCode': '0', 'error': 'Please provide email'}, status=400)
    is_valid = validate_email(email)
    if is_valid:
        return Response({'statusCode': '0', 'error': is_valid}, status=400)

    try:
        if not User.objects.filter(email=email).exists():
            return Response({'statusCode': '0', 'error': 'Email is not registered'}, status=400)
        if verify_otp(otp, email):
            return Response({'statusCode': '1', 'message': 'otp is valid', 'data': 1}, status=200)
        else:
            return Response({'statusCode': '0', 'message': 'invalid otp', 'data': 0}, status=200)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


def save_otp_db(email, secret, otp):
    otp_instance = OTP(key=email, otp_secret=secret, otp=otp)
    otp_instance.save()


@api_view(['POST'])
def create_password(request):
    email = request.data.get('email')
    password = request.data.get('password')
    confirm_password = request.data.get('confirm_password')

    if not email:
        return Response({'statusCode': '0', 'error': 'Please provide email'}, status=400)
    if not password:
        return Response({'statusCode': '0', 'error': 'Please provide password'}, status=400)
    if not confirm_password:
        return Response({'statusCode': '0', 'error': 'Please provide confirm password'}, status=400)
    is_valid = validate_email(email)
    if is_valid:
        return Response({'statusCode': '0', 'error': is_valid}, status=400)

    try:
        if not User.objects.filter(email=email).exists():
            return Response({'statusCode': '0', 'error': 'Email is not registered'}, status=400)
        if password != confirm_password:
            return Response({'statusCode': '0', 'messege': 'password and confirm password does not match.'}, status=400)

        user = User.objects.get(email=email)
        # user.password = confirm_password
        user.set_password(confirm_password)
        user.save()
        return Response({'statusCode': '1', 'message': 'password created'}, status=200)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
def signup(request):
    email = request.data.get('email')
    username = request.data.get('username')
    password = request.data.get('password')
    is_active = request.data.get('is_active')
    is_admin = request.data.get('is_admin')
    first_name = request.data.get('first_name')
    last_name = request.data.get('last_name')
    phone_no = request.data.get('phone_no')
    profile_pic = request.data.get('profile_pic')

    if not email:
        return Response({'statusCode': '0', 'error': 'Please provide email'}, status=400)
    if not username:
        return Response({'statusCode': '0', 'error': 'Please provide username'}, status=400)
    if not first_name:
        return Response({'statusCode': '0', 'error': 'Please provide first name'}, status=400)
    if not last_name:
        return Response({'statusCode': '0', 'error': 'Please provide last name'}, status=400)
    if not phone_no:
        return Response({'statusCode': '0', 'error': 'Please provide phone number'}, status=400)
    if not profile_pic:
        return Response({'statusCode': '0', 'error': 'Please provide profile pic'}, status=400)

    is_valid_email = validate_email(email)
    if is_valid_email:
        return Response({'statusCode': '0', 'error': is_valid_email}, status=400)

    if User.objects.filter(email=email).exists():
        return Response({'statusCode': '0', 'error': 'Email already Exists'}, status=200)

    is_valid = validate_phone_number(phone_no)
    if is_valid:
        return Response({'statusCode': '0', 'error': is_valid}, status=400)
    try:
        if profile_pic:
            format, docstr = profile_pic.split(';base64')
            if format not in ['data:image/jpg', 'data:image/jpeg', 'data:image/png']:
                return Response({'statusCode': '0', 'messege': 'only jpg, jpeg and png files are allowed.'}, status=400)
            extension = get_file_extension(format)
            image_data = base64.b64decode(docstr)
            size = len(image_data)
            size_mb = size / (1024 * 1024)
            if size_mb > 25:
                return Response({'statusCode': '0', 'messege': 'file size must be less than 25 MB'}, status=400)
            document_name = create_unique_name(first_name + '_' + last_name)
            document_name = document_name + '.' + extension
            document = ContentFile(image_data, name=document_name)

            user = User.objects.create_user(email=email, username=username, password=password, is_active=is_active,
                                            is_admin=is_admin, first_name=first_name, last_name=last_name,
                                            phone_no=phone_no,
                                            profile_pic=document)
            serializer = UserSerializer(user)

            return Response({'statusCode': '1', 'message': 'User created successfully', 'user': serializer.data},
                            status=201)
        else:
            return Response({'statusCode': '0', 'error': 'Please Provide Profile Pic'}, status=400)
    except Exception as e:
        return Response({'statusCode': '0', 'error': str(e)}, status=500)


@api_view(['GET'])
def captcha_image(request):
    request.session.cycle_key()
    captcha_challenge = generate_captcha()
    captcha_key = str(uuid.uuid4())

    # Store the captcha challenge with the unique identifier in the session
    store_captcha_with_identifier(request, captcha_key, captcha_challenge)

    cc = get_captcha_from_storage(request.session.session_key, captcha_key)  # Implement this retrieval logic

    image_buffer = generate_captcha_image(captcha_challenge)
    session_age = request.session.get_expiry_age()
    expiration_date = datetime.utcnow() + timedelta(seconds=session_age)
    expiration_date_str = expiration_date.strftime('%a, %d %b %Y %H:%M:%S GMT')

    response = HttpResponse(image_buffer.getvalue(), content_type='image/jpeg')
    # response['x-session-key'] = request.session.session_key

    response['Access-Control-Allow-Credentials'] = 'true'
    response['Access-Control-Allow-Headers'] = ', '.join(
        ['proxyId', 'Authorization', 'X-Requested-With', 'x-captcha-key', 'content-type', 'Set-Cookie',
         'Origin'])
    response['Access-Control-Expose-Headers'] = 'x-captcha-key,x-session-key, Set-Cookie'
    response['Allow'] = 'GET, OPTIONS'
    response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response['Vary'] = 'Origin, Accept, Cookie'
    response['x-captcha-key'] = captcha_key
    response['x-session-key'] = request.session.session_key
    response['X-Content-Type-Options'] = 'nosniff'
    response['X-Frame-Options'] = 'DENY'

    # Set the session cookie dynamically based on your logic
    response.set_cookie('sessionid', request.session.session_key, expires=expiration_date_str,
                        httponly=True, max_age=session_age, path='/', samesite='Lax', secure=True)

    return response


@api_view(['POST'])
def signin(request):
    print(request.headers)
    print(request.COOKIES.get('sessionid'))
    # session_id = request.COOKIES.get('sessionid')
    session_id = request.headers.get('x-session-key')
    captcha_key = request.headers.get('x-captcha-key')  # Identifier sent by the user
    captcha = request.data.get('captcha')  # Captcha response sent by the user
    captcha_challenge = get_captcha_from_storage(session_id, captcha_key)  # Implement this retrieval logic

    if captcha_challenge is None:
        return Response({'statusCode': '0', 'error': 'Invalid or expired captcha challenge'}, status=400)
    is_admin = False
    form = LoginForm(data=request.data)

    if form.is_valid():
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password')
        if not email:
            return Response({'statusCode': '0', 'error': 'Please provide email'}, status=400)

        if not password:
            return Response({'statusCode': '0', 'error': 'Please provide password'}, status=400)

        is_valid = validate_email(email)
        if is_valid:
            return Response({'statusCode': '0', 'error': is_valid}, status=400)

        user = User.objects.filter(email=email).first()
        if captcha != captcha_challenge:
            return Response({'statusCode': '0', 'error': 'Invalid CAPTCHA. Please try again.'}, status=400)

        if user is None:
            return Response({'statusCode': '0', 'error': 'Email does not exist'}, status=400)

        if not user.check_password(password):
            return Response({'error': 'Invalid email or password'}, status=400)

        # if password != user.password:
        #     return Response({'statusCode': '0', 'error': 'Invalid email or password'}, status=400)

        if not user.is_active:
            return Response({'statusCode': '0', 'error': 'User is not Active'}, status=400)
        if user.is_admin is True:
            is_admin = True
        else:
            is_admin = False
        user_data = {
            'user_id': user.user_id,
            'username': user.username,
            'email': user.email,
            "is_admin": is_admin
        }

        refresh = RefreshToken.for_user(user)
        refresh_token = str(refresh)
        access_token = str(refresh.access_token)
        user.last_login = timezone.now()
        user.save()
        # Return user data and token
        return Response({
            'message': 'Logged in successfully',
            'user_data': user_data,  # Example: Return the user's ID
            'access_token': access_token,
            'refresh_token': refresh_token
        }, status=200)
    else:
        # If the form is invalid, construct an error response
        errors = dict(form.errors.items())
        print(errors)
        return Response({'error': 'Something went wrong'}, status=400)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    refresh_token = request.data.get('refresh')
    try:
        # Add refresh token to the blacklist
        TokenBlacklist.objects.create(token=refresh_token)
    except:
        pass
    return Response({'message': 'Logged out successfully'}, status=200)


@api_view(['GET'])
@permission_classes([AllowAll])
def get_profile_details(request):
    profile_pic = ""
    try:
        user = User.objects.get(user_id=request.user.user_id)

        if user is None:
            return Response({'statusCode': '0', 'messege': 'User not found'}, status=200)

        with open(user.profile_pic.path, 'rb') as file:
            encoded_pic = base64.b64encode(file.read()).decode('utf-8')
        ext = user.profile_pic.path.split('.')[-1].lower()
        if ext in ['jpg', 'jpeg', 'png']:
            profile_pic = f"data:image/{ext};base64,{encoded_pic}"
        user_info = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "phone_no": user.phone_no,
            "email": user.email,
            "profile_pic_name": os.path.basename(user.profile_pic.path),
            "profile_pic": profile_pic
        }
        return Response({
            'statusCode': '1',
            'data': user_info
        }, status=200)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([AllowAll])
def update_profile(request):
    first_name = request.data.get('first_name')
    last_name = request.data.get('last_name')
    phone_no = request.data.get('phone_no')
    profile_pic = request.data.get('profile_pic')
    profile_pic_name = request.data.get('profile_pic_name')

    if not first_name:
        return Response({'statusCode': '0', 'error': 'Please provide first name'}, status=400)
    if not last_name:
        return Response({'statusCode': '0', 'error': 'Please provide last name'}, status=400)
    if not phone_no:
        return Response({'statusCode': '0', 'error': 'Please provide phone number'}, status=400)
    if not profile_pic:
        return Response({'statusCode': '0', 'error': 'Please provide profile pic'}, status=400)
    if not profile_pic_name:
        return Response({'statusCode': '0', 'error': 'Please provide profile pic name'}, status=400)

    if not all([first_name, last_name, phone_no, profile_pic, profile_pic_name]):
        return Response({'statusCode': '0', 'error': 'Missing required data'}, status=400)

    is_valid = validate_phone_number(phone_no)
    if is_valid:
        return Response({'statusCode': '0', 'error': is_valid}, status=400)

    try:
        user = User.objects.get(user_id=request.user.user_id)
    except User.DoesNotExist:
        return Response({'statusCode': '0', 'error': 'User not found'}, status=404)

    try:
        if profile_pic:
            format, docstr = profile_pic.split(';base64')
            if format not in ['data:image/jpg', 'data:image/jpeg', 'data:image/png']:
                return Response({'statusCode': '0', 'messege': 'only jpg, jpeg and png files are allowed.'}, status=400)
            decoded_pic = base64.b64decode(docstr.encode())
            ext = profile_pic_name.split('.')[-1].lower()
            if ext not in ['jpg', 'jpeg', 'png']:
                return Response({'statusCode': '0', 'messege': 'only image is allowed for profile pic.'}, status=400)
            new_path = os.path.join(os.path.dirname(user.profile_pic.path), profile_pic_name)

            if os.path.exists(user.profile_pic.path):
                os.remove(user.profile_pic.path)
            with open(new_path, 'wb') as file:
                file.write(decoded_pic)
            if ext in ['jpg', 'jpeg', 'png']:
                encoded_pic = f"data:image/{ext};base64,{docstr}"
            else:
                encoded_pic = None
            user.first_name = first_name
            user.last_name = last_name
            user.phone_no = phone_no
            user.profile_pic = new_path
            user.save()

            return Response({
                'statusCode': '1', 'messege': 'Profile Details updated successfully'
            }, status=200)
        else:
            return Response({'statusCode': '0', 'error': 'Please Provide Profile Pic'}, status=400)
    except Exception as e:
        return Response({'statusCode': '0', 'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    user_id = request.user.user_id
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')
    confirm_password = request.data.get('confirm_password')

    if not all([old_password, new_password, new_password]):
        return Response({'statusCode': '0', 'error': 'Missing required data'}, status=400)

    if not old_password:
        return Response({'statusCode': '0', 'error': 'Please enter old password'}, status=400)
    if not new_password:
        return Response({'statusCode': '0', 'error': 'Please enter new password'}, status=400)
    if not confirm_password:
        return Response({'statusCode': '0', 'error': 'Please enter confirm password'}, status=400)

    try:
        user = User.objects.get(user_id=user_id)

        if user.check_password(old_password):
            if new_password == confirm_password:
                # user.password = new_password
                user.set_password(new_password)
                user.save()
                return Response({'data': 'Password update successful.', 'statusCode': '1'},
                                status=200)
            else:
                return Response({'data': 'new password and confirm password does not match.', 'statusCode': '0'},
                                status=400)
        else:
            return Response({'data': 'Incorrect old password', 'statusCode': '0'}, status=400)

    except Exception as e:
        return Response({'statusCode': '0', 'error': str(e)}, status=500)
