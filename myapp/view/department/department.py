import pandas as pd
from django.core.paginator import Paginator
from django.db.models import Count, Sum, Q
from django.http import HttpResponse
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.workbook import Workbook
from rest_framework.decorators import permission_classes, api_view
from rest_framework.response import Response

from ...model.department import Department, Category, Document
from ...utils.common import convert_size, size_multiplier
from ...utils.decoraters import IsAuthenticated


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_department_file_storage_report(request):
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

        departments = Department.objects.filter(user_id=request.user.user_id, user=request.user)
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
@permission_classes([IsAuthenticated])  # Add the necessary permission classes
def download_excel_report(request):
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

        departments = Department.objects.filter(user_id=request.user.user_id, user=request.user)
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
@permission_classes([IsAuthenticated])
def get_departments_by_userid(request):
    response_data = []
    try:
        user_id = request.user.user_id
        departments = Department.objects.filter(user_id=user_id, user=request.user)
        for dep in departments:
            info = {
                'id': dep.id,
                'dep_name': dep.dep_name
            }
            response_data.append(info)
        return Response({'data': response_data, 'statusCode': 1}, status=200)
    except Exception as e:
        return Response({'error': str(e)}, status=500)
