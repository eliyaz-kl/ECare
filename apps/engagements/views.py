from django.shortcuts import render, get_object_or_404

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from .models import Engagement
# Create your views here.



@login_required
def dashboard(request):

    total_engagements = Engagement.objects.count()

    pending_engagements = Engagement.objects.filter(
        status='NEW'
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

    engagements = engagements.order_by(
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


def inbox(request):

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

    engagements = engagements.order_by(
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
        'engagements/inbox.html',
        {
            'engagements': page_obj,
            'page_obj': page_obj,
            'current_type': engagement_type,
            'current_type_label': engagement_type_labels.get(
                engagement_type,
                'All'
            ),
        }
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
