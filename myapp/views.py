import logging

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .models import Grievance
from .serializers import GrievanceSerializer
from .utils.decoraters import IsAuthenticated

user_dto = {}

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_grievance(request):
    serializer_data = request.data.copy()  # Create a copy of the request data

    try:
        serializer_data['user'] = request.user.user_id
        serializer = GrievanceSerializer(data=serializer_data)

        if serializer.is_valid():
            # Save the Grievance instance with user_id set
            serializer.save()  # Assuming Grievance model has user_id field
            return Response({'message': 'Grievance created successfully'}, status=201)

        return Response(serializer.errors, status=400)

    except IndexError:
        # Handle cases where the token is not found or not in the expected format
        return Response({'error': 'Invalid token format'}, status=400)
    except KeyError as e:
        # Handle cases where the expected claims are not present in the token payload
        return Response({'error': f'Missing claim in token: {e}'}, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_grievance(request):
    grievances = Grievance.objects.filter(user=request.user)
    serializer = GrievanceSerializer(grievances, many=True)
    return Response(serializer.data, status=200)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_grievance_by_userid(request, user_id):
    grievances = Grievance.objects.filter(user_id=user_id, user=request.user)
    serializer = GrievanceSerializer(grievances, many=True)
    if grievances is None:
        return Response({'error': 'No data found'}, status=404)

    return Response(serializer.data, status=200)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_grievances_by_userorgkid(request):
    type_of_id = request.data.get('type_of_id')
    id = request.data.get('value')

    if id and not (id.startswith('G') or id.startswith('U')):
        return Response({
            'statusCode': '0',
            'messege': 'Please enter a valid id'
        })
    if type_of_id == 'user_id':
        grievances = Grievance.objects.filter(user_id=id, user=request.user)
    elif type_of_id == 'gk_id':
        grievances = Grievance.objects.filter(gk_id=id, user=request.user)
    else:
        return Response({'statusCode': '0',
                         'messege': 'Please enter a valid id type'})

    serializer = GrievanceSerializer(grievances, many=True)

    return Response(serializer.data, status=200)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_grievance(request, gk_id):
    try:
        grievance = Grievance.objects.get(pk=gk_id, user=request.user)

        serializer = GrievanceSerializer(grievance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'statusCode': '1', 'message': 'Grievance Updated Successfully'}, serializer.data)

        return Response({'statusCode': '0'}, serializer.errors, status=400)

    except Grievance.DoesNotExist:
        return Response({'statusCode': '0', 'error': 'Grievance not found'}, status=404)
    except Exception as e:
        return Response({'statusCode': '0', 'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_grievance(request, gk_id):
    grievance = Grievance.objects.filter(gk_id=gk_id, user=request.user).first()

    if grievance is None:
        return Response({'statusCode': '0', 'error': 'Grievance not found'}, status=404)

    grievance.delete()

    return Response({'statusCode': '1', 'message': 'Grievance deleted successfully'}, status=200)


