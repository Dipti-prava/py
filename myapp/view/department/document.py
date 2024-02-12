import base64
import os

from django.core.files.base import ContentFile
from django.core.paginator import Paginator
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from ...model.department import Department, SubCategory, Category, Document
from ...serializer.department import DocumentSerializer
from ...utils.common import get_allowed_extension, get_file_extension, convert_size
from ...utils.decoraters import IsAuthenticated


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_document(request):
    doc_category = request.data.get('category')
    sub_cat_id = request.data.get('sub_category')
    doc_type = request.data.get('fileType')
    document_name = request.data.get('name')
    doc_data = request.data.get('doc')
    allowed_extensions = get_allowed_extension(doc_type.lower())

    if not doc_category:
        return Response({'statusCode': '0', 'error': 'Please provide category'}, status=400)
    if not doc_type:
        return Response({'statusCode': '0', 'error': 'Please provide file type'}, status=400)
    if not document_name:
        return Response({'statusCode': '0', 'error': 'Please provide file name'}, status=400)
    if not doc_data:
        return Response({'statusCode': '0', 'error': 'Please provide file'}, status=400)
    if not sub_cat_id:
        return Response({'statusCode': '0', 'error': 'Please provide sub category'}, status=400)

    if not all([doc_category, doc_type, document_name, doc_data, sub_cat_id]):
        return Response({'statusCode': '0', 'error': 'Missing required data'}, status=400)

    user_id = request.user.user_id
    departments_mapped_userid = Department.objects.filter(user_id=user_id, user=request.user)
    categories_mapped_userid = Category.objects.filter(dep__in=departments_mapped_userid)
    category_details = categories_mapped_userid.values_list('id', flat=True)
    is_cat_exists = int(doc_category) in category_details
    print(is_cat_exists)
    if not is_cat_exists:
        return Response({'statusCode': '0', 'error': 'invalid category id'}, status=400)

    category = categories_mapped_userid.get(pk=doc_category)
    sub_categories = SubCategory.objects.filter(cat=category)
    is_sub_cat_exists = sub_categories.filter(pk=sub_cat_id).exists()
    print(is_sub_cat_exists)
    if not is_sub_cat_exists:
        return Response({'statusCode': '0', 'error': 'invalid sub category id'}, status=400)

    try:

        format, docstr = doc_data.split(';base64,')  # Extract format and data
        extension = get_file_extension(format)
        if extension not in allowed_extensions:
            return Response({'statusCode': '0', 'message': 'Please upload a valid ' + doc_type + ' file'}, status=400)

        image_data = base64.b64decode(docstr)
        size = len(image_data)
        size_mb = size / (1024 * 1024)
        if size_mb > 25:
            return Response({'statusCode': '0', 'messege': 'file size must be less than 25 MB'}, status=400)
        document_name = document_name + '.' + extension
        document = ContentFile(image_data, name=document_name)

        # Save document details in the database
        document_object = Document.objects.create(
            user_id=request.user.user_id,
            name=document_name,
            cat_id=doc_category,
            sub_cat_id=sub_cat_id,
            doc_type=doc_type.lower(),
            size=size,
            doc=document  # Save the ContentFile in the 'doc' field of Document model
        )

        serializer = DocumentSerializer(document_object)
        return Response({'statusCode': '1', 'message': 'Document Uploaded Successfully'}, status=201)

    except Exception as e:
        return Response({'statusCode': '0', 'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def list_documents(request):
    try:
        user_id = request.user.user_id
        documents = Document.objects.filter(user_id=user_id, user=request.user)

        if documents is None:
            return Response({'statusCode': '1', 'messege': 'No document found'}, status=200)

        no_of_entries = request.data.get('no_of_entries')
        if not no_of_entries:
            return Response({'statusCode': '0', 'message': 'Please specify "no_of_entries"'}, status=400)
        page_no = request.data.get('page_no')

        # Search functionality across multiple fields
        search_query = request.data.get('search_query', None)
        if search_query:
            documents = documents.filter(
                Q(name__icontains=search_query) |
                Q(cat__cat_name__icontains=search_query) |
                Q(doc_type__icontains=search_query)
            )

        # Sorting functionality
        sort_by = request.data.get('sort_by', 'name')  # Default sorting by 'name'
        if sort_by == 'category':
            sort_by = 'cat__cat_name'
        if sort_by not in ['name', 'cat__cat_name', 'size', 'doc_type']:
            sort_by = 'name'  # If invalid sort field provided, default to 'name'

        sort_order = request.data.get('sort_order', 'asc')  # Default sorting order is ascending
        if sort_order.lower() not in ['asc', 'desc']:
            sort_order = 'asc'  # If invalid sort order provided, default to ascending

        if sort_order.lower() == 'asc':
            documents = documents.order_by(sort_by)
        else:
            documents = documents.order_by(f'-{sort_by}')  # Minus sign for descending order

        # Get the page size from the frontend request or set a default value
        page_size = int(request.data.get('no_of_entries', 5))  # Default page size is 10

        # Pagination
        paginator = Paginator(documents, page_size)  # Change '10' to desired items per page
        page_number = request.data.get('page_no', 1)
        page_obj = paginator.get_page(page_number)
        # List to store document information with base64 content
        documents_data = []
        count = 0
        for document in page_obj:
            with open(document.doc.path, 'rb') as file:
                # Encode document content in base64
                encoded_data = base64.b64encode(file.read()).decode('utf-8')

            # Determine the file type and append the appropriate prefix

            file_extension = document.doc.path.split('.')[-1].lower()
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
            size_formatted = convert_size(document.size)

            category = Category.objects.get(pk=document.cat_id)
            sub_category = SubCategory.objects.get(pk=document.sub_cat_id)

            # Create a dictionary containing document information and base64 content
            doc_info = {
                'id': document.id,
                'name': document.name,
                'category': category.cat_name,
                'sub_category': sub_category.sub_cat_name,
                'doc_type': document.doc_type,
                'size': size_formatted,
                'doc': encoded_file
            }

            documents_data.append(doc_info)
            count = count + 1

        # Return all documents with their information and base64 content
        return Response({'statusCode': '1', 'documents': documents_data, 'current_page': page_obj.number,
                         'total_pages': paginator.num_pages, 'total_entries': documents.count()}, status=200)

    except Exception as e:
        return Response({'statusCode': '0', 'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_counts_document(request):
    try:
        user_id = request.user.user_id
        documents = Document.objects.filter(user_id=user_id, user=request.user)

        if documents is None:
            response_data = {
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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_document_by_id(request):
    try:
        user_id = request.user.user_id
        documents = Document.objects.filter(user_id=user_id, user=request.user)

        if documents is None:
            return Response({'messege': 'No document found'}, status=200)

        # List to store document information with base64 content
        documents_data = []
        for document in documents:
            with open(document.doc.path, 'rb') as file:
                # Encode document content in base64
                encoded_data = base64.b64encode(file.read()).decode('utf-8')
                # Determine the file type and append the appropriate prefix

                file_extension = document.doc.path.split('.')[-1].lower()
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
                size_formatted = convert_size(document.size)
                # Create a dictionary containing document information and base64 content
                doc_info = {
                    'id': document.id,
                    'name': document.name,
                    'doc_type': document.doc_type,
                    'size': size_formatted,
                    'doc': encoded_file
                }

                documents_data.append(doc_info)

        # Return all documents with their information and base64 content
        return Response({'statusCode': '1', 'documents': documents_data}, status=200)

    except Exception as e:
        return Response({'statusCode': '0', 'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_documentby_doc_id(request):
    doc_id = request.data.get('doc_id')  # Use GET to retrieve the doc_id parameter
    try:
        document = Document.objects.get(pk=doc_id, user=request.user)
    except Document.DoesNotExist:
        return Response({'statusCode': '0', 'error': 'Document not found'}, status=404)

    try:
        with open(document.doc.path, 'rb') as file:
            # Encode document content in base64
            encoded_data = base64.b64encode(file.read()).decode('utf-8')

        file_extension = document.doc.path.split('.')[-1].lower()
        print("file_Ext", file_extension)
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
        size_formatted = convert_size(document.size)
        doc_info = {
            'id': document.id,
            'name': document.name,
            'doc_type': document.doc_type,
            'size': size_formatted,
            'doc': encoded_file
        }

        return Response({'statusCode': '1', 'data': doc_info}, status=200)
    except Exception as e:
        return Response({'statusCode': '0', 'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def update_document(request):
    # doc_id, doc
    doc_id = request.data.get('doc_id')
    category = request.data.get('category')
    doc_name = request.data.get('name')
    doc = request.data.get('doc')

    if not doc_name:
        return Response({'statusCode': '0', 'error': 'Please provide file name'}, status=400)
    if not doc:
        return Response({'statusCode': '0', 'error': 'Please provide file'}, status=400)

    if not all([doc_name, doc]):
        return Response({'statusCode': '0', 'error': 'Missing required data'}, status=400)

    try:
        document = Document.objects.get(pk=doc_id, user=request.user)
    except Document.DoesNotExist:
        return Response({'statusCode': '0', 'error': 'Document not found'}, status=404)

    try:
        if doc:
            format, docstr = doc.split(';base64,')
            decoded_doc = base64.b64decode(docstr.encode())

            file_extension = document.doc.path.split('.')[-1].lower()

            new_filename = f'{doc_name}.{file_extension}'
            new_path = os.path.join(os.path.dirname(document.doc.path), doc_name)

            if os.path.exists(document.doc.path):
                os.remove(document.doc.path)

            with open(new_path, 'wb') as file:
                file.write(decoded_doc)

            if file_extension == 'pdf':
                encoded_file = f"data:application/{file_extension};base64,{docstr}"
            elif file_extension == 'ppt':
                encoded_file = f"data:application/vnd.ms-powerpoint;base64,{docstr}"
            elif file_extension == 'pptx':
                encoded_file = f"data:application/vnd.openxmlformats-officedocument.presentationml.presentation;base64,{docstr}"
            elif file_extension == 'xls':
                encoded_file = f"data:application/vnd.ms-excel;base64,{docstr}"
            elif file_extension == 'xlsx':
                encoded_file = f"data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{docstr}"
            elif file_extension == 'doc':
                encoded_file = f"data:application/msword;base64,{docstr}"
            elif file_extension == 'docx':
                encoded_file = f"data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,{docstr}"
            elif file_extension in ['jpg', 'jpeg', 'png']:
                encoded_file = f"data:image/{file_extension};base64,{docstr}"
            else:
                encoded_file = None

            # Update document metadata
            document.doc_type = file_extension
            document.name = doc_name
            document.category = category
            document.doc = new_path
            document.size = len(decoded_doc) / (1024 * 1024)  # Size in MB
            document.save()

            doc_info = {
                'id': document.id,
                'name': document.name,
                'doc_type': document.doc_type,
                'size': document.size,
                'doc': encoded_file
            }
            return Response({'statusCode': '1', 'data': doc_info, 'message': 'Document updated successfully'},
                            status=200)
        else:
            return Response({'statusCode': '0', 'error': 'No document data provided for update'}, status=400)
    except Exception as e:
        return Response({'statusCode': '0', 'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_document(request):
    doc_id = request.data.get('doc_id')
    if not doc_id or not isinstance(doc_id, int):
        return Response({'statusCode': '0', 'error': 'Invalid or empty doc_id'}, status=400)

    try:
        document_exists = Document.objects.filter(pk=doc_id, user=request.user).exists()

        if not document_exists:
            return Response(
                {"statusCode": 0, "message": "Document with id " + format(doc_id) + " does not exist"}, status=400)

        document = Document.objects.get(pk=doc_id, user=request.user)
        # Get the path of the document file
        document_path = document.doc.path
        document.delete()

        # Check if the file exists and delete it from the storage folder
        if os.path.exists(document_path):
            os.remove(document_path)

        return Response({'statusCode': '1', 'message': 'Document deleted successfully'}, status=200)
    except Document.DoesNotExist:
        return Response({'statusCode': '0', 'error': 'Document not found'}, status=400)

    except Exception as e:
        return Response({'statusCode': '0', 'error': str(e)}, status=500)
