import base64
from datetime import timedelta

import pandas as pd
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum
from django.http import HttpResponse
from django.utils import timezone
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from ...model.department import Document, Department, Category, SubCategory
from ...serializer.admin import ResourceSerializer, RoleSerializer, RoleResourceMappingSerializer
from ...utils.common import size_multiplier

from ...utils.decoraters import AdminOnly
from ...utils.forms import LoginForm
from ...models import User

user_dto = {}


@api_view(['POST'])
def admin_login(request):
    captcha_challenge = request.session.get('captcha')
    form = LoginForm(initial={'captcha': captcha_challenge}, data=request.data)

    if form.is_valid():
        email = form.cleaned_data.get('email')
        password = request.data.get('password')
        captcha_response = form.cleaned_data.get('captcha')

        user = User.objects.filter(email=email).first()

        if captcha_response != captcha_challenge:
            return Response({'error': 'Invalid CAPTCHA. Please try again.'}, status=400)
        if user is None:
            return Response({'error': 'Email does not exist'}, status=400)

        if user is None or not user.check_password(password):
            return Response({'error': 'Invalid email or password'}, status=400)
        if not user.is_active:
            return Response({'error': 'User is not Active'}, status=400)

        # Check if the user is authenticated and is an admin
        if user and user.is_admin:
            refresh = RefreshToken.for_user(user)  # Generate JWT refresh token
            access_token = str(refresh.access_token)  # Extract the access token

            user_data = {
                'user_id': user.user_id,
                'username': user.username,
                'email': user.email,
                # Add other fields as needed
            }

            return Response({
                'message': 'Logged in successfully',
                'user_data': user_data,
                'access_token': access_token  # Return the JWT access token
            }, status=200)
        else:
            return Response({'error': 'Invalid credentials or not an admin'}, status=401)
    else:
        # If the form is invalid, construct an error response
        errors = dict(form.errors.items())
        return Response({'error': errors}, status=400)


@api_view(['POST'])
@permission_classes([AdminOnly])
def create_role(request):
    serializer = RoleSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            'statusCode': '1',
            'data': serializer.data,
            'message': 'Role created successfully.',
        }, status=201)
    return Response({
        'statusCode': '0',
        'message': 'Role creation failed.',
    }, status=400)


@api_view(['POST'])
@permission_classes([AdminOnly])
def create_resource(request):
    serializer = ResourceSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            'statusCode': '1',
            'data': serializer.data,
            'message': 'Resource created successfully.',
        }, status=201)
    return Response({
        'statusCode': '0',
        'message': 'Resource creation failed.',
    }, status=400)


@api_view(['POST'])
@permission_classes([AdminOnly])
def create_role_resource_mapping(request):
    serializer = RoleResourceMappingSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response({
            'statusCode': '1',
            'data': serializer.data,
            'message': 'Role Resource mapped successfully.',
        }, status=201)
    return Response({
        'statusCode': '0',
        'message': 'Role-Resource mapping failed.',
    }, status=400)


@api_view(['GET'])
@permission_classes([AdminOnly])
def list_documents_admin(request):
    try:
        # Fetch all documents from the database
        documents = Document.objects.all()

        # Pagination
        paginator = Paginator(documents, 10)  # Change '10' to desired items per page
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        # List to store document information with base64 content
        documents_data = []

        for document in page_obj:
            with open(document.doc.path, 'rb') as file:
                # Encode document content in base64
                encoded_data = base64.b64encode(file.read()).decode('utf-8')

            # Determine the file type and append the appropriate prefix

            file_extension = document.doc.path.split('.')[-1].lower()
            if file_extension in ['pdf', 'ppt', 'pptx', 'doc', 'docx', 'xls', 'xlsx']:
                encoded_file = f"data:application/{file_extension};base64,{encoded_data}"
            elif file_extension in ['jpg', 'jpeg', 'png']:
                encoded_file = f"data:image/{file_extension};base64,{encoded_data}"
            else:
                encoded_file = None
            # Create a dictionary containing document information and base64 content
            doc_info = {
                'id': document.id,
                'name': document.name,
                'doc_type': document.doc_type,
                'size': document.size,
                'doc': encoded_file
            }

            documents_data.append(doc_info)

        # Return all documents with their information and base64 content
        return Response({
            'documents': documents_data,
            'current_page': page_obj.number,
            'total_pages': paginator.num_pages
        }, status=200)

    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([AdminOnly])
