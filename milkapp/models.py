from django.db import models


class userProfileModel(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class milkShiftNameModel(models.Model):
    user = models.ForeignKey(
        userProfileModel,
        on_delete=models.CASCADE,
        related_name="milk_shifts_name_model"
    )
    shift_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.shift_name


class updateMilkEntryModel(models.Model):
    STATE = [
        ('Present', 'Present'),
        ('Absent', 'Absent'),
        (None, None),
    ]
    user = models.ForeignKey(userProfileModel, on_delete=models.CASCADE)
    milk_shift = models.ForeignKey(milkShiftNameModel, on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateField(default=None, null=True, blank=True)
    liter = models.FloatField(default=1)
    price = models.FloatField(default=50)
    state = models.CharField(max_length=20, choices=STATE, default=None, null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "milk_shift", "date"],
                name="unique_milk_entry_per_shift_date",
            )
        ]

    def __str__(self):
        return f"{self.user.name} - {self.date} - {self.liter}L - ${self.price} - {self.state}"


class totalPriceModel(models.Model):
    userprofile = models.OneToOneField(userProfileModel, on_delete=models.CASCADE)
    milk_shift = models.ForeignKey(milkShiftNameModel, on_delete=models.CASCADE)
    total_liter = models.FloatField(default=0)
    total_price = models.FloatField(default=0)

    def __str__(self):
        return f"{self.userprofile.name} - Total Liter: {self.total_liter}L - Total Price: ${self.total_price}"
