from django.db import models
from django.utils import timezone
from django.utils.timezone import now


class MpesaTransaction(models.Model):
    CheckoutRequestID = models.CharField(max_length=50, blank=True, null=True)
    MerchantRequestID = models.CharField(max_length=20, blank=True, null=True)
    ResultCode = models.IntegerField(blank=True, null=True)
    ResultDesc = models.CharField(max_length=120, blank=True, null=True)
    Amount = models.FloatField(blank=True, null=True)
    MpesaReceiptNumber = models.CharField(max_length=15, blank=True, null=True)
    TransactionDate = models.DateTimeField(blank=True, null=True)
    PhoneNumber = models.CharField(max_length=13, blank=True, null=True)

    def __str__(self):
        return f"{self.PhoneNumber} HAS PAID  {self.Amount} : {self.MpesaReceiptNumber}"


    class Meta:
        verbose_name = ("M-PESA  Payment")
        verbose_name_plural = ("M-PESA  Payments")
        
class EventRegistration(models.Model):
    # Choices for the 'Are you a student?' field
    YES_NO_CHOICES = [
        ('yes', 'Yes'),
        ('no', 'No'),
    ]

    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()
    is_campus_student = models.CharField(
        max_length=3, choices=YES_NO_CHOICES, default='no'
    )
    school_name = models.CharField(
        max_length=255, blank=True, null=True
    )

    def __str__(self):
        return self.name