def admin_dashboard_counts(request):
    try:
        documents = Document.objects.all()
        departments = Department.objects.all()
        if documents is None:
            response_data = {
                "total_department": departments.count(),
                "no_of_file": '0',
                "total_size": '0 MB',
                "fileType": {
                    "ppt": {
                        'size': '0 MB', 'total': '0'
                    },
                    "pdf": {
                        'size': '0 MB', 'total': '0'
                    },
                    'image': {
                        'size': '0 MB', 'total': '0'
                    },
                    'word': {
                        'size': '0 MB', 'total': '0'
                    },
                    'excel': {
                        'size': '0 MB', 'total': '0'
                    }
                }
            }
            return Response({'statusCode': '1', 'data': response_data}, status=200)
        no_of_file = documents.count()
        total_size_bytes = sum(doc.doc.size for doc in documents)
        total_size_mb = total_size_bytes / (1024 * 1024)  # Convert bytes to MB
        size_pdf = sum(doc.doc.size for doc in documents if doc.doc.name.lower().endswith('.pdf'))
        size_ppt = sum(doc.doc.size for doc in documents if doc.doc.name.lower().endswith(('.ppt', '.pptx')))
        size_image = sum(
            doc.doc.size for doc in documents if doc.doc.name.lower().endswith(('.jpg', '.jpeg', '.png')))
        size_excel = sum(doc.doc.size for doc in documents if doc.doc.name.lower().endswith(('.xls', '.xlsx')))
        size_word = sum(doc.doc.size for doc in documents if doc.doc.name.lower().endswith(('.doc', '.docx')))
        total_pdf = documents.filter(doc__endswith='.pdf').count()
        total_ppt = documents.filter(Q(doc__endswith='.ppt') | Q(doc__endswith='.pptx')).count()
        total_images = documents.filter(
            Q(doc__endswith='.jpg') | Q(doc__endswith='.jpeg') | Q(doc__endswith='.png')).count()
        total_excel = documents.filter(Q(doc__endswith='.xls') | Q(doc__endswith='.xlsx')).count()
        total_word = documents.filter(Q(doc__endswith='.doc') | Q(doc__endswith='.docx')).count()

        response_data = {
            "total_department": departments.count(),
            "no_of_file": f"{no_of_file}",
            "total_size": f"{total_size_mb:.1f} MB",
            "fileType": {
                "ppt": {
                    'size': convert_size(size_ppt), 'total': total_ppt
                },
                "pdf": {
                    'size': convert_size(size_pdf), 'total': total_pdf
                },
                'image': {
                    'size': convert_size(size_image), 'total': total_images
                },
                'word': {
                    'size': convert_size(size_word), 'total': total_word
                },
                'excel': {
                    'size': convert_size(size_excel), 'total': total_excel
                }
            }
        }

        return Response({'statusCode': '1', 'data': response_data}, status=200)

    except Exception as e:
        return Response({'statusCode': '0', 'error': str(e)}, status=500)


def convert_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} bytes"
    elif 1024 <= size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.0f} KB"
    elif 1024 ** 2 <= size_bytes < 1024 ** 3:
        return f"{size_bytes / (1024 ** 2):.0f} MB"
    else:
        return f"{size_bytes / (1024 ** 3):.0f} GB"


