# Generated by Django 5.0.4 on 2024-08-08 10:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("task_workers", "0006_subscriptionplan_tasker_subscription_status_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="tasker",
            name="subscription_plan",
        ),
        migrations.RemoveField(
            model_name="tasker",
            name="subscription_status",
        ),
        migrations.DeleteModel(
            name="SubscriptionPlan",
        ),
    ]
