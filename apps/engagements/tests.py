from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from apps.customers.models import Customer

from .models import Engagement, EngagementMessage
from .services import auto_reply_engagement_with_llm


class AutoReplyWorkflowTests(TestCase):

    def setUp(self):
        self.customer = Customer.objects.create(
            platform='X',
            external_user_id='customer-1',
            username='customer1',
            display_name='Customer One',
        )
        self.engagement = Engagement.objects.create(
            customer=self.customer,
            engagement_type='DM',
            external_id='engagement-1',
            content='Thank you for the excellent service.',
            category='Appreciation',
        )

    @override_settings(AUTO_REPLY_CATEGORIES=['Appreciation'])
    @patch('apps.engagements.services._post_json')
    def test_auto_reply_closes_engagement_and_creates_system_message(self, post_json):
        post_json.return_value = {
            'message': {
                'content': '{"reply": "Thank you for your kind words."}'
            }
        }

        reply = auto_reply_engagement_with_llm(self.engagement)

        self.engagement.refresh_from_db()
        self.assertEqual(reply, 'Thank you for your kind words.')
        self.assertEqual(self.engagement.ai_response, reply)
        self.assertEqual(self.engagement.final_response, reply)
        self.assertTrue(self.engagement.is_auto_replied)
        self.assertEqual(self.engagement.status, 'CLOSED')
        self.assertEqual(
            EngagementMessage.objects.get(engagement=self.engagement).sender_type,
            'SYSTEM',
        )

    @override_settings(AUTO_REPLY_CATEGORIES=['Appreciation'])
    @patch('apps.engagements.services._post_json')
    def test_auto_reply_is_idempotent(self, post_json):
        self.engagement.ai_response = 'Already sent.'
        self.engagement.final_response = 'Already sent.'
        self.engagement.is_auto_replied = True
        self.engagement.status = 'CLOSED'
        self.engagement.save()

        reply = auto_reply_engagement_with_llm(self.engagement)

        self.assertEqual(reply, 'Already sent.')
        post_json.assert_not_called()
        self.assertEqual(
            EngagementMessage.objects.filter(engagement=self.engagement).count(),
            0,
        )

    @override_settings(AUTO_REPLY_CATEGORIES=['Appreciation'])
    @patch('apps.engagements.services._post_json')
    def test_categorization_endpoint_runs_auto_reply_for_appreciation(self, post_json):
        user = get_user_model().objects.create_user(
            username='agent',
            password='password',
        )
        client = Client()
        client.force_login(user)
        post_json.side_effect = [
            {
                'message': {
                    'content': '{"category": "Appreciation"}'
                }
            },
            {
                'message': {
                    'content': '{"reply": "We appreciate your feedback."}'
                }
            },
        ]

        response = client.get(
            reverse('categorize_engagement', args=[self.engagement.id])
        )

        self.engagement.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['auto_replied'])
        self.assertEqual(self.engagement.status, 'CLOSED')
        self.assertTrue(self.engagement.is_auto_replied)