def get_file(data):
    print(">>>>>>>%%%%%<<<<<<", data.doc.path)
    with open(data.doc.path, 'rb') as file:
        encoded_data = base64.b64encode(file.read()).decode('utf-8')
    file_extension = data.doc.path.split('.')[-1].lower()
    if file_extension == 'pdf':
        encoded_file = f"data:application/{file_extension};base64,{encoded_data}"
    elif file_extension == 'ppt':
        encoded_file = f"data:application/vnd.ms-powerpoint;base64,{encoded_data}"
    elif file_extension == 'pptx':
        encoded_file = f"data:application/vnd.openxmlformats-officedocument.presentationml.presentation;base64,{encoded_data}"
    elif file_extension == 'xls':
        encoded_file = f"data:application/vnd.ms-excel;base64,{encoded_data}"
    elif file_extension == 'xlsx':
        encoded_file = f"data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{encoded_data}"
    elif file_extension == 'doc':
        encoded_file = f"data:application/msword;base64,{encoded_data}"
    elif file_extension == 'docx':
        encoded_file = f"data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,{encoded_data}"
    elif file_extension in ['jpg', 'jpeg', 'png']:
        encoded_file = f"data:image/{file_extension};base64,{encoded_data}"
    else:
        encoded_file = None
    return encoded_file


