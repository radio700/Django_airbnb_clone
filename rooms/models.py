from django.db import models
from django_countries.fields import CountryField
from core import models as core_models
from users import models as user_models
from django.urls import reverse

# Create your models here.


class AbstractItem(core_models.TimeStampModel):

    """abstrace item"""

    name = models.CharField(max_length=80)
    # subtitle = models.CharField(max_length=100)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class RoomType(AbstractItem):
    class Meta:
        verbose_name = "Room Type"
        ordering = ["name"]


class Amenity(AbstractItem):
    """room object definition"""

    pass


class Facility(AbstractItem):
    """Faiciliey"""

    pass


class HouseRule(AbstractItem):
    class Meta:
        verbose_name = "House Rule"


class Room(core_models.TimeStampModel):
    """room model def"""

    name = models.CharField(max_length=140)
    description = models.TextField()
    country = CountryField()
    city = models.CharField(max_length=80)
    price = models.IntegerField()
    address = models.CharField(max_length=140)
    guest = models.IntegerField(help_text="얼마나 많은 사람들이 지낼껀지")
    beds = models.IntegerField()
    bedrooms = models.IntegerField()
    baths = models.IntegerField()
    check_in = models.TimeField()
    check_out = models.TimeField()
    instant_book = models.BooleanField(default=False)
    host = models.ForeignKey(
        user_models.User, related_name="rooms", on_delete=models.CASCADE
    )
    room_type = models.ForeignKey(
        RoomType, related_name="rooms", on_delete=models.SET_NULL, null=True
    )
    amenities = models.ManyToManyField(Amenity, related_name="rooms", blank=True)
    facilities = models.ManyToManyField(Facility, related_name="rooms", blank=True)
    house_rules = models.ManyToManyField(HouseRule, related_name="rooms", blank=True)

    def __str__(self):
        return self.name

    # 이걸로 city에 소문자로 적든 대문자로 적든 무조건 첫 글자는 대문자로 적게됨 상속이용해서
    def save(self, *args, **kwargs):
        self.city = str.capitalize(self.city)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("rooms:detail", kwargs={"pk": self.pk})

    def total_rating(self):
        all_reviews = self.reviews.all()
        all_ratings = 0
        if len(all_reviews) > 0:
            for review in all_reviews:
                all_ratings = +review.rating_average()
            return round(all_ratings / len(all_reviews), 2)
        return 0

    def first_photo(self):
        photo, = self.photos.all()[:1]
        return photo.file.url


class Photo(core_models.TimeStampModel):
    """photo model def"""

    caption = models.CharField(max_length=80)
    file = models.ImageField(upload_to="room_photos")
    room = models.ForeignKey(Room, related_name="photos", on_delete=models.CASCADE)

    def __str__(self):
        return self.caption

