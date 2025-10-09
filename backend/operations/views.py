from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime, timedelta

from .models import AppointmentManagement, QueueManagement, PriorityQueue, Notification, Messaging, DoctorAvailability, Conversation, Message, MessageReaction, MessageNotification
from backend.users.models import User
from .serializers import DashboardStatsSerializer, ConversationSerializer, MessageSerializer, CreateMessageSerializer, CreateReactionSerializer, UserSerializer, MessageNotificationSerializer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def doctor_dashboard_stats(request):
    """
    Get dashboard statistics for a doctor
    - Total appointments (today and upcoming)
    - Patients in queue (normal and priority)
    - Notifications (unread messages from patients, nurses, other doctors)
    - Pending assessments (nurse charts awaiting doctor review)
    """
    try:
        # Get the current doctor
        doctor = request.user
        
        # Get today's date
        today = timezone.now().date()
        
        # 1. Total Appointments (today and upcoming)
        total_appointments = AppointmentManagement.objects.filter(
            doctor__user=doctor,
            appointment_date__date__gte=today,
            status__in=['scheduled', 'in_progress']
        ).count()
        
        # 2. Patients in Queue (normal and priority)
        # Normal queue - patients waiting in OPD
        normal_queue = QueueManagement.objects.filter(
            department='OPD',
            status='waiting'
        ).count()
        
        # Priority queue - patients with special needs
        priority_queue = PriorityQueue.objects.filter(
            department='OPD'
        ).count()
        
        total_patients = normal_queue + priority_queue
        
        # 3. Notifications (unread messages from patients, nurses, other doctors)
        notifications = Notification.objects.filter(
            user=doctor,
            is_read=False
        ).count()
        
        # 4. Pending Assessments (nurse charts awaiting doctor review)
        # For now, set to 0 since NurseChart model is not implemented yet
        pending_assessment = 0
        # Prepare response data
        stats_data = {
            'total_appointments': total_appointments,
            'total_patients': total_patients,
            'normal_queue': normal_queue,
            'priority_queue': priority_queue,
            'notifications': notifications,
            'pending_assessment': 0
        }
        
        serializer = DashboardStatsSerializer(stats_data)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': f'Failed to fetch dashboard statistics: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def doctor_appointments(request):
    """
    Get appointments for the current doctor
    """
    try:
        doctor = request.user
        today = timezone.now().date()
        
        appointments = AppointmentManagement.objects.filter(
            doctor__user=doctor,
            appointment_date__date__gte=today
        ).order_by('appointment_date')
        
        from .serializers import AppointmentSerializer
        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': f'Failed to fetch appointments: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def doctor_queue_patients(request):
    """
    Get patients in queue for the current doctor
    """
    try:
        # Get normal queue patients
        normal_queue = QueueManagement.objects.filter(
            department='OPD',
            status='waiting'
        ).order_by('position_in_queue')
        
        # Get priority queue patients
        priority_queue = PriorityQueue.objects.filter(
            department='OPD'
        ).order_by('priority_position')
        
        from .serializers import QueueSerializer, PriorityQueueSerializer
        
        normal_serializer = QueueSerializer(normal_queue, many=True)
        priority_serializer = PriorityQueueSerializer(priority_queue, many=True)
        
        return Response({
            'normal_queue': normal_serializer.data,
            'priority_queue': priority_serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': f'Failed to fetch queue patients: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def doctor_notifications(request):
    """
    Get notifications for the current doctor
    """
    try:
        doctor = request.user
        
        notifications = Notification.objects.filter(
            user=doctor
        ).order_by('-created_at')[:10]  # Get last 10 notifications
        
        from .serializers import NotificationSerializer
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': f'Failed to fetch notifications: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def mark_notification_as_read(request, notification_id):
    """
    Mark a specific notification as read
    """
    try:
        doctor = request.user
        
        notification = Notification.objects.filter(
            id=notification_id,
            user=doctor
        ).first()
        
        if not notification:
            return Response({
                'error': 'Notification not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        notification.is_read = True
        notification.save()
        
        return Response({
            'message': 'Notification marked as read'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': f'Failed to mark notification as read: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_all_notifications_read(request):
    """
    Mark all notifications as read for the current doctor
    """
    try:
        doctor = request.user
        
        updated_count = Notification.objects.filter(
            user=doctor,
            is_read=False
        ).update(is_read=True)
        
        return Response({
            'message': f'{updated_count} notifications marked as read'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': f'Failed to mark notifications as read: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def doctor_pending_assessments(request):
    """
    Get pending nurse charts for the current doctor
    """
    try:
        doctor = request.user
        
        # For now, return empty list since NurseChart model is not implemented yet
        # In the future, this would fetch pending nurse charts
        return Response([], status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': f'Failed to fetch pending assessments: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def doctor_blocked_dates(request):
    """
    Get blocked dates for the current doctor
    """
    try:
        doctor = request.user

        # Safely resolve the doctor's profile; return empty list if none exists
        from backend.users.models import GeneralDoctorProfile
        doctor_profile = GeneralDoctorProfile.objects.filter(user=doctor).first()
        if not doctor_profile:
            return Response([], status=status.HTTP_200_OK)
        
        blocked_dates = DoctorAvailability.objects.filter(
            doctor=doctor_profile,
            is_blocked=True
        ).values_list('date', flat=True)
        
        return Response(list(blocked_dates), status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': f'Failed to fetch blocked dates: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def doctor_block_date(request):
    """
    Block a date for the current doctor
    """
    try:
        doctor = request.user
        date = request.data.get('date')
        reason = request.data.get('reason', '')
        
        if not date:
            return Response({
                'error': 'Date is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Resolve the doctor's profile safely
        from backend.users.models import GeneralDoctorProfile
        doctor_profile = GeneralDoctorProfile.objects.filter(user=doctor).first()
        if not doctor_profile:
            return Response({
                'error': 'Doctor profile not found for this user.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if date is already blocked
        existing_block = DoctorAvailability.objects.filter(
            doctor=doctor_profile,
            date=date
        ).first()
        
        if existing_block:
            return Response({
                'error': 'Date is already blocked'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create new blocked date
        DoctorAvailability.objects.create(
            doctor=doctor_profile,
            date=date,
            reason=reason,
            is_blocked=True
        )
        
        return Response({
            'message': 'Date blocked successfully'
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'error': f'Failed to block date: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def doctor_create_appointment(request):
    """
    Create a new appointment for the current doctor
    """
    try:
        doctor = request.user
        
        # Get patient by name (in a real app, you'd have patient selection)
        patient_name = request.data.get('patient_name')
        appointment_date = request.data.get('appointment_date')
        appointment_type = request.data.get('appointment_type', 'consultation')
        notes = request.data.get('notes', '')
        
        if not all([patient_name, appointment_date]):
            return Response({
                'error': 'Patient name and appointment date are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # For now, create a mock patient or find existing one
        # In a real app, you'd have proper patient selection
        from backend.users.models import PatientProfile
        
        # Try to find existing patient or create a placeholder
        patient_profile = PatientProfile.objects.filter(
            user__full_name__icontains=patient_name
        ).first()
        
        if not patient_profile:
            return Response({
                'error': 'Patient not found. Please ensure the patient is registered.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create appointment
        appointment = AppointmentManagement.objects.create(
            patient=patient_profile,
            doctor=doctor.doctor_profile,
            appointment_date=appointment_date,
            appointment_type=appointment_type,
            status='scheduled'
        )
        
        # Create notification for the doctor about the new appointment
        Notification.objects.create(
            user=doctor,
            message=f"New appointment scheduled with {patient_name} on {appointment_date}"
        )
        
        return Response({
            'message': 'Appointment created successfully',
            'appointment_id': appointment.appointment_id
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'error': f'Failed to create appointment: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Messaging Views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_conversations(request):
    """
    Get all conversations for the current user
    """
    try:
        user = request.user
        
        # Get conversations where user is a participant
        conversations = Conversation.objects.filter(
            participants=user,
            is_active=True
        ).prefetch_related('participants', 'messages__sender', 'messages__reactions__user')
        
        serializer = ConversationSerializer(conversations, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': f'Failed to fetch conversations: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_conversation(request):
    """
    Create a new conversation with another user
    """
    try:
        user = request.user
        other_user_id = request.data.get('other_user_id')
        
        if not other_user_id:
            return Response({
                'error': 'other_user_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if other user exists and is a doctor or nurse
        try:
            other_user = User.objects.get(id=other_user_id)
            if other_user.role not in ['doctor', 'nurse']:
                return Response({
                    'error': 'Can only message doctors and nurses'
                }, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({
                'error': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if conversation already exists
        existing_conversation = Conversation.objects.filter(
            participants=user
        ).filter(
            participants=other_user
        ).first()
        
        if existing_conversation:
            serializer = ConversationSerializer(existing_conversation, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        # Create new conversation
        conversation = Conversation.objects.create()
        conversation.participants.add(user, other_user)
        
        serializer = ConversationSerializer(conversation, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'error': f'Failed to create conversation: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_messages(request, conversation_id):
    """
    Get messages for a specific conversation
    """
    try:
        user = request.user
        
        # Check if user is participant in conversation
        conversation = Conversation.objects.filter(
            id=conversation_id,
            participants=user
        ).first()
        
        if not conversation:
            return Response({
                'error': 'Conversation not found or access denied'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get messages with reactions
        messages = conversation.messages.all().prefetch_related('reactions__user')
        serializer = MessageSerializer(messages, many=True)
        
        # Mark messages as read and delivered
        conversation.mark_messages_as_read(user)
        conversation.mark_messages_as_delivered(user)
        
        # Send delivery notifications for unread messages
        unread_messages = conversation.messages.filter(
            is_delivered=False
        ).exclude(sender=user)
        
        for message in unread_messages:
            send_delivery_notification(message, user.id)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': f'Failed to fetch messages: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_message(request, conversation_id):
    """
    Send a message to a conversation
    """
    try:
        user = request.user
        
        # Check if user is participant in conversation
        conversation = Conversation.objects.filter(
            id=conversation_id,
            participants=user
        ).first()
        
        if not conversation:
            return Response({
                'error': 'Conversation not found or access denied'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = CreateMessageSerializer(data=request.data)
        if serializer.is_valid():
            message = serializer.save(
                conversation=conversation,
                sender=user
            )
            
            # Update file information if attachment exists
            if message.file_attachment:
                message.file_name = message.file_attachment.name.split('/')[-1]
                message.file_size = message.file_attachment.size
                message.save()
            
            # Update conversation timestamp
            conversation.save()
            
            # Create notifications for recipients
            message.create_notifications()
            
            # Send real-time notifications via WebSocket
            send_message_notification(message)
            
            response_serializer = MessageSerializer(message)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        return Response({
            'error': f'Failed to send message: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_reaction(request, message_id):
    """
    Add a reaction to a message
    """
    try:
        user = request.user
        
        # Get message and check if user has access
        message = Message.objects.filter(
            id=message_id,
            conversation__participants=user
        ).first()
        
        if not message:
            return Response({
                'error': 'Message not found or access denied'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = CreateReactionSerializer(data=request.data)
        if serializer.is_valid():
            reaction_type = serializer.validated_data['reaction_type']
            
            # Check if user already reacted with this type
            existing_reaction = MessageReaction.objects.filter(
                message=message,
                user=user,
                reaction_type=reaction_type
            ).first()
            
            if existing_reaction:
                # Remove existing reaction
                existing_reaction.delete()
                return Response({
                    'message': 'Reaction removed',
                    'action': 'removed'
                }, status=status.HTTP_200_OK)
            else:
                # Remove other reactions from this user
                MessageReaction.objects.filter(
                    message=message,
                    user=user
                ).exclude(reaction_type=reaction_type).delete()
                
                # Add new reaction
                reaction = MessageReaction.objects.create(
                    message=message,
                    user=user,
                    reaction_type=reaction_type
                )
                
                return Response({
                    'message': 'Reaction added',
                    'action': 'added',
                    'reaction': CreateReactionSerializer(reaction).data
                }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        return Response({
            'error': f'Failed to add reaction: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_available_users(request):
    """
    Get list of verified doctors and nurses available for secure messaging.
    Only shows healthcare providers who have completed admin verification process.
    """
    try:
        user = request.user
        search_query = request.GET.get('search', '').strip()
        
        # Security: Only allow verified users to access messaging
        if user.verification_status != 'approved':
            return Response({
                'error': 'Account verification required to access messaging features.',
                'verification_status': user.verification_status
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get only admin-verified doctors and nurses (excluding current user)
        # This ensures secure communication between authenticated healthcare providers
        available_users = User.objects.filter(
            role__in=['doctor', 'nurse'],
            is_active=True,
            verification_status='approved'  # Only admin-verified users for security
        ).exclude(id=user.id)
        
        # Apply search filter if search query is provided
        if search_query:
            available_users = available_users.filter(
                Q(full_name__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(role__icontains=search_query)
            )
        
        serializer = UserSerializer(available_users, many=True)
        return Response({
            'users': serializer.data,
            'total_count': available_users.count(),
            'message': f'Found {available_users.count()} verified healthcare providers'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': f'Failed to fetch available users: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_message_notifications(request):
    """
    Get message notifications for the current user
    """
    try:
        user = request.user
        
        # Get unread message notifications
        notifications = MessageNotification.objects.filter(
            recipient=user,
            is_sent=False
        ).order_by('-created_at')[:20]
        
        serializer = MessageNotificationSerializer(notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': f'Failed to fetch notifications: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_notification_as_sent(request, notification_id):
    """
    Mark a notification as sent
    """
    try:
        user = request.user
        
        notification = MessageNotification.objects.filter(
            id=notification_id,
            recipient=user
        ).first()
        
        if not notification:
            return Response({
                'error': 'Notification not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        notification.is_sent = True
        notification.sent_at = timezone.now()
        notification.save()
        
        return Response({
            'message': 'Notification marked as sent'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': f'Failed to mark notification as sent: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_message_as_read(request, message_id):
    """
    Mark a specific message as read
    """
    try:
        user = request.user
        
        message = Message.objects.filter(
            id=message_id,
            conversation__participants=user
        ).first()
        
        if not message:
            return Response({
                'error': 'Message not found or access denied'
            }, status=status.HTTP_404_NOT_FOUND)
        
        if not message.is_read and message.sender != user:
            message.is_read = True
            message.read_at = timezone.now()
            message.save()
            
            # Create read notification
            MessageNotification.objects.create(
                message=message,
                recipient=message.sender,
                notification_type='message_read'
            )
            
            # Send real-time read notification
            send_read_notification(message, user.id)
        
        return Response({
            'message': 'Message marked as read'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': f'Failed to mark message as read: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Medicine Inventory Views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_medicine_inventory(request):
    """
    Get medicine inventory for the current nurse with optional search functionality
    """
    try:
        user = request.user
        
        # Check if user is a nurse
        if user.role != 'nurse':
            return Response({
                'error': 'Access denied. Only nurses can view medicine inventory.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get search parameter
        search_query = request.GET.get('search', '').strip()
        
        # Get medicine inventory for the current nurse
        from .models import MedicineInventory
        inventory = MedicineInventory.objects.filter(
            inventory__user=user
        )
        
        # Apply search filter if search query is provided
        if search_query:
            inventory = inventory.filter(
                Q(medicine_name__icontains=search_query) |
                Q(batch_number__icontains=search_query) |
                Q(manufacturer__icontains=search_query)
            )
        
        inventory = inventory.order_by('medicine_name')
        
        from .serializers import MedicineInventorySerializer
        serializer = MedicineInventorySerializer(inventory, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': f'Failed to fetch medicine inventory: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_medicine(request):
    """
    Add a new medicine to inventory
    """
    try:
        user = request.user
        
        # Check if user is a nurse
        if user.role != 'nurse':
            return Response({
                'error': 'Access denied. Only nurses can manage medicine inventory.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        from .models import MedicineInventory
        from backend.users.models import NurseProfile
        
        # Get nurse profile
        nurse_profile = NurseProfile.objects.get(user=user)
        
        # Create medicine inventory entry
        medicine = MedicineInventory.objects.create(
            inventory=nurse_profile,
            medicine_name=request.data.get('name'),
            stock_number=request.data.get('quantity', 0),
            current_stock=request.data.get('quantity', 0),
            unit_price=request.data.get('unit_price', 0),
            minimum_stock_level=request.data.get('min_stock_level', 0),
            expiry_date=request.data.get('expiry_date'),
            batch_number=request.data.get('batch_number', ''),
            usage_pattern=request.data.get('description', '')
        )
        
        from .serializers import MedicineInventorySerializer
        serializer = MedicineInventorySerializer(medicine)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'error': f'Failed to add medicine: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_medicine(request, medicine_id):
    """
    Update medicine inventory
    """
    try:
        user = request.user
        
        # Check if user is a nurse
        if user.role != 'nurse':
            return Response({
                'error': 'Access denied. Only nurses can manage medicine inventory.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        from .models import MedicineInventory
        
        # Get medicine
        medicine = MedicineInventory.objects.get(
            id=medicine_id,
            inventory__user=user
        )
        
        # Update fields
        medicine.medicine_name = request.data.get('name', medicine.medicine_name)
        medicine.current_stock = request.data.get('quantity', medicine.current_stock)
        medicine.unit_price = request.data.get('unit_price', medicine.unit_price)
        medicine.minimum_stock_level = request.data.get('min_stock_level', medicine.minimum_stock_level)
        medicine.expiry_date = request.data.get('expiry_date', medicine.expiry_date)
        medicine.usage_pattern = request.data.get('description', medicine.usage_pattern)
        medicine.save()
        
        from .serializers import MedicineInventorySerializer
        serializer = MedicineInventorySerializer(medicine)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except MedicineInventory.DoesNotExist:
        return Response({
            'error': 'Medicine not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': f'Failed to update medicine: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_medicine(request, medicine_id):
    """
    Delete medicine from inventory
    """
    try:
        user = request.user
        
        # Check if user is a nurse
        if user.role != 'nurse':
            return Response({
                'error': 'Access denied. Only nurses can manage medicine inventory.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        from .models import MedicineInventory
        
        # Get and delete medicine
        medicine = MedicineInventory.objects.get(
            id=medicine_id,
            inventory__user=user
        )
        medicine.delete()
        
        return Response({
            'message': 'Medicine deleted successfully'
        }, status=status.HTTP_200_OK)
        
    except MedicineInventory.DoesNotExist:
        return Response({
            'error': 'Medicine not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': f'Failed to delete medicine: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Nurse Queue Views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def nurse_queue_patients(request):
    """
    Get patients in queue for nurses
    """
    try:
        user = request.user
        
        # Check if user is a nurse
        if user.role != 'nurse':
            return Response({
                'error': 'Access denied. Only nurses can view patient queue.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get normal queue patients
        normal_queue = QueueManagement.objects.filter(
            department='OPD',
            status='waiting'
        ).order_by('position_in_queue')
        
        # Get priority queue patients
        priority_queue = PriorityQueue.objects.filter(
            department='OPD'
        ).order_by('priority_position')
        
        from .serializers import QueueSerializer, PriorityQueueSerializer
        
        normal_serializer = QueueSerializer(normal_queue, many=True)
        priority_serializer = PriorityQueueSerializer(priority_queue, many=True)
        
        return Response({
            'normal_queue': normal_serializer.data,
            'priority_queue': priority_serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': f'Failed to fetch queue patients: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Doctor Selection Views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_available_doctors(request):
    """
    Get available verified doctors by specialization with optional search functionality.
    Only shows doctors who have completed admin verification process.
    """
    try:
        user = request.user
        
        # Check if user is a nurse and is verified
        if user.role != 'nurse':
            return Response({
                'error': 'Access denied. Only nurses can view available doctors.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Security: Only allow verified nurses to access doctor information
        if user.verification_status != 'approved':
            return Response({
                'error': 'Account verification required to access doctor information.',
                'verification_status': user.verification_status
            }, status=status.HTTP_403_FORBIDDEN)
        
        specialization = request.GET.get('specialization', '')
        search_query = request.GET.get('search', '').strip()
        
        # Get only admin-verified doctors with the specified specialization
        from backend.users.models import GeneralDoctorProfile
        
        doctors_query = GeneralDoctorProfile.objects.filter(
            user__verification_status='approved',  # Only admin-verified doctors for security
            user__is_active=True
        )
        
        if specialization:
            doctors_query = doctors_query.filter(specialization__icontains=specialization)
        
        # Apply search filter if search query is provided
        if search_query:
            doctors_query = doctors_query.filter(
                Q(user__full_name__icontains=search_query) |
                Q(specialization__icontains=search_query) |
                Q(department__icontains=search_query)
            )
        
        doctors = doctors_query.select_related('user')
        
        # Get current patient count for each doctor
        doctor_data = []
        for doctor in doctors:
            current_patients = AppointmentManagement.objects.filter(
                doctor=doctor,
                appointment_date__date=timezone.now().date(),
                status__in=['scheduled', 'in_progress']
            ).count()
            
            doctor_data.append({
                'id': doctor.user.id,
                'full_name': doctor.user.full_name,
                'specialization': doctor.specialization,
                'department': doctor.department,
                'is_available': current_patients < 10,  # Assume max 10 patients per doctor
                'current_patients': current_patients,
                'profile_picture': doctor.user.profile_picture,
                'verification_status': doctor.user.verification_status,
                'is_verified': True  # All returned doctors are verified
            })
        
        return Response({
            'doctors': doctor_data,
            'total_count': len(doctor_data),
            'message': f'Found {len(doctor_data)} verified doctors',
            'security_note': 'Only admin-verified doctors are shown for secure healthcare operations'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': f'Failed to fetch available doctors: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def assign_patient_to_doctor(request):
    """
    Assign a patient to a doctor
    """
    try:
        user = request.user
        
        # Check if user is a nurse
        if user.role != 'nurse':
            return Response({
                'error': 'Access denied. Only nurses can assign patients.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        patient_id = request.data.get('patient_id')
        doctor_id = request.data.get('doctor_id')
        specialization = request.data.get('specialization')
        assigned_by = request.data.get('assigned_by')
        
        if not all([patient_id, doctor_id, specialization]):
            return Response({
                'error': 'Patient ID, Doctor ID, and specialization are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get doctor profile
        from backend.users.models import GeneralDoctorProfile
        try:
            doctor_profile = GeneralDoctorProfile.objects.get(user_id=doctor_id)
        except GeneralDoctorProfile.DoesNotExist:
            return Response({
                'error': 'Doctor not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Create appointment for the patient
        from backend.users.models import PatientProfile
        try:
            patient_profile = PatientProfile.objects.get(user_id=patient_id)
        except PatientProfile.DoesNotExist:
            return Response({
                'error': 'Patient not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Create appointment
        appointment = AppointmentManagement.objects.create(
            patient=patient_profile,
            doctor=doctor_profile,
            appointment_date=timezone.now(),
            appointment_type='consultation',
            status='scheduled',
            notes=f'Assigned by nurse for {specialization} consultation'
        )
        
        # Remove patient from queue if they were in queue
        QueueManagement.objects.filter(
            patient=patient_profile,
            status='waiting'
        ).update(status='assigned')
        
        PriorityQueue.objects.filter(
            patient=patient_profile
        ).delete()
        
        # Create notification for doctor
        Notification.objects.create(
            user=doctor_profile.user,
            message=f'New patient {patient_profile.user.full_name} assigned to you for {specialization} consultation',
            is_read=False
        )
        
        return Response({
            'message': 'Patient assigned successfully',
            'appointment_id': appointment.appointment_id
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'error': f'Failed to assign patient: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def send_message_notification(message):
    """Send real-time notification via WebSocket"""
    channel_layer = get_channel_layer()
    message_data = MessageSerializer(message).data
    
    # Send to all participants except sender
    for participant in message.conversation.participants.exclude(id=message.sender.id):
        group_name = f'messaging_{participant.id}'
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'new_message',
                'message': message_data
            }
        )

def send_delivery_notification(message, recipient_id):
    """Send delivery notification via WebSocket"""
    channel_layer = get_channel_layer()
    message_data = MessageSerializer(message).data
    
    group_name = f'messaging_{message.sender.id}'
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'message_delivered',
            'message': message_data
        }
    )

def send_read_notification(message, reader_id):
    """Send read notification via WebSocket"""
    channel_layer = get_channel_layer()
    message_data = MessageSerializer(message).data
    
    group_name = f'messaging_{message.sender.id}'
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'message_read',
            'message': message_data
        }
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_doctor_assignments(request):
    """
    Get patient assignments for the current doctor
    """
    try:
        user = request.user

        # Check if user is a doctor
        if user.role != 'doctor':
            return Response({
                'error': 'Access denied. Only doctors can view their assignments.'
            }, status=status.HTTP_403_FORBIDDEN)

        # Get doctor profile
        from backend.users.models import GeneralDoctorProfile
        try:
            doctor_profile = GeneralDoctorProfile.objects.get(user=user)
        except GeneralDoctorProfile.DoesNotExist:
            return Response({
                'error': 'Doctor profile not found'
            }, status=status.HTTP_404_NOT_FOUND)

        # Get assignments for this doctor
        from .models import PatientAssignment
        assignments = PatientAssignment.objects.filter(
            doctor=doctor_profile
        ).select_related('patient__user', 'assigned_by')

        from .serializers import PatientAssignmentSerializer
        serializer = PatientAssignmentSerializer(assignments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'error': f'Failed to fetch assignments: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def accept_assignment(request, assignment_id):
    """
    Accept a patient assignment
    """
    try:
        user = request.user

        # Check if user is a doctor
        if user.role != 'doctor':
            return Response({
                'error': 'Access denied. Only doctors can accept assignments.'
            }, status=status.HTTP_403_FORBIDDEN)

        # Get assignment
        from .models import PatientAssignment
        try:
            assignment = PatientAssignment.objects.get(
                id=assignment_id,
                doctor__user=user
            )
        except PatientAssignment.DoesNotExist:
            return Response({
                'error': 'Assignment not found or access denied'
            }, status=status.HTTP_404_NOT_FOUND)

        # Update assignment status
        assignment.status = 'accepted'
        assignment.accepted_at = timezone.now()
        assignment.save()

        from .serializers import PatientAssignmentSerializer
        serializer = PatientAssignmentSerializer(assignment)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'error': f'Failed to accept assignment: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def consultation_notes(request, assignment_id=None):
    """
    Get or create consultation notes for an assignment
    """
    try:
        user = request.user

        # Check if user is a doctor
        if user.role != 'doctor':
            return Response({
                'error': 'Access denied. Only doctors can manage consultation notes.'
            }, status=status.HTTP_403_FORBIDDEN)

        if request.method == 'GET':
            # Get consultation notes for assignment
            from .models import ConsultationNotes
            try:
                notes = ConsultationNotes.objects.get(
                    assignment_id=assignment_id,
                    doctor__user=user
                )
                from .serializers import ConsultationNotesSerializer
                serializer = ConsultationNotesSerializer(notes)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except ConsultationNotes.DoesNotExist:
                return Response({
                    'error': 'Consultation notes not found'
                }, status=status.HTTP_404_NOT_FOUND)

        elif request.method == 'POST':
            # Create or update consultation notes
            from .models import PatientAssignment, ConsultationNotes
            try:
                assignment = PatientAssignment.objects.get(
                    id=assignment_id,
                    doctor__user=user
                )
            except PatientAssignment.DoesNotExist:
                return Response({
                    'error': 'Assignment not found or access denied'
                }, status=status.HTTP_404_NOT_FOUND)

            # Create or update consultation notes
            notes, created = ConsultationNotes.objects.get_or_create(
                assignment=assignment,
                defaults={
                    'doctor': assignment.doctor,
                    'patient': assignment.patient,
                    'chief_complaint': request.data.get('chief_complaint', ''),
                    'history_of_present_illness': request.data.get('history_of_present_illness', ''),
                    'physical_examination': request.data.get('physical_examination', ''),
                    'diagnosis': request.data.get('diagnosis', ''),
                    'treatment_plan': request.data.get('treatment_plan', ''),
                    'medications_prescribed': request.data.get('medications_prescribed', ''),
                    'follow_up_instructions': request.data.get('follow_up_instructions', ''),
                    'additional_notes': request.data.get('additional_notes', ''),
                    'status': request.data.get('status', 'draft')
                }
            )

            if not created:
                # Update existing notes
                for field in ['chief_complaint', 'history_of_present_illness', 'physical_examination',
                             'diagnosis', 'treatment_plan', 'medications_prescribed', 'follow_up_instructions',
                             'additional_notes', 'status']:
                    if field in request.data:
                        setattr(notes, field, request.data[field])
                notes.save()

            from .serializers import ConsultationNotesSerializer
            serializer = ConsultationNotesSerializer(notes)
            return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'error': f'Failed to manage consultation notes: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)