from django import template
from accounts.models import Notification

register = template.Library()

@register.simple_tag(takes_context=True)
def get_agent_notifications(context):
    user = context['user']  # Assuming 'user' is available in the template context
    agent_notifications = Notification.objects.filter(user=user)
    return agent_notifications