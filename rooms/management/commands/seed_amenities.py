from django.core.management.base import BaseCommand
from rooms.models import Amenity

class Command(BaseCommand):
    help = "이건 편의시설 amenities 씨드임"

    # def add_arguments(self, parser):
    #     parser.add_argument("--times", help="얼마나말할까여?")

    def handle(self, *args, **options):
        amenities = [
            "Hair dryer",
            "Cleaning products",
            "Shampoo",
            "Conditioner",
            "Body soap",
            "Bidet",
            "Shower gel",
            "Hot water",
            "Washer",
            "Essentials",
            "Hangers",
            "Bed linens",
            "Clothing storage",
            "Extra pillows and blankets",
            "TV with standard cable",
            "Air conditioning",
            "Heating",
            "Smoke alarm",
            "Carbon monoxide alarm",
            "Fire extinguisher",
            "Wifi",
            "Kitchen",
            "Refrigerator",
            "Microwave",
            "Dishes and silverware",
            "Freezer",
            "Hot water kettle",
            "Coffee maker",
            "Wine glasses",
            "Toaster",
            "Dining table",
            "Stove",
            "Free parking on premises",
            "Free street parking",
            "Single level home",
            "No stairs in home",
            "Long term stays allowed",
            "Self check-in",
            "Keypad",
        ]

        for a in amenities:
            Amenity.objects.create(name=a)
        self.stdout.write(self.style.SUCCESS("amenities created"))