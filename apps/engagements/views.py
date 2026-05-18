from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils import timezone

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q

from .models import Engagement
# Create your views here.


def _get_per_page(request, default=25, maximum=100):
    try:
        per_page = int(request.GET.get('per_page', default))
    except (TypeError, ValueError):
        per_page = default

    return max(1, min(per_page, maximum))


def _format_sla_remaining(engagement):
    if not engagement.sla:
        return '00:00'

    remaining = engagement.sla - timezone.now()
    total_minutes = max(0, int(remaining.total_seconds() // 60))
    hours, minutes = divmod(total_minutes, 60)

    return f'{hours:02d}:{minutes:02d}'


def _serialize_engagements_for_grid(engagements):
    rows = []

    for engagement in engagements:
        customer = engagement.customer
        rows.append({
            'request_number': f'#{engagement.request_number}',
            'ticket_id': f'#{engagement.id}',
            'customer_name': customer.display_name or customer.username,
            'subject': engagement.content,
            'priority': engagement.priority,
            'source': customer.get_platform_display(),
            'source_type': 'Private' if engagement.engagement_type == 'DM' else 'Public',
            'request_type': engagement.get_engagement_type_display(),
            'creation_time': engagement.created_at.strftime('%Y-%m-%d %H:%M'),
            'status': engagement.status,
            'last_update': engagement.updated_at.strftime('%Y-%m-%d %H:%M'),
            'sla_remaining': _format_sla_remaining(engagement),
            'detail_url': reverse('engagement_detail', args=[engagement.id]),
        })

    return rows



@login_required
def dashboard(request):

    total_engagements = Engagement.objects.count()

    pending_engagements = Engagement.objects.filter(
        status='NEW',

    ).count()

    if not request.user.is_authenticated:
        return render(
            request,
            'engagements/inbox.html',
            {
                'engagements': []
            }
        )

    engagement_type = request.GET.get('type')
    engagements = Engagement.objects.select_related(
        'customer',
        'assigned_agent'
    )

    if engagement_type:
        engagements = engagements.filter(
            engagement_type=engagement_type
        )

    engagements = engagements.filter(
        engagement_type='DM'
    ).order_by(
        '-created_at'
    )
    paginator = Paginator(engagements, 5)
    page_obj = paginator.get_page(request.GET.get('page'))

    engagement_type_labels = {
        'DM': 'DMs',
        'MENTION': 'Mentions',
        'POST_REPLY': 'Replies',
    }

    return render(
            request,
            'engagements/dashboard.html',
            {
                'total_engagements': total_engagements,
                'pending_engagements': pending_engagements,
                'engagements': page_obj,
                'page_obj': page_obj,
                'current_type': engagement_type,
                'current_type_label': engagement_type_labels.get(
                    engagement_type,
                    'All'
                ),
            }
        )


def _render_engagement_grid(request, engagements, page_title, list_url_name):

    engagement_type = request.GET.get('type')
    search_query = request.GET.get('q', '').strip()

    if engagement_type:
        engagements = engagements.filter(
            engagement_type=engagement_type
        )

    if search_query:
        engagements = engagements.filter(
            Q(external_id__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(category__icontains=search_query) |
            Q(customer__username__icontains=search_query) |
            Q(customer__display_name__icontains=search_query)
        )

    engagements = engagements.order_by(
        '-created_at'
    )
    per_page = _get_per_page(request)
    paginator = Paginator(engagements, per_page)
    page_obj = paginator.get_page(request.GET.get('page'))
    query_params = request.GET.copy()
    query_params.pop('page', None)
    page_query_prefix = query_params.urlencode()

    engagement_type_labels = {
        'DM': 'DMs',
        'MENTION': 'Mentions',
        'POST_REPLY': 'Replies',
    }

    return render(
        request,
        'engagements/inbox.html',
        {
            'engagements': page_obj,
            'inbox_rows': _serialize_engagements_for_grid(page_obj),
            'page_obj': page_obj,
            'page_range': paginator.get_elided_page_range(
                page_obj.number,
                on_each_side=2,
                on_ends=1,
            ),
            'current_type': engagement_type,
            'current_query': search_query,
            'per_page': per_page,
            'page_title': page_title,
            'list_url_name': list_url_name,
            'page_query_prefix': f'{page_query_prefix}&' if page_query_prefix else '',
            'current_type_label': engagement_type_labels.get(
                engagement_type,
                'All'
            ),
        }
    )


def inbox(request):

    if not request.user.is_authenticated:
        return render(
            request,
            'engagements/inbox.html',
            {
                'engagements': []
            }
        )

    engagements = Engagement.objects.select_related(
        'customer',
        'assigned_agent',
    ).exclude(status='CLOSED')


    return _render_engagement_grid(
        request,
        engagements,
        'Active Request',
        'inbox'
    )


@login_required
def assigned(request):
    engagements = Engagement.objects.select_related(
        'customer',
        'assigned_agent'
    ).filter(
        assigned_agent=request.user,
        status='ASSIGNED'
    )

    return _render_engagement_grid(
        request,
        engagements,
        'Assigned Request',
        'assigned'
    )


@login_required
def resolved(request):
    engagements = Engagement.objects.select_related(
        'customer',
        'assigned_agent'
    ).filter(
        status='CLOSED'
    )

    if not request.user.is_staff and not request.user.is_superuser:
        engagements = engagements.filter(
            assigned_agent=request.user
        )

    return _render_engagement_grid(
        request,
        engagements,
        'Resolved Request',
        'resolved'
    )


@login_required
def engagement_detail(request, pk):

    engagement = get_object_or_404(
        Engagement,
        pk=pk
    )

    if request.method == 'POST':

        final_response = request.POST.get(
            'final_response'
        )

        engagement.final_response = final_response

        engagement.save()

    return render(
        request,
        'engagements/engagement_detail.html',
        {
            'engagement': engagement
        }
    )
