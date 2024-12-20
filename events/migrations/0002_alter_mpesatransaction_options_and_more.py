# Generated by Django 5.1.4 on 2024-12-08 16:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='mpesatransaction',
            options={'verbose_name': 'M-PESA  Payment', 'verbose_name_plural': 'M-PESA  Payments'},
        ),
        migrations.RenameField(
            model_name='mpesatransaction',
            old_name='phone_number',
            new_name='MpesaReceiptNumber',
        ),
        migrations.RenameField(
            model_name='mpesatransaction',
            old_name='result_code',
            new_name='ResultCode',
        ),
        migrations.RenameField(
            model_name='mpesatransaction',
            old_name='transaction_date',
            new_name='TransactionDate',
        ),
        migrations.RemoveField(
            model_name='mpesatransaction',
            name='amount',
        ),
        migrations.RemoveField(
            model_name='mpesatransaction',
            name='callback_url',
        ),
        migrations.RemoveField(
            model_name='mpesatransaction',
            name='checkout_request_id',
        ),
        migrations.RemoveField(
            model_name='mpesatransaction',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='mpesatransaction',
            name='merchant_request_id',
        ),
        migrations.RemoveField(
            model_name='mpesatransaction',
            name='mpesa_receipt_number',
        ),
        migrations.RemoveField(
            model_name='mpesatransaction',
            name='result_desc',
        ),
        migrations.RemoveField(
            model_name='mpesatransaction',
            name='status',
        ),
        migrations.RemoveField(
            model_name='mpesatransaction',
            name='updated_at',
        ),
        migrations.AddField(
            model_name='mpesatransaction',
            name='CheckoutRequestID',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='mpesatransaction',
            name='MerchantRequestID',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='mpesatransaction',
            name='PhoneNumber',
            field=models.CharField(blank=True, max_length=13, null=True),
        ),
        migrations.AddField(
            model_name='mpesatransaction',
            name='ResultDesc',
            field=models.CharField(blank=True, max_length=120, null=True),
        ),
        migrations.AddField(
            model_name='mpesatransaction',
            name='Amount',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
