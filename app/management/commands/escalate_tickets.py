from django.core.management.base import BaseCommand
from django.utils.timezone import now
from django.core.mail import send_mail
from datetime import timedelta
from app.models import HelpDeskTicket

class Command(BaseCommand):
    help = "Escalate tickets to HR and Manager if unseen within 1 minute (for testing)."

    HR_ISSUE_DISPLAY = {
        'attendance': 'Attendance Issue',
        'payroll': 'Payroll Issue',
        'leave': 'Leave Request',
        'policy': 'Policy Clarification',
    }

    IT_ISSUE_DISPLAY = {
        'login': 'Login Problem',
        'hardware': 'Hardware Issue',
        'software': 'Software Problem',
        'network': 'Network Issue',
    }

    AS_ISSUE_DISPLAY = {  # Renamed category: AS = Asset
        'exam': 'Laptop Not Working',
        'grading': 'Missing Asset',
        'result': 'Need New Equipment',
        'reassessment': 'Return Asset Request',
    }

    def get_issue_display(self, ticket):
        issue_type = ticket.issue_type
        if ticket.category == 'HR':
            return self.HR_ISSUE_DISPLAY.get(issue_type, issue_type)
        elif ticket.category == 'IT':
            return self.IT_ISSUE_DISPLAY.get(issue_type, issue_type)
        elif ticket.category == 'AS':  # AS now means "Asset"
            return self.AS_ISSUE_DISPLAY.get(issue_type, issue_type)
        return issue_type

    def handle(self, *args, **kwargs):
        now_time = now()

        # Escalate to HR after 1 minute if TL hasn't seen
        tl_tickets = HelpDeskTicket.objects.filter(
            viewed_by_tl=False,
            escalated_to_hr_at__isnull=True,
            created_at__lte=now_time - timedelta(minutes=1)
        )

        for ticket in tl_tickets:
            ticket.escalated_to_hr_at = now_time
            ticket.save()

            issue_display = self.get_issue_display(ticket)

            if ticket.escalate_to_hr and ticket.escalate_to_hr.email:
                send_mail(
                    subject=f"[Escalated to HR] Ticket #{ticket.id}",
                    message=(
                        f"The ticket from {ticket.employee} has been escalated to you.\n\n"
                        f"Issue Type: {issue_display}\n"
                        f"Description: {ticket.description}"
                    ),
                    from_email=None,
                    recipient_list=[ticket.escalate_to_hr.email],
                    fail_silently=False,
                )
            self.stdout.write(self.style.WARNING(f"Escalated to HR: Ticket #{ticket.id}"))

        # Escalate to Manager after 1 more minute if HR hasn't seen
        hr_tickets = HelpDeskTicket.objects.filter(
            viewed_by_hr=False,
            escalated_to_hr_at__isnull=False,
            escalated_to_manager_at__isnull=True,
            escalated_to_hr_at__lte=now_time - timedelta(minutes=1)
        )

        for ticket in hr_tickets:
            ticket.escalated_to_manager_at = now_time
            ticket.save()

            issue_display = self.get_issue_display(ticket)

            if ticket.manager and ticket.manager.email:
                send_mail(
                    subject=f"[Escalated to Manager] Ticket #{ticket.id}",
                    message=(
                        f"The ticket from {ticket.employee} has now been escalated to you.\n\n"
                        f"Issue Type: {issue_display}\n"
                        f"Description: {ticket.description}"
                    ),
                    from_email=None,
                    recipient_list=[ticket.manager.email],
                    fail_silently=False,
                )
            self.stdout.write(self.style.ERROR(f"Escalated to Manager: Ticket #{ticket.id}"))

        self.stdout.write(self.style.SUCCESS("Escalation process completed."))
