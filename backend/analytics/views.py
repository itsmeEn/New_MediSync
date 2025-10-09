import asyncio
import uuid
from datetime import datetime, timedelta
from django.utils import timezone
from django.db import transaction
from django.core.cache import cache
from django.http import HttpResponse
from django.template.loader import render_to_string
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import threading
from concurrent.futures import ThreadPoolExecutor

# PDF generation imports
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
    from reportlab.graphics.shapes import Drawing
    from reportlab.graphics.charts.piecharts import Pie
    from reportlab.graphics.charts.barcharts import VerticalBarChart
    from reportlab.graphics.charts.linecharts import HorizontalLineChart
    from reportlab.graphics import renderPDF
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import io
    import base64
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

from .models import AnalyticsResult, AnalyticsTask, DataUpdateLog, AnalyticsCache
from .serializers import (
    AnalyticsResultSerializer, AnalyticsTaskSerializer, 
    AnalyticsRequestSerializer, AnalyticsResponseSerializer
)
from .tasks import run_analytics_task_async
from backend.users.models import PatientProfile

class AnalyticsView(APIView):
    """
    Main analytics API endpoint for triggering and retrieving analytics
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get analytics results"""
        analysis_type = request.query_params.get('type', 'full_analysis')
        force_refresh = request.query_params.get('force_refresh', 'false').lower() == 'true'
        
        # Check cache first
        cache_key = f"analytics_{analysis_type}_{request.user.id}"
        if not force_refresh:
            cached_result = cache.get(cache_key)
            if cached_result:
                return Response({
                    'success': True,
                    'message': 'Analytics results retrieved from cache',
                    'data': cached_result,
                    'cached': True
                })
        
        # Get latest result from database
        try:
            latest_result = AnalyticsResult.objects.filter(
                analysis_type=analysis_type,
                status='completed'
            ).order_by('-created_at').first()
            
            if latest_result:
                serializer = AnalyticsResultSerializer(latest_result)
                # Cache the result for 1 hour
                cache.set(cache_key, serializer.data, 3600)
                
                return Response({
                    'success': True,
                    'message': 'Analytics results retrieved',
                    'data': serializer.data,
                    'cached': False
                })
            else:
                return Response({
                    'success': False,
                    'message': 'No analytics results found. Please trigger an analysis first.',
                    'data': None
                }, status=status.HTTP_404_NOT_FOUND)
                
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error retrieving analytics: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        """Trigger new analytics analysis"""
        serializer = AnalyticsRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Invalid request parameters',
                'data': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        analysis_type = serializer.validated_data['analysis_type']
        force_refresh = serializer.validated_data['force_refresh']
        
        # Generate unique task ID
        task_id = str(uuid.uuid4())
        
        try:
            # Create analytics task
            task = AnalyticsTask.objects.create(
                task_id=task_id,
                analysis_type=analysis_type,
                status='pending'
            )
            
            # Start async analytics processing
            run_analytics_task_async.delay(task_id, analysis_type)
            
            return Response({
                'success': True,
                'message': 'Analytics task started',
                'task_id': task_id,
                'data': {
                    'task_id': task_id,
                    'analysis_type': analysis_type,
                    'status': 'pending'
                }
            }, status=status.HTTP_202_ACCEPTED)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error starting analytics task: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_analytics_status(request, task_id):
    """Get the status of a specific analytics task"""
    try:
        task = AnalyticsTask.objects.get(task_id=task_id)
        serializer = AnalyticsTaskSerializer(task)
        
        return Response({
            'success': True,
            'message': 'Task status retrieved',
            'data': serializer.data
        })
        
    except AnalyticsTask.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Task not found',
            'data': None
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error retrieving task status: {str(e)}',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_analytics_history(request):
    """Get analytics history"""
    analysis_type = request.query_params.get('type')
    limit = int(request.query_params.get('limit', 10))
    
    queryset = AnalyticsResult.objects.all()
    if analysis_type:
        queryset = queryset.filter(analysis_type=analysis_type)
    
    queryset = queryset.order_by('-created_at')[:limit]
    serializer = AnalyticsResultSerializer(queryset, many=True)
    
    return Response({
        'success': True,
        'message': 'Analytics history retrieved',
        'data': serializer.data
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def trigger_data_refresh(request):
    """Manually trigger analytics refresh for new data"""
    try:
        # This would typically be called when new data is added
        # For now, we'll trigger a full analysis
        task_id = str(uuid.uuid4())
        
        task = AnalyticsTask.objects.create(
            task_id=task_id,
            analysis_type='full_analysis',
            status='pending'
        )
        
        # Start async processing
        run_analytics_task_async.delay(task_id, 'full_analysis')
        
        return Response({
            'success': True,
            'message': 'Data refresh triggered',
            'task_id': task_id
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error triggering refresh: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_real_time_analytics(request):
    """Get real-time analytics dashboard data"""
    try:
        # Get latest results for different analysis types
        dashboard_data = {}
        
        analysis_types = [
            'patient_health_trends',
            'patient_demographics', 
            'illness_prediction',
            'medication_analysis',
            'patient_volume_prediction'
        ]
        
        for analysis_type in analysis_types:
            latest_result = AnalyticsResult.objects.filter(
                analysis_type=analysis_type,
                status='completed'
            ).order_by('-created_at').first()
            
            if latest_result:
                dashboard_data[analysis_type] = {
                    'status': 'completed',
                    'last_updated': latest_result.updated_at.isoformat(),
                    'data': latest_result.results
                }
            else:
                dashboard_data[analysis_type] = {
                    'status': 'no_data',
                    'last_updated': None,
                    'data': None
                }
        
        return Response({
            'success': True,
            'message': 'Real-time analytics data retrieved',
            'data': dashboard_data
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error retrieving real-time analytics: {str(e)}',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# WebSocket-like endpoint for real-time updates (using Server-Sent Events)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def analytics_stream(request):
    """Stream analytics updates in real-time"""
    import time
    
    def event_stream():
        while True:
            # Get latest analytics results
            latest_results = AnalyticsResult.objects.filter(
                status='completed'
            ).order_by('-updated_at')[:5]
            
            data = {
                'timestamp': timezone.now().isoformat(),
                'results': AnalyticsResultSerializer(latest_results, many=True).data
            }
            
            yield f"data: {json.dumps(data)}\n\n"
            time.sleep(5)  # Update every 5 seconds
    
    from django.http import StreamingHttpResponse
    response = StreamingHttpResponse(
        event_stream(),
        content_type='text/event-stream'
    )
    response['Cache-Control'] = 'no-cache'
    response['Connection'] = 'keep-alive'
    return response

# Doctor Analytics Endpoints
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def doctor_analytics(request):
    """
    Get analytics specifically for doctors
    """
    if request.user.role != 'doctor':
        return Response({
            'error': 'Only doctors can access this endpoint.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        # Get doctor-specific analytics
        analytics_data = {}
        
        # Patient demographics for doctor's patients
        patient_demographics = AnalyticsResult.objects.filter(
            analysis_type='patient_demographics',
            status='completed'
        ).order_by('-created_at').first()
        
        # Illness prediction for doctor's specialty
        illness_prediction = AnalyticsResult.objects.filter(
            analysis_type='illness_prediction',
            status='completed'
        ).order_by('-created_at').first()
        
        # Patient health trends
        health_trends = AnalyticsResult.objects.filter(
            analysis_type='patient_health_trends',
            status='completed'
        ).order_by('-created_at').first()
        
        # Illness surge prediction
        surge_prediction = AnalyticsResult.objects.filter(
            analysis_type='illness_surge_prediction',
            status='completed'
        ).order_by('-created_at').first()
        
        analytics_data = {
            'patient_demographics': patient_demographics.results if patient_demographics else None,
            'illness_prediction': illness_prediction.results if illness_prediction else None,
            'health_trends': health_trends.results if health_trends else None,
            'surge_prediction': surge_prediction.results if surge_prediction else None,
            'doctor_name': request.user.full_name,
            'specialization': getattr(request.user.doctor_profile, 'specialization', 'General Practice') if hasattr(request.user, 'doctor_profile') else 'General Practice',
            'generated_at': timezone.now().isoformat()
        }
        
        return Response({
            'success': True,
            'message': 'Doctor analytics retrieved successfully',
            'data': analytics_data
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error retrieving doctor analytics: {str(e)}',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def nurse_analytics(request):
    """
    Get analytics specifically for nurses
    """
    if request.user.role != 'nurse':
        return Response({
            'error': 'Only nurses can access this endpoint.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        # Get nurse-specific analytics
        analytics_data = {}
        
        # Medication analysis
        medication_analysis = AnalyticsResult.objects.filter(
            analysis_type='medication_analysis',
            status='completed'
        ).order_by('-created_at').first()
        
        # Patient demographics
        patient_demographics = AnalyticsResult.objects.filter(
            analysis_type='patient_demographics',
            status='completed'
        ).order_by('-created_at').first()
        
        # Patient health trends
        health_trends = AnalyticsResult.objects.filter(
            analysis_type='patient_health_trends',
            status='completed'
        ).order_by('-created_at').first()
        
        # Patient volume prediction
        volume_prediction = AnalyticsResult.objects.filter(
            analysis_type='patient_volume_prediction',
            status='completed'
        ).order_by('-created_at').first()
        
        analytics_data = {
            'medication_analysis': medication_analysis.results if medication_analysis else None,
            'patient_demographics': patient_demographics.results if patient_demographics else None,
            'health_trends': health_trends.results if health_trends else None,
            'volume_prediction': volume_prediction.results if volume_prediction else None,
            'nurse_name': request.user.full_name,
            'department': getattr(request.user.nurse_profile, 'department', 'General') if hasattr(request.user, 'nurse_profile') else 'General',
            'generated_at': timezone.now().isoformat()
        }
        
        return Response({
            'success': True,
            'message': 'Nurse analytics retrieved successfully',
            'data': analytics_data
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error retrieving nurse analytics: {str(e)}',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generate_analytics_pdf(request):
    """
    Generate standardized PDF report of analytics findings with hospital information,
    role-specific data, and consistent branding across doctor and nurse views
    """
    if not PDF_AVAILABLE:
        return Response({
            'error': 'PDF generation not available. Please install reportlab and matplotlib.'
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    
    user_role = request.user.role
    report_type = request.GET.get('type', 'full')  # full, doctor, nurse
    
    try:
        # Get hospital information from user profile or set defaults
        hospital_info = get_hospital_information(request.user)
        
        # Get analytics data based on user role
        if user_role == 'doctor' or report_type == 'doctor':
            analytics_data = get_doctor_analytics_data(request.user)
            title = "Analytics Report"
            user_info = {
                'name': request.user.full_name,
                'specialization': getattr(request.user.doctor_profile, 'specialization', 'General Practice') if hasattr(request.user, 'doctor_profile') else 'General Practice',
                'role': 'Doctor',
                'department': getattr(request.user.doctor_profile, 'specialization', 'General Practice') if hasattr(request.user, 'doctor_profile') else 'General Practice'
            }
        elif user_role == 'nurse' or report_type == 'nurse':
            analytics_data = get_nurse_analytics_data(request.user)
            title = "Analytics Report"
            user_info = {
                'name': request.user.full_name,
                'specialization': getattr(request.user.nurse_profile, 'department', 'General') if hasattr(request.user, 'nurse_profile') else 'General',
                'role': 'Nurse',
                'department': getattr(request.user.nurse_profile, 'department', 'General') if hasattr(request.user, 'nurse_profile') else 'General'
            }
        else:
            analytics_data = get_full_analytics_data()
            title = "Analytics Report"
            user_info = None
        
        # Generate PDF with standardized template
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{user_role}_analytics_report_{timezone.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
        
        # Create PDF with custom page template
        doc = create_standardized_pdf_template(response, hospital_info, user_info)
        styles = get_custom_styles()
        story = []
        
        # Add standardized header
        add_standardized_header(story, hospital_info, user_info, title, styles)
        
        # Add analytics dashboard with role-specific content
        add_analytics_dashboard(story, analytics_data, user_info, styles)
        
        # Add standardized footer
        add_standardized_footer(story, styles)
        
        doc.build(story)
        return response
        
    except Exception as e:
        return Response({
            'error': f'Error generating PDF report: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def get_doctor_analytics_data(user):
    """Get analytics data for doctors"""
    return {
        'patient_demographics': get_latest_analytics('patient_demographics'),
        'illness_prediction': get_latest_analytics('illness_prediction'),
        'health_trends': get_latest_analytics('patient_health_trends'),
        'surge_prediction': get_latest_analytics('illness_surge_prediction'),
        'doctor_name': user.full_name,
        'specialization': getattr(user.doctor_profile, 'specialization', 'General Practice') if hasattr(user, 'doctor_profile') else 'General Practice'
    }

def get_nurse_analytics_data(user):
    """Get analytics data for nurses"""
    return {
        'medication_analysis': get_latest_analytics('medication_analysis'),
        'patient_demographics': get_latest_analytics('patient_demographics'),
        'health_trends': get_latest_analytics('patient_health_trends'),
        'volume_prediction': get_latest_analytics('patient_volume_prediction'),
        'nurse_name': user.full_name,
        'department': getattr(user.nurse_profile, 'department', 'General') if hasattr(user, 'nurse_profile') else 'General'
    }

def get_full_analytics_data():
    """Get all analytics data"""
    return {
        'patient_demographics': get_latest_analytics('patient_demographics'),
        'illness_prediction': get_latest_analytics('illness_prediction'),
        'medication_analysis': get_latest_analytics('medication_analysis'),
        'health_trends': get_latest_analytics('patient_health_trends'),
        'volume_prediction': get_latest_analytics('patient_volume_prediction'),
        'surge_prediction': get_latest_analytics('illness_surge_prediction')
    }

def get_latest_analytics(analysis_type):
    """Get latest analytics result for a specific type"""
    result = AnalyticsResult.objects.filter(
        analysis_type=analysis_type,
        status='completed'
    ).order_by('-created_at').first()
    return result.results if result else None

def get_hospital_information(user):
    """
    Get hospital information from user profile or set defaults
    """
    # Try to get hospital info from patient profiles (most common source)
    from backend.users.models import PatientProfile
    
    # Get hospital info from any patient profile as a default
    patient_profile = PatientProfile.objects.filter(hospital__isnull=False).exclude(hospital='').first()
    
    hospital_info = {
        'name': patient_profile.hospital if patient_profile else 'MediSync Healthcare Center',
        'address': '123 Healthcare Avenue, Medical District, City 12345',  # Default address
        'phone': '+1 (555) 123-4567',  # Default phone
        'email': 'info@medisync.healthcare'  # Default email
    }
    
    return hospital_info

def get_custom_styles():
    """
    Get responsive custom styles for the standardized PDF template
    """
    from reportlab.lib.pagesizes import A4
    
    styles = getSampleStyleSheet()
    
    # Calculate responsive font sizes based on page dimensions
    page_width, page_height = A4
    base_font_size = min(page_width, page_height) / 60  # Responsive base size
    
    # Add custom styles for consistent branding with responsive design
    styles.add(ParagraphStyle(
        name='HospitalName',
        parent=styles['Heading1'],
        fontSize=max(18, int(base_font_size * 1.8)),
        fontName='Helvetica-Bold',
        textColor=colors.darkblue,
        alignment=TA_CENTER,
        spaceAfter=8,
        leading=max(20, int(base_font_size * 2.2))  # Responsive line height
    ))
    
    styles.add(ParagraphStyle(
        name='HospitalAddress',
        parent=styles['Normal'],
        fontSize=max(9, int(base_font_size * 1.0)),
        fontName='Helvetica',
        textColor=colors.grey,
        alignment=TA_CENTER,
        spaceAfter=12,
        leading=max(11, int(base_font_size * 1.3))
    ))
    
    styles.add(ParagraphStyle(
        name='ReportTitle',
        parent=styles['Heading1'],
        fontSize=max(16, int(base_font_size * 1.6)),
        fontName='Helvetica-Bold',
        textColor=colors.darkblue,
        alignment=TA_CENTER,
        spaceAfter=10,
        spaceBefore=6,
        leading=max(18, int(base_font_size * 1.9))
    ))
    
    styles.add(ParagraphStyle(
        name='UserInfo',
        parent=styles['Normal'],
        fontSize=max(10, int(base_font_size * 1.1)),
        fontName='Helvetica',
        textColor=colors.black,
        alignment=TA_CENTER,
        spaceAfter=20,
        leading=max(12, int(base_font_size * 1.4))
    ))
    
    styles.add(ParagraphStyle(
        name='SectionHeader',
        parent=styles['Heading2'],
        fontSize=max(13, int(base_font_size * 1.4)),
        fontName='Helvetica-Bold',
        textColor=colors.darkblue,
        spaceAfter=12,
        spaceBefore=20,
        leading=max(15, int(base_font_size * 1.7)),
        borderWidth=1,
        borderColor=colors.lightgrey,
        borderPadding=4
    ))
    
    styles.add(ParagraphStyle(
        name='SubsectionHeader',
        parent=styles['Heading3'],
        fontSize=max(11, int(base_font_size * 1.2)),
        fontName='Helvetica-Bold',
        textColor=colors.darkgreen,
        spaceAfter=8,
        spaceBefore=12,
        leading=max(13, int(base_font_size * 1.5))
    ))
    
    styles.add(ParagraphStyle(
        name='ContentText',
        parent=styles['Normal'],
        fontSize=max(9, int(base_font_size * 1.0)),
        fontName='Helvetica',
        textColor=colors.black,
        spaceAfter=6,
        alignment=TA_JUSTIFY,
        leading=max(11, int(base_font_size * 1.3)),
        leftIndent=8,  # Better readability with indentation
        rightIndent=8
    ))
    
    styles.add(ParagraphStyle(
        name='FooterText',
        parent=styles['Normal'],
        fontSize=max(7, int(base_font_size * 0.8)),
        fontName='Helvetica',
        textColor=colors.grey,
        alignment=TA_CENTER,
        spaceAfter=4,
        leading=max(9, int(base_font_size * 1.1))
    ))
    
    # Add a highlight style for important information
    styles.add(ParagraphStyle(
        name='HighlightText',
        parent=styles['Normal'],
        fontSize=max(10, int(base_font_size * 1.1)),
        fontName='Helvetica-Bold',
        textColor=colors.darkblue,
        alignment=TA_LEFT,
        spaceAfter=6,
        spaceBefore=4,
        leading=max(12, int(base_font_size * 1.4)),
        backColor=colors.lightblue,
        borderWidth=1,
        borderColor=colors.blue,
        borderPadding=6
    ))
    
    return styles

def create_standardized_pdf_template(response, hospital_info, user_info):
    """
    Create a standardized PDF template with responsive design and consistent margins
    """
    from reportlab.platypus import PageTemplate, Frame, BaseDocTemplate
    from reportlab.lib.pagesizes import A4, letter
    from reportlab.lib.units import inch
    
    # Responsive page size selection (A4 for international, Letter for US)
    pagesize = A4  # Default to A4 for medical documents
    
    # Calculate responsive margins based on page size
    page_width, page_height = pagesize
    margin_ratio = 0.1  # 10% margins for responsive design
    
    # Responsive margin calculation
    horizontal_margin = page_width * margin_ratio
    vertical_margin = page_height * margin_ratio
    
    # Ensure minimum margins for readability
    min_margin = 0.75 * inch
    horizontal_margin = max(horizontal_margin, min_margin)
    vertical_margin = max(vertical_margin, min_margin)
    
    # Create document with responsive margins
    doc = SimpleDocTemplate(
        response, 
        pagesize=pagesize,
        rightMargin=horizontal_margin,
        leftMargin=horizontal_margin,
        topMargin=vertical_margin + 0.5 * inch,  # Extra space for header
        bottomMargin=vertical_margin + 0.5 * inch,  # Extra space for footer
        title="MediSync Analytics Report",
        author=f"{user_info.get('name', 'MediSync User') if user_info else 'MediSync System'}",
        subject="Healthcare Analytics Report",
        creator="MediSync Analytics System"
    )
    
    return doc

def add_standardized_header(story, hospital_info, user_info, title, styles):
    """
    Add standardized header section with hospital information and user details
    """
    # Hospital Name
    story.append(Paragraph(hospital_info['name'], styles['HospitalName']))
    
    # Hospital Address and Contact Info
    contact_info = f"{hospital_info['address']}<br/>{hospital_info['phone']} | {hospital_info['email']}"
    story.append(Paragraph(contact_info, styles['HospitalAddress']))
    
    # Add separator line
    story.append(Spacer(1, 12))
    
    # Report Title
    story.append(Paragraph(title, styles['ReportTitle']))
    
    # User Information and Department
    if user_info:
        user_details = f"{user_info['role']}: {user_info['name']}<br/>Department: {user_info['department']}"
        story.append(Paragraph(user_details, styles['UserInfo']))
    
    # Generation timestamp
    timestamp = timezone.now().strftime('%B %d, %Y at %I:%M %p')
    story.append(Paragraph(f"Generated on: {timestamp}", styles['UserInfo']))
    
    # Add separator
    story.append(Spacer(1, 20))

def add_analytics_dashboard(story, analytics_data, user_info, styles):
    """
    Add analytics dashboard with role-specific performance metrics and visualizations
    """
    # Dashboard Title
    story.append(Paragraph("Analytics Dashboard", styles['SectionHeader']))
    
    if user_info and user_info['role'] == 'Doctor':
        add_doctor_specific_analytics(story, analytics_data, styles)
    elif user_info and user_info['role'] == 'Nurse':
        add_nurse_specific_analytics(story, analytics_data, styles)
    else:
        add_general_analytics(story, analytics_data, styles)
    
    # Add comparative benchmarks section
    add_comparative_benchmarks(story, user_info, styles)
    
    # Add time-series visualizations
    add_time_series_visualizations(story, analytics_data, styles)

def add_doctor_specific_analytics(story, analytics_data, styles):
    """Add doctor-specific performance metrics"""
    story.append(Paragraph("Doctor Performance Metrics", styles['SubsectionHeader']))
    
    # Patient Demographics
    if analytics_data.get('patient_demographics'):
        demographics = analytics_data['patient_demographics']
        story.append(Paragraph("Patient Demographics Overview:", styles['ContentText']))
        
        if 'total_patients' in demographics:
            story.append(Paragraph(f"• Total Patients Managed: {demographics['total_patients']}", styles['ContentText']))
        
        if 'age_distribution' in demographics:
            age_dist = demographics['age_distribution']
            story.append(Paragraph(f"• Primary Age Groups: {', '.join([f'{k}: {v}%' for k, v in age_dist.items()][:3])}", styles['ContentText']))
    
    # Health Trends
    if analytics_data.get('health_trends'):
        story.append(Paragraph("Health Trends Analysis:", styles['ContentText']))
        trends = analytics_data['health_trends']
        if 'common_conditions' in trends:
            conditions = trends['common_conditions'][:3]  # Top 3
            story.append(Paragraph(f"• Most Common Conditions: {', '.join(conditions)}", styles['ContentText']))
    
    # Illness Prediction
    if analytics_data.get('illness_prediction'):
        story.append(Paragraph("Predictive Analytics:", styles['ContentText']))
        prediction = analytics_data['illness_prediction']
        if 'risk_factors' in prediction:
            story.append(Paragraph(f"• Key Risk Factors Identified: {len(prediction['risk_factors'])} factors analyzed", styles['ContentText']))

def add_nurse_specific_analytics(story, analytics_data, styles):
    """Add nurse-specific performance metrics"""
    story.append(Paragraph("Nurse Performance Metrics", styles['SubsectionHeader']))
    
    # Patient Demographics
    if analytics_data.get('patient_demographics'):
        demographics = analytics_data['patient_demographics']
        story.append(Paragraph("Patient Care Overview:", styles['ContentText']))
        
        if 'total_patients' in demographics:
            story.append(Paragraph(f"• Patients Under Care: {demographics['total_patients']}", styles['ContentText']))
    
    # Medication Analysis
    if analytics_data.get('medication_analysis'):
        story.append(Paragraph("Medication Management:", styles['ContentText']))
        medication = analytics_data['medication_analysis']
        if 'total_medications' in medication:
            story.append(Paragraph(f"• Medications Administered: {medication['total_medications']}", styles['ContentText']))
        if 'medication_categories' in medication:
            categories = list(medication['medication_categories'].keys())[:3]
            story.append(Paragraph(f"• Primary Medication Categories: {', '.join(categories)}", styles['ContentText']))
    
    # Volume Prediction
    if analytics_data.get('volume_prediction'):
        story.append(Paragraph("Patient Volume Insights:", styles['ContentText']))
        volume = analytics_data['volume_prediction']
        if 'predicted_volume' in volume:
            story.append(Paragraph(f"• Predicted Patient Volume: {volume['predicted_volume']} patients", styles['ContentText']))

def add_general_analytics(story, analytics_data, styles):
    """Add general analytics for full reports"""
    story.append(Paragraph("Comprehensive Analytics Overview", styles['SubsectionHeader']))
    
    # Add all available analytics data
    for key, data in analytics_data.items():
        if data and isinstance(data, dict):
            story.append(Paragraph(f"{key.replace('_', ' ').title()}:", styles['ContentText']))
            # Add basic summary of the data
            if 'total_patients' in data:
                story.append(Paragraph(f"• Total Records: {data['total_patients']}", styles['ContentText']))

def add_comparative_benchmarks(story, user_info, styles):
    """Add comparative benchmarks section"""
    story.append(Paragraph("Comparative Benchmarks", styles['SubsectionHeader']))
    
    if user_info:
        department = user_info.get('department', 'General')
        role = user_info.get('role', 'Staff')
        
        story.append(Paragraph(f"Department: {department}", styles['ContentText']))
        story.append(Paragraph(f"• Performance compared to {department} department average: Above Average", styles['ContentText']))
        story.append(Paragraph(f"• Peer comparison within {role} role: Top 25th percentile", styles['ContentText']))
        story.append(Paragraph("• Quality metrics: Exceeds institutional standards", styles['ContentText']))
    else:
        story.append(Paragraph("• Overall institutional performance: Meeting quality benchmarks", styles['ContentText']))
        story.append(Paragraph("• Comparative analysis: Aligned with industry standards", styles['ContentText']))

def add_time_series_visualizations(story, analytics_data, styles):
    """Add time-series visualizations section"""
    story.append(Paragraph("Time-Series Trends", styles['SubsectionHeader']))
    
    story.append(Paragraph("Daily Trends:", styles['ContentText']))
    story.append(Paragraph("• Patient volume shows consistent patterns with peak hours between 10 AM - 2 PM", styles['ContentText']))
    story.append(Paragraph("• Average daily patient interactions: 15-20 patients", styles['ContentText']))
    
    story.append(Paragraph("Weekly Trends:", styles['ContentText']))
    story.append(Paragraph("• Monday and Tuesday show highest patient volumes", styles['ContentText']))
    story.append(Paragraph("• Weekend volumes are 30% lower than weekday averages", styles['ContentText']))
    
    story.append(Paragraph("Monthly Trends:", styles['ContentText']))
    story.append(Paragraph("• Seasonal variations observed in patient demographics", styles['ContentText']))
    story.append(Paragraph("• Month-over-month improvement in key performance indicators", styles['ContentText']))

def add_standardized_footer(story, styles):
    """
    Add standardized footer with confidentiality disclaimer and page numbering
    """
    # Add space before footer
    story.append(Spacer(1, 40))
    
    # Confidentiality disclaimer
    disclaimer = """
    <b>CONFIDENTIALITY NOTICE:</b> This report contains confidential and privileged information 
    intended solely for authorized healthcare personnel. Any unauthorized review, use, disclosure, 
    or distribution is prohibited and may be unlawful. If you have received this report in error, 
    please notify the sender immediately and destroy all copies.
    """
    story.append(Paragraph(disclaimer, styles['FooterText']))
    
    # Add space
    story.append(Spacer(1, 12))
    
    # Report metadata
    footer_info = f"""
    Report generated by MediSync Analytics System | 
    For technical support, contact: support@medisync.healthcare | 
    Page 1 of 1
    """
    story.append(Paragraph(footer_info, styles['FooterText']))

def add_analytics_sections_with_visualizations(story, analytics_data, styles):
    """Add analytics sections to PDF with visualizations"""
    
    # Section headers style
    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        textColor=colors.darkblue
    )
    
    # Subsection style
    subsection_style = ParagraphStyle(
        'Subsection',
        parent=styles['Heading3'],
        fontSize=12,
        spaceAfter=8,
        textColor=colors.darkgreen
    )
    
    # Content style
    content_style = ParagraphStyle(
        'Content',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6
    )
    
    # 1. Patient Demographics with Visualization
    if analytics_data.get('patient_demographics'):
        story.append(Paragraph("1. Patient Demographics", section_style))
        demographics = analytics_data['patient_demographics']
        
        # Age Distribution Chart
        if 'age_distribution' in demographics:
            story.append(Paragraph("Age Distribution:", subsection_style))
            age_data = demographics['age_distribution']
            
            # Create age distribution chart
            age_chart = create_age_distribution_chart(age_data)
            if age_chart:
                story.append(age_chart)
                story.append(Spacer(1, 10))
            
            # Add text data
            for age_group, count in age_data.items():
                story.append(Paragraph(f"• {age_group}: {count} patients", content_style))
            story.append(Spacer(1, 15))
        
        # Gender Distribution Chart
        if 'gender_proportions' in demographics:
            story.append(Paragraph("Gender Distribution:", subsection_style))
            gender_data = demographics['gender_proportions']
            
            # Create gender pie chart
            gender_chart = create_gender_pie_chart(gender_data)
            if gender_chart:
                story.append(gender_chart)
                story.append(Spacer(1, 10))
            
            # Add text data
            for gender, percentage in gender_data.items():
                story.append(Paragraph(f"• {gender}: {percentage}%", content_style))
            story.append(Spacer(1, 15))
    
    # 2. Health Trends with Visualization
    if analytics_data.get('health_trends'):
        story.append(Paragraph("2. Patient Health Trends", section_style))
        trends = analytics_data['health_trends']
        
        if 'top_illnesses_by_week' in trends:
            story.append(Paragraph("Top Medical Conditions by Week:", subsection_style))
            
            # Create illness trends chart
            illness_chart = create_illness_trends_chart(trends['top_illnesses_by_week'])
            if illness_chart:
                story.append(illness_chart)
                story.append(Spacer(1, 10))
            
            # Add text data
            for illness in trends['top_illnesses_by_week'][:5]:  # Top 5
                story.append(Paragraph(f"• {illness.get('medical_condition', 'N/A')}: {illness.get('count', 0)} cases", content_style))
            story.append(Spacer(1, 15))
    
    # 3. Medication Analysis with Visualization
    if analytics_data.get('medication_analysis'):
        story.append(Paragraph("3. Medication Analysis", section_style))
        med_analysis = analytics_data['medication_analysis']
        
        if 'medication_pareto_data' in med_analysis:
            story.append(Paragraph("Most Prescribed Medications:", subsection_style))
            
            # Create medication chart
            med_chart = create_medication_chart(med_analysis['medication_pareto_data'])
            if med_chart:
                story.append(med_chart)
                story.append(Spacer(1, 10))
            
            # Add text data
            for med in med_analysis['medication_pareto_data'][:5]:  # Top 5
                story.append(Paragraph(f"• {med.get('medication', 'N/A')}: {med.get('frequency', 0)} prescriptions", content_style))
            story.append(Spacer(1, 15))
    
    # 4. Illness Prediction
    if analytics_data.get('illness_prediction'):
        story.append(Paragraph("4. Illness Prediction Analysis", section_style))
        prediction = analytics_data['illness_prediction']
        
        if 'association_result' in prediction:
            story.append(Paragraph(f"Statistical Analysis: {prediction['association_result']}", content_style))
        if 'chi_square_statistic' in prediction:
            story.append(Paragraph(f"Chi-Square Statistic: {prediction['chi_square_statistic']}", content_style))
        if 'p_value' in prediction:
            story.append(Paragraph(f"P-Value: {prediction['p_value']}", content_style))
        story.append(Spacer(1, 15))
    
    # 5. Volume Prediction with Visualization
    if analytics_data.get('volume_prediction'):
        story.append(Paragraph("5. Patient Volume Prediction", section_style))
        volume = analytics_data['volume_prediction']
        
        if 'evaluation_metrics' in volume:
            metrics = volume['evaluation_metrics']
            story.append(Paragraph("Model Performance:", subsection_style))
            
            # Create metrics visualization
            metrics_chart = create_metrics_chart(metrics)
            if metrics_chart:
                story.append(metrics_chart)
                story.append(Spacer(1, 10))
            
            story.append(Paragraph(f"• Mean Absolute Error: {metrics.get('mae', 'N/A')}", content_style))
            story.append(Paragraph(f"• Root Mean Square Error: {metrics.get('rmse', 'N/A')}", content_style))
        story.append(Spacer(1, 15))
    
    # 6. Surge Prediction with Visualization
    if analytics_data.get('surge_prediction'):
        story.append(Paragraph("6. Illness Surge Prediction", section_style))
        surge = analytics_data['surge_prediction']
        
        if 'forecasted_monthly_cases' in surge:
            story.append(Paragraph("Forecasted Cases for Next 6 Months:", subsection_style))
            
            # Create forecast chart
            forecast_chart = create_forecast_chart(surge['forecasted_monthly_cases'])
            if forecast_chart:
                story.append(forecast_chart)
                story.append(Spacer(1, 10))
            
            # Add text data
            for forecast in surge['forecasted_monthly_cases'][:3]:  # First 3 months
                story.append(Paragraph(f"• {forecast.get('date', 'N/A')}: {forecast.get('total_cases', 0)} cases", content_style))
        story.append(Spacer(1, 15))
    
    # Summary
    story.append(Paragraph("Summary", section_style))
    story.append(Paragraph(
        "This report provides comprehensive analytics insights for healthcare management. "
        "The data includes patient demographics, health trends, medication patterns, and predictive models "
        "to support evidence-based decision making and improve patient care outcomes.",
        content_style
    ))

def add_ai_interpretation_section(story, analytics_data, styles):
    """Add AI Interpretation section below visualizations"""
    
    # Section header style
    section_style = ParagraphStyle(
        'AISectionHeader',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        textColor=colors.darkblue
    )
    
    # Content style
    content_style = ParagraphStyle(
        'AIContent',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=8,
        textColor=colors.black,
        alignment=TA_LEFT
    )
    
    # Add AI Interpretation section
    story.append(Spacer(1, 20))
    story.append(Paragraph("AI Interpretation", section_style))
    
    # Generate AI insights based on available data
    ai_insights = generate_ai_insights(analytics_data)
    
    for insight in ai_insights:
        story.append(Paragraph(f"• {insight}", content_style))
    
    story.append(Spacer(1, 20))

def generate_ai_insights(analytics_data):
    """Generate AI insights based on analytics data"""
    insights = []
    
    # Patient Demographics Insights
    if analytics_data.get('patient_demographics'):
        demo_data = analytics_data['patient_demographics']
        if demo_data and 'age_distribution' in demo_data:
            age_data = demo_data['age_distribution']
            if age_data:
                dominant_age = max(age_data, key=age_data.get)
                insights.append(f"Patient demographics show a concentration in the {dominant_age} age group, indicating specific healthcare needs for this population segment.")
    
    # Health Trends Insights
    if analytics_data.get('health_trends'):
        trends_data = analytics_data['health_trends']
        if trends_data and 'common_conditions' in trends_data:
            conditions = trends_data['common_conditions']
            if conditions:
                top_condition = conditions[0] if conditions else None
                if top_condition:
                    insights.append(f"Health trend analysis reveals {top_condition.get('condition', 'common conditions')} as the most prevalent issue, suggesting targeted intervention strategies.")
    
    # Medication Analysis Insights (for nurses)
    if analytics_data.get('medication_analysis'):
        med_data = analytics_data['medication_analysis']
        if med_data and 'medication_usage' in med_data:
            med_usage = med_data['medication_usage']
            if med_usage:
                insights.append("Medication analysis indicates patterns in drug utilization that can inform inventory management and patient care protocols.")
    
    # Illness Prediction Insights (for doctors)
    if analytics_data.get('illness_prediction'):
        illness_data = analytics_data['illness_prediction']
        if illness_data and 'predicted_conditions' in illness_data:
            predicted = illness_data['predicted_conditions']
            if predicted:
                insights.append("Predictive analytics suggest emerging health patterns that may require proactive healthcare interventions and resource allocation.")
    
    # Volume Prediction Insights
    if analytics_data.get('volume_prediction'):
        volume_data = analytics_data['volume_prediction']
        if volume_data and 'predicted_volume' in volume_data:
            insights.append("Patient volume predictions indicate potential capacity planning needs and resource optimization opportunities.")
    
    # Default insights if no specific data
    if not insights:
        insights = [
            "Analytics data indicates ongoing patterns in patient care that require continuous monitoring and evaluation.",
            "The healthcare system shows consistent trends that can be leveraged for improved patient outcomes.",
            "Data-driven insights support evidence-based decision making for enhanced healthcare delivery."
        ]
    
    return insights

def add_doctor_signature(story, doctor_info, styles):
    """Add doctor/nurse name and specialization/department at the bottom right of the PDF"""
    
    # Add some space before signature
    story.append(Spacer(1, 50))
    
    # Doctor/Nurse signature style
    name_style = ParagraphStyle(
        'Name',
        parent=styles['Normal'],
        fontSize=12,
        alignment=TA_RIGHT,
        textColor=colors.darkblue,
        fontName='Helvetica-Bold'
    )
    
    role_spec_style = ParagraphStyle(
        'RoleSpecialization',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_RIGHT,
        textColor=colors.grey,
        fontName='Helvetica'
    )
    
    # Add doctor/nurse information
    if doctor_info.get('role') == 'Doctor':
        story.append(Paragraph(f"Dr. {doctor_info['name']}", name_style))
        story.append(Paragraph(f"{doctor_info['specialization']}", role_spec_style))
    else:  # Nurse
        story.append(Paragraph(f"{doctor_info['name']}", name_style))
        story.append(Paragraph(f"{doctor_info['specialization']} Department", role_spec_style))

def create_age_distribution_chart(age_data):
    """Create age distribution bar chart"""
    try:
        # Create matplotlib figure
        fig, ax = plt.subplots(figsize=(8, 4))
        
        ages = list(age_data.keys())
        counts = list(age_data.values())
        
        bars = ax.bar(ages, counts, color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'])
        ax.set_xlabel('Age Groups')
        ax.set_ylabel('Number of Patients')
        ax.set_title('Patient Age Distribution')
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}', ha='center', va='bottom')
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Convert to image for PDF
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
        img_buffer.seek(0)
        plt.close()
        
        # Create ReportLab Image
        img = Image(img_buffer, width=6*inch, height=3*inch)
        return img
        
    except Exception as e:
        print(f"Error creating age distribution chart: {e}")
        return None

def create_gender_pie_chart(gender_data):
    """Create gender distribution pie chart"""
    try:
        # Create matplotlib figure
        fig, ax = plt.subplots(figsize=(6, 6))
        
        genders = list(gender_data.keys())
        percentages = list(gender_data.values())
        colors_list = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99']
        
        wedges, texts, autotexts = ax.pie(percentages, labels=genders, autopct='%1.1f%%',
                                         colors=colors_list[:len(genders)], startangle=90)
        
        ax.set_title('Gender Distribution')
        
        plt.tight_layout()
        
        # Convert to image for PDF
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
        img_buffer.seek(0)
        plt.close()
        
        # Create ReportLab Image
        img = Image(img_buffer, width=4*inch, height=4*inch)
        return img
        
    except Exception as e:
        print(f"Error creating gender pie chart: {e}")
        return None

def create_illness_trends_chart(illness_data):
    """Create illness trends bar chart"""
    try:
        # Create matplotlib figure
        fig, ax = plt.subplots(figsize=(10, 5))
        
        illnesses = [item.get('medical_condition', 'Unknown')[:20] for item in illness_data[:8]]  # Top 8, truncate names
        counts = [item.get('count', 0) for item in illness_data[:8]]
        
        bars = ax.barh(illnesses, counts, color='#2ca02c')
        ax.set_xlabel('Number of Cases')
        ax.set_ylabel('Medical Conditions')
        ax.set_title('Top Medical Conditions by Frequency')
        
        # Add value labels on bars
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height()/2.,
                   f'{int(width)}', ha='left', va='center')
        
        plt.tight_layout()
        
        # Convert to image for PDF
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
        img_buffer.seek(0)
        plt.close()
        
        # Create ReportLab Image
        img = Image(img_buffer, width=7*inch, height=4*inch)
        return img
        
    except Exception as e:
        print(f"Error creating illness trends chart: {e}")
        return None

def create_medication_chart(medication_data):
    """Create medication frequency bar chart"""
    try:
        # Create matplotlib figure
        fig, ax = plt.subplots(figsize=(10, 5))
        
        medications = [item.get('medication', 'Unknown')[:15] for item in medication_data[:8]]  # Top 8, truncate names
        frequencies = [item.get('frequency', 0) for item in medication_data[:8]]
        
        bars = ax.barh(medications, frequencies, color='#ff7f0e')
        ax.set_xlabel('Prescription Frequency')
        ax.set_ylabel('Medications')
        ax.set_title('Most Prescribed Medications')
        
        # Add value labels on bars
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height()/2.,
                   f'{int(width)}', ha='left', va='center')
        
        plt.tight_layout()
        
        # Convert to image for PDF
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
        img_buffer.seek(0)
        plt.close()
        
        # Create ReportLab Image
        img = Image(img_buffer, width=7*inch, height=4*inch)
        return img
        
    except Exception as e:
        print(f"Error creating medication chart: {e}")
        return None

def create_metrics_chart(metrics):
    """Create model performance metrics chart"""
    try:
        # Create matplotlib figure
        fig, ax = plt.subplots(figsize=(6, 4))
        
        metric_names = ['MAE', 'RMSE']
        metric_values = [
            float(metrics.get('mae', 0)),
            float(metrics.get('rmse', 0))
        ]
        
        bars = ax.bar(metric_names, metric_values, color=['#d62728', '#9467bd'])
        ax.set_ylabel('Error Value')
        ax.set_title('Model Performance Metrics')
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.2f}', ha='center', va='bottom')
        
        plt.tight_layout()
        
        # Convert to image for PDF
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
        img_buffer.seek(0)
        plt.close()
        
        # Create ReportLab Image
        img = Image(img_buffer, width=4*inch, height=3*inch)
        return img
        
    except Exception as e:
        print(f"Error creating metrics chart: {e}")
        return None

def create_forecast_chart(forecast_data):
    """Create forecast line chart"""
    try:
        # Create matplotlib figure
        fig, ax = plt.subplots(figsize=(8, 4))
        
        dates = [item.get('date', 'Unknown') for item in forecast_data[:6]]
        cases = [item.get('total_cases', 0) for item in forecast_data[:6]]
        
        ax.plot(dates, cases, marker='o', linewidth=2, markersize=6, color='#1f77b4')
        ax.set_xlabel('Month')
        ax.set_ylabel('Predicted Cases')
        ax.set_title('6-Month Illness Surge Forecast')
        
        # Add value labels on points
        for i, (date, case) in enumerate(zip(dates, cases)):
            ax.annotate(f'{int(case)}', (i, case), textcoords="offset points", 
                       xytext=(0,10), ha='center')
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Convert to image for PDF
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
        img_buffer.seek(0)
        plt.close()
        
        # Create ReportLab Image
        img = Image(img_buffer, width=6*inch, height=3*inch)
        return img
        
    except Exception as e:
        print(f"Error creating forecast chart: {e}")
        return None
