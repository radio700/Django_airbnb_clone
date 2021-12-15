from django.core.management.base import BaseCommand
from rooms.models import Facility

class Command(BaseCommand):
    help = "이건 편의시설 facilities 씨드임"

    # def add_arguments(self, parser):
    #     parser.add_argument("--times", help="얼마나말할까여?")

    def handle(self, *args, **options):
        facilities = [
            "private entrance",
            "Paid parking on premises",
            "Paid parking off premises",
            "Elevator",
            "Parking",
            "Gym",
        ]

        for f in facilities:
            Facility.objects.create(name=f)
        self.stdout.write(self.style.SUCCESS(f"{len(facilities)} created "))