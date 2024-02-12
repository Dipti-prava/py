from django.core.paginator import Paginator
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from ...model.department import Department, Category, SubCategory
from ...serializer.department import CategorySerializer, SubCategorySerializer
from ...utils.decoraters import IsAuthenticated


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_category(request):
    serializer_data = request.data.copy()
    try:
        dep_id = request.data.get('dep_id')
        cat_name = request.data.get('cat_name')

        if not dep_id:
            return Response({'statusCode': '0', 'error': 'Please provide document type'}, status=400)
        if not cat_name:
            return Response({'statusCode': '0', 'error': 'Please provide category name'}, status=400)

        if not all([dep_id, cat_name]):
            return Response({'statusCode': '0', 'error': 'Missing required data'}, status=400)
        user_id = request.user.user_id
        departments = Department.objects.filter(user_id=user_id, user=request.user).values_list('id', flat=True)
        is_avail = int(dep_id) in departments
        print(is_avail)
        if not is_avail:
            return Response({'statusCode': '0', 'error': 'invalid department id'}, status=400)

        serializer_data['dep'] = dep_id
        serializer_data['status'] = True
        serializer = CategorySerializer(data=serializer_data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'statusCode': '1',
                'data': serializer.data,
                'message': 'New Category added successfully.',
            }, status=200)
        return Response({
            'statusCode': '0',
            'message': 'failed.',
        }, status=400)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_sub_category(request):
    serializer_data = request.data.copy()
    try:
        cat_id = request.data.get('cat_id')
        sub_cat_name = request.data.get('sub_cat_name')

        if not cat_id:
            return Response({'statusCode': '0', 'error': 'Please provide department id'}, status=400)
        if not sub_cat_name:
            return Response({'statusCode': '0', 'error': 'Please provide category name'}, status=400)

        if not all([cat_id, sub_cat_name]):
            return Response({'statusCode': '0', 'error': 'Missing required data'}, status=400)
        user_id = request.user.user_id
        departments = Department.objects.filter(user_id=user_id, user=request.user)
        categories = Category.objects.filter(dep__in=departments).values_list('id', flat=True)
        print("all cattt", categories)
        is_avail = int(cat_id) in categories
        print(is_avail)
        if not is_avail:
            return Response({'statusCode': '0', 'error': 'invalid category id'}, status=400)

        serializer_data['cat'] = cat_id
        serializer_data['status'] = True
        serializer = SubCategorySerializer(data=serializer_data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'statusCode': '1',
                # 'data': serializer.data,
                'message': 'New Sub Category added successfully.',
            }, status=200)
        return Response({
            'statusCode': '0',
            'message': 'failed.',
        }, status=400)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_sub_category(request):
    cat_id = request.data.get('cat_id')
    sub_cat_id = request.data.get('sub_cat_id')
    sub_cat_name = request.data.get('sub_cat_name')

    if not cat_id:
        return Response({'statusCode': '0', 'error': 'Please provide category'}, status=400)
    if not sub_cat_id:
        return Response({'statusCode': '0', 'error': 'Please provide sub category id'}, status=400)
    if not sub_cat_name:
        return Response({'statusCode': '0', 'error': 'Please provide sub category name'}, status=400)

    subcategory = SubCategory.objects.get(pk=sub_cat_id)

    if not all([cat_id, sub_cat_id, sub_cat_name]):
        return Response({'statusCode': '0', 'error': 'Missing required data'}, status=400)
    try:
        if subcategory:
            subcategory.cat_id = cat_id
            subcategory.sub_cat_name = sub_cat_name
            subcategory.save()

            return Response({
                'statusCode': '1',
                'message': 'Sub Category updated successfully.',
            }, status=200)
        return Response({
            'statusCode': '0',
            'message': 'failed.',
        }, status=400)
    except Exception as e:
        return Response({'statusCode': '0', 'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_sub_category(request):
    sub_cat_id = request.data.get('sub_cat_id')
    if not sub_cat_id or not isinstance(sub_cat_id, int):
        return Response({'statusCode': '0', 'error': 'Invalid or empty cat_id'}, status=400)

    try:
        sub_category_exists = SubCategory.objects.filter(pk=sub_cat_id).exists()

        if not sub_category_exists:
            return Response(
                {"statusCode": 0, "message": "Sub Category with id " + format(sub_cat_id) + " does not exist"},
                status=400)

        subcategory = SubCategory.objects.get(pk=sub_cat_id)
        subcategory.delete()

        return Response({'statusCode': '1', 'message': 'Sub Category deleted successfully'}, status=200)
    except SubCategory.DoesNotExist:
        return Response({'statusCode': '0', 'error': 'Sub Category not found'}, status=400)

    except Exception as e:
        return Response({'statusCode': '0', 'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_category(request):
    dep_id = request.data.get('dep_id')
    cat_id = request.data.get('cat_id')
    cat_name = request.data.get('cat_name')

    if not dep_id:
        return Response({'statusCode': '0', 'error': 'Please provide department'}, status=400)
    if not cat_id:
        return Response({'statusCode': '0', 'error': 'Please provide category id'}, status=400)
    if not cat_name:
        return Response({'statusCode': '0', 'error': 'Please provide category name'}, status=400)

    category = Category.objects.get(pk=cat_id)

    if not all([dep_id, cat_id, cat_name]):
        return Response({'statusCode': '0', 'error': 'Missing required data'}, status=400)
    try:
        if category:
            category.dep_id = dep_id
            category.cat_name = cat_name
            category.save()

            return Response({
                'statusCode': '1',
                'message': 'Category updated successfully.',
            }, status=200)
        return Response({
            'statusCode': '0',
            'message': 'failed.',
        }, status=400)
    except Exception as e:
        return Response({'statusCode': '0', 'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_category(request):
    cat_id = request.data.get('cat_id')
    if not cat_id or not isinstance(cat_id, int):
        return Response({'statusCode': '0', 'error': 'Invalid or empty cat_id'}, status=400)

    try:
        category_exists = Category.objects.filter(pk=cat_id).exists()

        if not category_exists:
            return Response(
                {"statusCode": 0, "message": "Category with id " + format(cat_id) + " does not exist"}, status=400)

        category = Category.objects.get(pk=cat_id)
        category.delete()

        return Response({'statusCode': '1', 'message': 'Category deleted successfully'}, status=200)
    except Category.DoesNotExist:
        return Response({'statusCode': '0', 'error': 'Category not found'}, status=400)

    except Exception as e:
        return Response({'statusCode': '0', 'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_category(request):
    try:
        user_id = request.user.user_id
        departments_mapped_userid = Department.objects.filter(user_id=user_id, user=request.user)
        categories_mapped_userid = Category.objects.filter(dep__in=departments_mapped_userid)

        # Apply search
        search_query = request.data.get('search_query', '')
        if search_query:
            categories_mapped_userid = categories_mapped_userid.filter(
                Q(dep__dep_name__icontains=search_query) |
                Q(cat_name__icontains=search_query) |
                Q(id__icontains=search_query) |
                Q(status__icontains=search_query)
            )

        # Apply sorting
        sort_by = request.data.get('sort_by', 'dep__dep_name')  # Default sorting by 'dep_name'
        if sort_by == 'dep_name':
            sort_by = 'dep__dep_name'
        if sort_by not in ['dep__dep_name', 'cat_name', 'id', 'status']:
            sort_by = 'dep__dep_name'  # If invalid sort field provided, default to 'dep_name'

        sort_order = request.data.get('sort_order', 'asc')  # Default sorting order is ascending
        if sort_order.lower() not in ['asc', 'desc']:
            sort_order = 'asc'  # If invalid sort order provided, default to ascending

        if sort_order.lower() == 'asc':
            categories_mapped_userid = categories_mapped_userid.order_by(sort_by)
        else:
            categories_mapped_userid = categories_mapped_userid.order_by(
                f'-{sort_by}')  # Minus sign for descending order

        # Apply pagination
        page_size = int(request.data.get('no_of_entries', 10))  # Default page size is 10
        paginator = Paginator(categories_mapped_userid, page_size)
        page_number = request.data.get('page_no', 1)
        page_obj = paginator.get_page(page_number)

        # Construct response data
        response_data = []
        for data in page_obj.object_list.values('dep__dep_name', 'dep__id', 'cat_name', 'id', 'status'):
            info = {
                "dep_name": data['dep__dep_name'],
                "dep_id": data['dep__id'],
                "cat_name": data['cat_name'],
                "id": data['id'],
                "status": data['status']
            }
            response_data.append(info)

        return Response({
            "data": response_data,
            "current_page": page_obj.number,
            "total_pages": paginator.num_pages,
            "total_entries": paginator.count,
            "statusCode": "1"
        }, status=200)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_sub_category(request):
    try:
        user_id = request.user.user_id
        departments_mapped_userid = Department.objects.filter(user_id=user_id, user=request.user)
        categories_mapped_userid = Category.objects.filter(dep__in=departments_mapped_userid)
        sub_categories = SubCategory.objects.filter(cat__in=categories_mapped_userid)

        # Apply search
        search_query = request.data.get('search_query', '')
        if search_query:
            sub_categories = sub_categories.filter(
                Q(cat__cat_name__icontains=search_query) |
                Q(cat__dep__dep_name__icontains=search_query) |
                Q(sub_cat_name__icontains=search_query) |
                Q(id__icontains=search_query) |
                Q(status__icontains=search_query)
            )

        # Apply sorting
        sort_by = request.data.get('sort_by', 'cat__dep__dep_name')  # Default sorting by 'dep_name'
        if sort_by == 'dep_name':
            sort_by = 'cat__dep__dep_name'
        if sort_by == 'cat_name':
            sort_by = 'cat__cat_name'
        if sort_by not in ['cat__dep__dep_name', 'cat__cat_name', 'sub_cat_name', 'id', 'status']:
            sort_by = 'cat__dep__dep_name'  # If invalid sort field provided, default to 'dep_name'

        sort_order = request.data.get('sort_order', 'asc')  # Default sorting order is ascending
        if sort_order.lower() not in ['asc', 'desc']:
            sort_order = 'asc'  # If invalid sort order provided, default to ascending

        if sort_order.lower() == 'asc':
            sub_categories = sub_categories.order_by(sort_by)
        else:
            sub_categories = sub_categories.order_by(
                f'-{sort_by}')  # Minus sign for descending order

        # Apply pagination
        page_size = int(request.data.get('no_of_entries', 10))  # Default page size is 10
        paginator = Paginator(sub_categories, page_size)
        page_number = request.data.get('page_no', 1)
        page_obj = paginator.get_page(page_number)

        # Construct response data
        response_data = []
        for data in page_obj.object_list.values('cat__dep__dep_name', 'sub_cat_name', 'cat__id', 'cat__cat_name', 'id',
                                                'status'):
            info = {
                "dep_name": data['cat__dep__dep_name'],
                "cat_id": data['cat__id'],
                "sub_cat_name": data['sub_cat_name'],
                "cat_name": data['cat__cat_name'],
                "id": data['id'],
                "status": data['status']
            }
            response_data.append(info)

        return Response({
            "data": response_data,
            "current_page": page_obj.number,
            "total_pages": paginator.num_pages,
            "total_entries": paginator.count,
            "statusCode": "1"
        }, status=200)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_sub_category_dropdown(request):
    cat_id = request.data.get('cat_id')
    if not cat_id:
        return Response({'statusCode': '0', 'error': 'Please provide category'}, status=400)
    try:
        user_id = request.user.user_id
        departments_mapped_userid = Department.objects.filter(user_id=user_id, user=request.user)
        categories = Category.objects.filter(dep__in=departments_mapped_userid)
        is_cat_exists = categories.filter(pk=cat_id).exists()
        if not is_cat_exists:
            return Response(
                {"statusCode": 0, "message": "Category with id " + format(cat_id) + " does not exist"},
                status=400)
        category = categories.get(pk=cat_id)
        sub_categories = SubCategory.objects.filter(cat=category)
        # Construct response data
        response_data = []
        for data in sub_categories.values('sub_cat_name', 'id'):
            info = {
                "sub_cat_name": data['sub_cat_name'],
                "id": data['id'],
            }
            response_data.append(info)

        return Response({
            "data": response_data,
            "statusCode": "1"
        }, status=200)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_category_dropdown(request):
    try:
        user_id = request.user.user_id
        departments_mapped_userid = Department.objects.filter(user_id=user_id, user=request.user)
        categories_mapped_userid = Category.objects.filter(dep__in=departments_mapped_userid)

        # Construct response data
        response_data = []
        for data in categories_mapped_userid.values('dep__dep_name', 'dep__id', 'cat_name', 'id', 'status'):
            info = {
                "dep_name": data['dep__dep_name'],
                "dep_id": data['dep__id'],
                "cat_name": data['cat_name'],
                "id": data['id'],
                "status": data['status']
            }
            response_data.append(info)

        return Response({
            "data": response_data,
            "statusCode": "1"
        }, status=200)
    except Exception as e:
        return Response({'error': str(e)}, status=500)
