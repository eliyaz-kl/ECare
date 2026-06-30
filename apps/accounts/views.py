from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json
from .models import User
from .serializers import UserCreateSerializer, UserSerializer


@login_required
def create_user(request):
    """
    View to handle the creation of a new user.
    """
    from django.contrib.auth.models import Group

    if request.method == 'POST':
        serializer = UserCreateSerializer(data=request.POST)
        if serializer.is_valid():
            user = serializer.save()

            # Assign group if provided
            group_name = request.POST.get('user_group')
            if group_name:
                try:
                    group = Group.objects.get(name=group_name)
                    user.groups.add(group)
                except Group.DoesNotExist:
                    messages.warning(request, f'Group "{group_name}" not found.')

            # Save channels if provided
            channels = request.POST.get('channels', '')
            if channels:
                user.channels = channels
                user.save()

            messages.success(request, 'User created successfully!')
            return redirect('users-list')
        else:
            for field, errors in serializer.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')

    # Get all groups to pass to template
    groups = Group.objects.all()
    return render(request, 'admin/create-user.html', {'groups': groups})

@login_required
@require_http_methods(["GET"])
def get_user_details(request, user_id):
    """
    API endpoint to get user details by ID.
    """
    user = get_object_or_404(User, id=user_id)
    serializer = UserSerializer(user)
    return JsonResponse(serializer.data)


@login_required
@require_http_methods(["POST"])
def update_current_user_status(request):
    """
    API endpoint to update the logged-in user's availability status.
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON payload.'
        }, status=400)

    status = data.get('status')
    valid_statuses = {value for value, _label in User.Status.choices}

    if status not in valid_statuses:
        return JsonResponse({
            'success': False,
            'message': 'Invalid status.'
        }, status=400)

    request.user.current_status = status
    request.user.save(update_fields=['current_status', 'status_updated_at'])

    return JsonResponse({
        'success': True,
        'status': request.user.current_status,
        'label': request.user.get_current_status_display(),
    })

@login_required
@require_http_methods(["POST", "PUT"])
def edit_user_details(request, user_id):
    """
    API endpoint to edit user details.
    """
    user = get_object_or_404(User, id=user_id)

    try:
        data = json.loads(request.body)

        # Update user fields
        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        user.email = data.get('email', user.email)
        user.username = data.get('username', user.username)
        user.group = data.get('group', user.group)

        # Update password if provided
        if data.get('password'):
            user.set_password(data['password'])

        user.save()

        return JsonResponse({
            'success': True,
            'message': 'User updated successfully!'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)

@login_required
@require_http_methods(["DELETE", "POST"])
def delete_user(request, user_id):
    """
    API endpoint to delete a user.
    """
    user = get_object_or_404(User, id=user_id)

    try:
        username = user.username
        user.delete()
        return JsonResponse({
            'success': True,
            'message': f'User {username} deleted successfully!'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


@login_required
def users_list(request):
    """
    View to display the list of all users.
    """
    users = User.objects.all().order_by('-date_joined')

    context = {
        'users': users,
        'total_users': users.count(),
        'active_users': users.filter(is_active=True).count(),
        'suspended_users': users.filter(is_active=False).count(),
    }

    return render(request, 'admin/users-list.html', context)


@login_required
def users_api(request):
    """
    API endpoint to fetch users data for AG Grid.
    """
    users = User.objects.prefetch_related('groups').all().order_by('-date_joined')
    serializer = UserSerializer(users, many=True)

    # Format data for AG Grid
    formatted_data = []
    for user in serializer.data:
        formatted_data.append({
            'id': user['id'],
            'Full Name': f"{user.get('first_name', '')} {user.get('last_name', '')}".strip() or user['username'],
            'User Name': user['username'],
            'Email': user['email'],
            'Status': 'Active' if user['is_active'] else 'Inactive',
            'Group': user.get('groups', 'No Group'),
            'Channels': user.get('channels', '') or 'No Channels',
            'Joined Date': user['date_joined'][:10] if user['date_joined'] else '',
            'Last Active': user['date_joined'][:10] if user['date_joined'] else '',
            'Actions': user['id']  # Pass user ID for actions
        })

    return JsonResponse(formatted_data, safe=False)

@login_required
def manage_groups(request):
    """
    View to display and manage user groups.
    """
    from django.contrib.auth.models import Group

    groups = Group.objects.all().order_by('name')

    context = {
        'groups': groups,
    }

    return render(request, 'admin/manage-groups.html', context)

@login_required
@require_http_methods(["GET"])
def groups_api(request):
    """
    API endpoint to fetch all groups.
    """
    from django.contrib.auth.models import Group

    groups = Group.objects.all().order_by('name')
    groups_data = [{'id': group.id, 'name': group.name} for group in groups]

    return JsonResponse(groups_data, safe=False)

@login_required
@require_http_methods(["POST"])
def create_group(request):
    """
    API endpoint to create a new group.
    """
    from django.contrib.auth.models import Group

    try:
        data = json.loads(request.body)
        group_name = data.get('name', '').strip()

        if not group_name:
            return JsonResponse({
                'success': False,
                'message': 'Group name is required.'
            }, status=400)

        # Check if group already exists
        if Group.objects.filter(name=group_name).exists():
            return JsonResponse({
                'success': False,
                'message': f'Group "{group_name}" already exists.'
            }, status=400)

        # Create new group
        group = Group.objects.create(name=group_name)

        return JsonResponse({
            'success': True,
            'message': f'Group "{group_name}" created successfully!',
            'group': {'id': group.id, 'name': group.name}
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)

@login_required
@require_http_methods(["POST", "DELETE"])
def delete_group(request, group_id):
    """
    API endpoint to delete a group.
    """
    from django.contrib.auth.models import Group

    try:
        group = get_object_or_404(Group, id=group_id)
        group_name = group.name

        # Check if any users are assigned to this group
        user_count = group.user_set.count()
        if user_count > 0:
            return JsonResponse({
                'success': False,
                'message': f'Cannot delete group "{group_name}". {user_count} user(s) are assigned to this group.'
            }, status=400)

        group.delete()

        return JsonResponse({
            'success': True,
            'message': f'Group "{group_name}" deleted successfully!'
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)