@api_view(['GET'])
@permission_classes([AdminOnly])
def get_uploaded_files(request):
    try:
        departments = Department.objects.all()
        serialized_departments = []
        for department in departments:
            categories = Category.objects.filter(dep=department)
            serialized_categories = []
            total_size_bytes = 0
            for category in categories:
                documents = Document.objects.filter(cat=category)
                total_size_bytes += sum(doc.doc.size for doc in documents)
                # cat_wise_mb = total_size_bytes / (1024 * 1024)
                serialized_documents = []
                total_pdf = documents.filter(doc__endswith='.pdf').count()
                pdfs = documents.filter(doc__endswith='.pdf')
                pdf_docs = []
                for pdf in pdfs:
                    last_modified = pdf.upload_time
                    last_modified_tz = last_modified.astimezone(timezone.get_current_timezone())
                    adjusted_time = last_modified_tz + timedelta(hours=5, minutes=30)

                    size_formatted = convert_size(pdf.size)
                    encoded_file = get_file(pdf)
                    pdf_docs.append({
                        'file_name': pdf.name,
                        'size': size_formatted,
                        'file': encoded_file,
                        'uploaded_by': pdf.user.username,
                        'last_modified': adjusted_time.strftime('%d-%m-%Y %I:%M %p'),
                    })

                total_ppt = documents.filter(Q(doc__endswith='.ppt') | Q(doc__endswith='.pptx')).count()
                ppts = documents.filter(Q(doc__endswith='.ppt') | Q(doc__endswith='.pptx'))
                ppt_docs = []
                for ppt in ppts:
                    last_modified = ppt.upload_time
                    last_modified_tz = last_modified.astimezone(timezone.get_current_timezone())
                    adjusted_time = last_modified_tz + timedelta(hours=5, minutes=30)
                    size_formatted = convert_size(ppt.size)
                    encoded_file = get_file(ppt)
                    ppt_docs.append({
                        'file_name': ppt.name,
                        'size': size_formatted,
                        'file': encoded_file,
                        'uploaded_by': ppt.user.username,
                        'last_modified': adjusted_time.strftime('%d-%m-%Y %I:%M %p'),
                    })
                total_images = documents.filter(
                    Q(doc__endswith='.jpg') | Q(doc__endswith='.jpeg') | Q(doc__endswith='.png')).count()
                images = documents.filter(Q(doc__endswith='.jpg') | Q(doc__endswith='.jpeg') | Q(doc__endswith='.png'))
                image_docs = []
                for image in images:
                    last_modified = image.upload_time
                    last_modified_tz = last_modified.astimezone(timezone.get_current_timezone())
                    adjusted_time = last_modified_tz + timedelta(hours=5, minutes=30)
                    size_formatted = convert_size(image.size)
                    encoded_file = get_file(image)
                    image_docs.append({
                        'file_name': image.name,
                        'size': size_formatted,
                        'file': encoded_file,
                        'uploaded_by': image.user.username,
                        'last_modified': adjusted_time.strftime('%d-%m-%Y %I:%M %p'),
                    })
                total_excel = documents.filter(Q(doc__endswith='.xls') | Q(doc__endswith='.xlsx')).count()
                excels = documents.filter(Q(doc__endswith='.xls') | Q(doc__endswith='.xlsx'))
                excel_docs = []
                for excel in excels:
                    last_modified = excel.upload_time
                    last_modified_tz = last_modified.astimezone(timezone.get_current_timezone())
                    adjusted_time = last_modified_tz + timedelta(hours=5, minutes=30)

                    size_formatted = convert_size(excel.size)
                    encoded_file = get_file(excel)
                    excel_docs.append({
                        'file_name': excel.name,
                        'size': size_formatted,
                        'file': encoded_file,
                        'uploaded_by': excel.user.username,
                        'last_modified': adjusted_time.strftime('%d-%m-%Y %I:%M %p'),
                    })
                total_word = documents.filter(Q(doc__endswith='.doc') | Q(doc__endswith='.docx')).count()
                words = documents.filter(Q(doc__endswith='.doc') | Q(doc__endswith='.docx'))
                word_docs = []
                for word in words:
                    last_modified = word.upload_time
                    last_modified_tz = last_modified.astimezone(timezone.get_current_timezone())
                    adjusted_time = last_modified_tz + timedelta(hours=5, minutes=30)

                    size_formatted = convert_size(word.size)
                    encoded_file = get_file(word)
                    word_docs.append({
                        'file_name': word.name,
                        'size': size_formatted,
                        'file': encoded_file,
                        'uploaded_by': word.user.username,
                        'last_modified': adjusted_time.strftime('%d-%m-%Y %I:%M %p'),
                    })

                serialized_documents.append({
                    "fileType": {
                        "ppt": {
                            'total': total_ppt,
                            'files': ppt_docs
                        },
                        "pdf": {
                            'total': total_pdf,
                            'files': pdf_docs
                        },
                        'image': {
                            'total': total_images,
                            'files': image_docs
                        },
                        'word': {
                            'total': total_word,
                            'files': word_docs
                        },
                        'excel': {
                            'total': total_excel,
                            'files': excel_docs
                        }
                    }
                })
                serialized_categories.append({
                    'category_id': category.id,
                    'category_name': category.cat_name,
                    'total_file': documents.count(),
                    'document': serialized_documents
                    # Add other category details here if needed
                })
            total_size_mb = total_size_bytes / (1024 * 1024)
            serialized_departments.append({
                'department_name': department.dep_name,
                'categories': serialized_categories,
                'total_size': f"{total_size_mb:.0f} MB",
            })
        return Response({'statusCode': '1', 'data': serialized_departments}, status=200)
    except Exception as e:
        return Response({'statusCode': '0', 'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([AdminOnly])
def get_active_users(request):
    try:
        # Calculate the time threshold (10 or 20 minutes ago)
        threshold = timezone.now() - timezone.timedelta(minutes=10)

        active_users = get_user_model().objects.filter(last_activity_time__gte=threshold)

        response_data = []
        profile_pic = ''
        # You can then use the active_users queryset for further processing or iteration
        for user in active_users:
            print(user.username)
            last_login_time = user.last_activity_time
            last_login_time_tz = last_login_time.astimezone(timezone.get_current_timezone())
            adjusted_time = last_login_time_tz + timedelta(hours=5, minutes=30)
            with open(user.profile_pic.path, 'rb') as file:
                encoded_pic = base64.b64encode(file.read()).decode('utf-8')
            ext = user.profile_pic.path.split('.')[-1].lower()
            if ext in ['jpg', 'jpeg', 'png']:
                profile_pic = f"data:image/{ext};base64,{encoded_pic}"

            user_info = {
                "user_name": user.username,
                "login_time": adjusted_time.strftime('%d-%m-%Y %I:%M %p'),
                "profile_pic": profile_pic
            }
            response_data.append(user_info)

        return Response({'statusCode': '1', 'data': response_data}, status=200)
    except Exception as e:
        return Response({'statusCode': '0', 'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([AdminOnly])
def get_all_department_file_storage_report(request):
    try:
        no_of_entries = int(request.data.get('no_of_entries', 10))
        page_no = int(request.data.get('page_no', 1))
        search_query = request.data.get('search_query', None)
        dep_id = request.data.get('dep_id')
        cat_id = request.data.get('cat_id')
        file_type = request.data.get('file_type')
        sort_by = request.data.get('sort_by', 'total_size')  # Default sorting by total_size
        sort_order = request.data.get('sort_order', 'asc')  # Default sorting order is ascending

        file_types = ['pdf', 'ppt', 'image', 'word', 'excel']
        result = []

        departments = Department.objects.all()
        if dep_id:
            departments = departments.filter(pk=dep_id)

        for department in departments:
            categories = Category.objects.filter(dep=department)
            if cat_id:
                categories = categories.filter(pk=cat_id)

            for category in categories:
                documents = Document.objects.filter(cat=category)

                if file_type:
                    documents = documents.filter(doc_type=file_type)

                if search_query:
                    documents = documents.filter(
                        Q(dep_name__icontains=search_query) |
                        Q(cat_name__icontains=search_query) |
                        Q(doc_type__icontains=search_query)
                    )

                file_info = documents.values(
                    'doc_type',
                ).annotate(
                    total_size=Sum('size'),
                    total_count=Count('id')
                )

                for d in file_info:
                    total_size = convert_size(d['total_size'])
                    result.append({
                        'dep_name': department.dep_name,
                        'cat_name': category.cat_name,
                        'file_type': d['doc_type'],
                        'total_size': total_size,
                        'total_count': d['total_count'] or 0,
                    })

        # Sorting the result
        if sort_by == 'total_size':
            result = sorted(result, key=lambda x: (
                float(x['total_size'].split()[0]) * size_multiplier(x['total_size'].split()[1]),  # Convert to bytes
            ), reverse=sort_order.lower() == 'desc')
        elif sort_by == 'total_count':
            result = sorted(result, key=lambda x: x['total_count'], reverse=sort_order.lower() == 'desc')

        paginator = Paginator(result, no_of_entries)
        page_result = paginator.get_page(page_no)

        return Response({'statusCode': '1', 'documents': page_result.object_list, 'total_pages': paginator.num_pages,
                         'current_page': page_result.number, 'total_entries': paginator.count},
                        status=200)

    except Exception as e:
        return Response({'statusCode': '0', 'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([AdminOnly])  # Add the necessary permission classes
def download_all_excel_report(request):
    try:
        no_of_entries = int(request.data.get('no_of_entries', 10))
        page_no = int(request.data.get('page_no', 1))
        search_query = request.data.get('search_query', None)
        dep_id = request.data.get('dep_id')
        cat_id = request.data.get('cat_id')
        file_type = request.data.get('file_type')
        sort_by = request.data.get('sort_by', 'total_size')  # Default sorting by total_size
        sort_order = request.data.get('sort_order', 'asc')  # Default sorting order is ascending

        file_types = ['pdf', 'ppt', 'image', 'word', 'excel']
        result = []

        departments = Department.objects.all()
        if dep_id:
            departments = departments.filter(pk=dep_id)

        for department in departments:
            categories = Category.objects.filter(dep=department)
            if cat_id:
                categories = categories.filter(pk=cat_id)

            for category in categories:
                documents = Document.objects.filter(cat=category)

                if file_type:
                    documents = documents.filter(doc_type=file_type)

                if search_query:
                    documents = documents.filter(
                        Q(dep_name__icontains=search_query) |
                        Q(cat_name__icontains=search_query) |
                        Q(doc_type__icontains=search_query)
                    )

                file_info = documents.values(
                    'doc_type',
                ).annotate(
                    total_size=Sum('size'),
                    total_count=Count('id')
                )

                for d in file_info:
                    total_size = convert_size(d['total_size'])
                    result.append({
                        'dep_name': department.dep_name,
                        'cat_name': category.cat_name,
                        'file_type': d['doc_type'],
                        'total_size': total_size,
                        'total_count': d['total_count'] or 0,
                    })

        # Sorting the result
        if sort_by == 'total_size':
            result = sorted(result, key=lambda x: (
                float(x['total_size'].split()[0]) * size_multiplier(x['total_size'].split()[1]),  # Convert to bytes
            ), reverse=sort_order.lower() == 'desc')
        elif sort_by == 'total_count':
            result = sorted(result, key=lambda x: x['total_count'], reverse=sort_order.lower() == 'desc')

        paginator = Paginator(result, no_of_entries)
        page_result = paginator.get_page(page_no)

        # Convert the entire result to a DataFrame
        df = pd.DataFrame(result, columns=['dep_name', 'cat_name', 'file_type', 'total_size', 'total_count'])
        df = df.rename(columns={
            'dep_name': 'Department Name',
            'cat_name': 'Category Name',
            'file_type': 'File Type',
            'total_size': 'Total Size',
            'total_count': 'Total Count',
        })

        # Create a response with an Excel file
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename=department_file_storage_report.xlsx'

        # Create an Excel workbook
        book = Workbook()

        # Convert the DataFrame to rows and write to the Excel sheet
        sheet = book.active
        for row in dataframe_to_rows(df, index=False, header=True):
            sheet.append(row)

        # Auto-size columns
        for column in sheet.columns:
            max_length = 0
            column = [cell for cell in column]
            try:
                max_length = max(len(str(cell.value)) for cell in column)
            except ValueError:
                pass
            adjusted_width = (max_length + 2)
            sheet.column_dimensions[column[0].column_letter].width = adjusted_width

        # Save the workbook and finalize the response
        book.save(response)
        return response

    except Exception as e:
        return Response({'statusCode': '0', 'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([AdminOnly])
def get_departments(request):
    response_data = []
    try:
        departments = Department.objects.all()
        for department in departments:
            categories = Category.objects.filter(dep=department)
            total_size_bytes = 0
            for category in categories:
                documents = Document.objects.filter(cat=category)
                total_size_bytes += sum(doc.doc.size for doc in documents)
            total_size_mb = total_size_bytes / (1024 * 1024)
            response_data.append({
                'dep_id': department.id,
                'total_size': f"{total_size_mb:.2f} MB",
                'dep_name': department.dep_name
            })
        return Response({'statusCode': '1', 'data': response_data, }, status=200)

    except Exception as e:
        return Response({'statusCode': '0', 'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([AdminOnly])
def get_categories(request, dep_id):
    # dep_id = request.data.get('dep_id')
    response_data = []
    try:
        categories = Category.objects.filter(dep__in=dep_id)

        # print(sub_category)
        print(SubCategory.objects.filter(cat__in=categories))
        for category in categories:
            sub_category = SubCategory.objects.filter(cat
                                                      =category).count()
            response_data.append({
                'cat_id': category.id,
                'total_sub_cat': sub_category,
                'cat_name': category.cat_name
            })
        return Response({'statusCode': '1', 'data': response_data, }, status=200)

    except Exception as e:
        return Response({'statusCode': '0', 'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([AdminOnly])
def get_sub_categories(request, cat_id):
    # dep_id = request.data.get('dep_id')
    response_data = []
    try:
        sub_categories = SubCategory.objects.filter(cat=cat_id)
        print(sub_categories)
        for category in sub_categories:
            documents = Document.objects.filter(sub_cat=category)
            total_pdf = documents.filter(doc__endswith='.pdf').count()
            total_ppt = documents.filter(Q(doc__endswith='.ppt') | Q(doc__endswith='.pptx')).count()
            total_images = documents.filter(
                Q(doc__endswith='.jpg') | Q(doc__endswith='.jpeg') | Q(doc__endswith='.png')).count()
            total_excel = documents.filter(Q(doc__endswith='.xls') | Q(doc__endswith='.xlsx')).count()
            total_word = documents.filter(Q(doc__endswith='.doc') | Q(doc__endswith='.docx')).count()

            response_data.append({
                'sub_cat_id': category.id,
                'sub_cat_name': category.sub_cat_name,
                'total_file': documents.count(),
                'files': [
                    {'type': 'PDF', 'total': total_pdf},
                    {'type': 'PPT', 'total': total_ppt},
                    {'type': 'IMAGES', 'total': total_images},
                    {'type': 'EXCEL', 'total': total_excel},
                    {'type': 'WORD', 'total': total_word},
                ]
            })
        return Response({'statusCode': '1', 'data': response_data, }, status=200)

    except Exception as e:
        return Response({'statusCode': '0', 'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([AdminOnly])
def get_all_documents(request):
    response_data = []
    docs = []
    no_of_entries = int(request.data.get('no_of_entries', 10))
    page_no = int(request.data.get('page_no', 1))
    search_query = request.data.get('search_query', None)
    sub_cat_id = request.data.get('sub_cat_id')
    filetype = request.data.get('file_type')
    sort_by = request.data.get('sort_by', 'total_size')  # Default sorting by total_size
    sort_order = request.data.get('sort_order', 'asc')  # Default sorting order is ascending

    try:
        documents = Document.objects.filter(sub_cat=sub_cat_id)
        docs = Document.objects.none()
        if filetype.upper() == 'PDF':
            docs = documents.filter(doc__endswith='.pdf')
        elif filetype.upper() == 'PPT':
            docs = documents.filter(Q(doc__endswith='.ppt') | Q(doc__endswith='.pptx'))
        elif filetype.upper() == 'IMAGES':
            docs = documents.filter(Q(doc__endswith='.jpg') | Q(doc__endswith='.jpeg') | Q(doc__endswith='.png'))
        elif filetype.upper() == 'EXCEL':
            docs = documents.filter(Q(doc__endswith='.xls') | Q(doc__endswith='.xlsx'))
            # for excel in docs:
            #     last_modified = excel.upload_time
            #     last_modified_tz = last_modified.astimezone(timezone.get_current_timezone())
            #     adjusted_time = last_modified_tz + timedelta(hours=5, minutes=30)
            #
            #     size_formatted = convert_size(excel.size)
            #     encoded_file = get_file(excel)
            #     response_data.append({
            #         'file_name': excel.name,
            #         'size': size_formatted,
            #         'file': encoded_file,
            #         'uploaded_by': excel.user.username,
            #         'last_modified': adjusted_time.strftime('%d-%m-%Y %I:%M %p'),
            #     })
        elif filetype.upper() == 'WORD':
            docs = documents.filter(Q(doc__endswith='.doc') | Q(doc__endswith='.docx'))

        if search_query:
            docs = docs.filter(
                Q(user__username__icontains=search_query) |
                Q(name__icontains=search_query) |
                Q(upload_time__icontains=search_query) |
                Q(id__icontains=search_query)
            )

        # Apply sorting
        sort_by = request.data.get('sort_by', 'user__username')  # Default sorting by 'dep_name'
        if sort_by == 'username':
            sort_by = 'user__username'
        if sort_by == 'last_modified':
            sort_by = 'upload_time'
        if sort_by not in ['user__username', 'name', 'id', 'upload_time']:
            sort_by = 'user__username'  # If invalid sort field provided, default to 'dep_name'

        sort_order = request.data.get('sort_order', 'asc')  # Default sorting order is ascending
        if sort_order.lower() not in ['asc', 'desc']:
            sort_order = 'asc'  # If invalid sort order provided, default to ascending

        if sort_order.lower() == 'asc':
            docs = docs.order_by(sort_by)
        else:
            docs = docs.order_by(
                f'-{sort_by}')  # Minus sign for descending order
        # Apply pagination
        page_size = int(request.data.get('no_of_entries', 10))  # Default page size is 10
        paginator = Paginator(docs, page_size)
        page_number = request.data.get('page_no', 1)
        page_obj = paginator.get_page(page_number)
        for data in page_obj:
            # .object_list.values('name', 'upload_time', 'doc', 'user__username', 'id', 'size')
            size_formatted = convert_size(data.size)
            encoded_file = get_file(data)
            last_modified = data.upload_time
            last_modified_tz = last_modified.astimezone(timezone.get_current_timezone())
            adjusted_time = last_modified_tz + timedelta(hours=5, minutes=30)

            response_data.append({
                'file_name': data.name,
                'size': size_formatted,
                'file': encoded_file,
                'uploaded_by': data.user.username,
                'last_modified': adjusted_time.strftime('%d-%m-%Y %I:%M %p'),
            })
        return Response({'statusCode': '1', 'data': response_data, 'current_page': page_obj.number,
                         'total_pages': paginator.num_pages, 'total_entries': docs.count()}, status=200)

    except Exception as e:
        return Response({'statusCode': '0', 'error': str(e)}, status=500)
