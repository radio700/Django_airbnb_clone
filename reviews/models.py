from django.db import models
from core import models as core_models
from users.models import User
from rooms.models import Room

# Create your models here.


class Review(core_models.TimeStampModel):
    """review"""

    review = models.TextField()
    accuracy = models.IntegerField()
    communication = models.IntegerField()
    cleanliness = models.IntegerField()
    location = models.IntegerField()
    check_in = models.IntegerField()
    value = models.IntegerField()
    user = models.ForeignKey(User, related_name="reviews", on_delete=models.CASCADE)
    room = models.ForeignKey(Room, related_name="reviews", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.review} - {self.room}"
        # 포린키 설정하니까 딴거도 가능한거야

    def rating_average(self):
        avg = (
            self.accuracy
            + self.communication
            + self.cleanliness
            + self.location
            + self.check_in
            + self.value
        ) / 6
        return round(avg, 2)
