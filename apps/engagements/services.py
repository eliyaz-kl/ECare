import json
from urllib import error, request

from django.conf import settings

from .models import Engagement


class EngagementCategorizationError(Exception):
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


def _post_json(url, payload):
    data = json.dumps(payload).encode('utf-8')
    http_request = request.Request(
        url,
        data=data,
        headers={'Content-Type': 'application/json'},
        method='POST',
    )

    try:
        with request.urlopen(http_request, timeout=settings.LOCAL_LLM_TIMEOUT) as response:
            return json.loads(response.read().decode('utf-8'))
    except (error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise EngagementCategorizationError(
            f'Local LLM request failed: {exc}'
        ) from exc


def _extract_category(raw_response):
    content = raw_response.get('message', {}).get('content')

    if not content:
        choices = raw_response.get('choices') or []
        if choices:
            content = choices[0].get('message', {}).get('content')

    if not content:
        raise EngagementCategorizationError('Local LLM response did not include content.')

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        parsed = {'category': content.strip()}

    category = parsed.get('category', '').strip()

    if not category:
        raise EngagementCategorizationError('Local LLM response did not include a category.')

    return category
