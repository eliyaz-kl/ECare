import json
from urllib import error, request

from django.conf import settings

from .models import Engagement, EngagementMessage


class EngagementCategorizationError(Exception):
    pass


class EngagementAutoReplyError(Exception):
    pass


def categorize_engagement_with_llm(engagement):
    categories = [choice[0] for choice in Engagement.CATEGORY_CHOICES]
    prompt = (
        'Categorize this customer engagement into exactly one of these '
        f'categories: {", ".join(categories)}.\n\n'
        'Return only JSON in this format: {"category": "Category Name"}.\n\n'
        f'Engagement content:\n{engagement.content}'
    )
    payload = {
        'model': settings.LOCAL_LLM_MODEL,
        'messages': [
            {
                'role': 'system',
                'content': (
                    'You classify customer support engagements. Choose only '
                    'one category from the provided list.'
                ),
            },
            {
                'role': 'user',
                'content': prompt,
            },
        ],
        'stream': False,
    }

    raw_response = _post_json(settings.LOCAL_LLM_CHAT_URL, payload)
    category = _extract_category(raw_response)

    if category not in categories:
        raise EngagementCategorizationError(
            f'LLM returned unsupported category: {category}'
        )

    engagement.category = category
    engagement.save(update_fields=['category', 'updated_at'])

    return category


def auto_reply_engagement_with_llm(engagement):
    if engagement.category not in settings.AUTO_REPLY_CATEGORIES:
        return None

    if engagement.is_auto_replied:
        return engagement.final_response or engagement.ai_response

    engagement.status = 'AUTO_REPLY'
    engagement.save(update_fields=['status', 'updated_at'])

    prompt = (
        'Write a concise, warm customer support reply for this engagement. '
        'The customer is sharing appreciation, so thank them sincerely. '
        'Do not promise compensation or create a support ticket. '
        'Return only JSON in this format: {"reply": "Response text"}.\n\n'
        f'Customer name: {engagement.customer.display_name or engagement.customer.username}\n'
        f'Engagement content:\n{engagement.content}'
    )
    payload = {
        'model': settings.LOCAL_LLM_MODEL,
        'messages': [
            {
                'role': 'system',
                'content': (
                    'You draft short, professional customer care replies. '
                    'Use the same language as the customer when clear.'
                ),
            },
            {
                'role': 'user',
                'content': prompt,
            },
        ],
        'stream': False,
    }

    raw_response = _post_json(
        settings.LOCAL_LLM_CHAT_URL,
        payload,
        EngagementAutoReplyError,
    )
    reply = _extract_reply(raw_response)

    engagement.ai_response = reply
    engagement.final_response = reply
    engagement.is_auto_replied = True
    engagement.status = 'CLOSED'
    engagement.save(update_fields=[
        'ai_response',
        'final_response',
        'is_auto_replied',
        'status',
        'updated_at',
    ])

    EngagementMessage.objects.create(
        engagement=engagement,
        sender_type='SYSTEM',
        content=reply,
    )

    return reply


def _post_json(url, payload, exception_class=EngagementCategorizationError):
    data = json.dumps(payload).encode('utf-8')
    http_request = request.Request(
        url,
        data=data,
        headers={'Content-Type': 'application/json'},
        method='POST'
    )

    try:
        with request.urlopen(http_request, timeout=settings.LOCAL_LLM_TIMEOUT) as response:
            return json.loads(response.read().decode('utf-8'))
    except (error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise exception_class(
            f'Local LLM request failed: {exc}'
        ) from exc


def _extract_message_content(raw_response, error_message, exception_class):
    content = raw_response.get('message', {}).get('content')

    if not content:
        choices = raw_response.get('choices') or []
        if choices:
            content = choices[0].get('message', {}).get('content')

    if not content:
        raise exception_class(error_message)

    return content


def _extract_category(raw_response):
    content = _extract_message_content(
        raw_response,
        'Local LLM response did not include content.',
        EngagementCategorizationError,
    )

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        parsed = {'category': content.strip()}

    category = parsed.get('category', '').strip()

    if not category:
        raise EngagementCategorizationError('Local LLM response did not include a category.')

    return category


def _extract_reply(raw_response):
    content = _extract_message_content(
        raw_response,
        'Local LLM response did not include reply content.',
        EngagementAutoReplyError,
    )

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        parsed = {'reply': content.strip()}

    reply = parsed.get('reply', '').strip()

    if not reply:
        raise EngagementAutoReplyError('Local LLM response did not include a reply.')

    return reply
