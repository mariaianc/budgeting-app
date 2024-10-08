# Generated by Django 5.0.2 on 2024-04-20 15:09

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='images/')),
            ],
        ),
        migrations.CreateModel(
            name='Economies',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('month', models.IntegerField()),
                ('year', models.IntegerField()),
                ('monthly_economies', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('total_economies', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Expense',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.DecimalField(decimal_places=2, max_digits=10)),
                ('type', models.CharField(choices=[('essential', 'Essential'), ('important', 'Important'), ('minor', 'Minor')], max_length=20)),
                ('frequency', models.CharField(choices=[('one_time', 'One Time'), ('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly'), ('6_months', 'Every 6 Months'), ('yearly', 'Yearly')], default='one_time', max_length=20)),
                ('category', models.CharField(choices=[('housing', 'Housing'), ('food', 'Food'), ('health', 'Health'), ('utilities', 'Utilities'), ('transport', 'Transport'), ('personal', 'Personal'), ('entertainment', 'Entertainment'), ('vices', 'Vices'), ('other', 'Other')], max_length=20)),
                ('day', models.DateField(auto_now_add=True)),
                ('hour', models.TimeField(auto_now_add=True)),
                ('currency', models.CharField(max_length=3)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Goal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('target_amount', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='GoalSavings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('month', models.IntegerField()),
                ('year', models.IntegerField()),
                ('monthly_savings', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('total_savings', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('goal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.goal')),
            ],
        ),
        migrations.CreateModel(
            name='Income',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_amount', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('income_left', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('month', models.IntegerField()),
                ('year', models.IntegerField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CashIncome',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('currency', models.CharField(max_length=3)),
                ('day', models.DateField(auto_now_add=True)),
                ('hour', models.TimeField(auto_now_add=True)),
                ('income', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cash_incomes', to='accounts.income')),
            ],
        ),
        migrations.CreateModel(
            name='CardIncome',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('currency', models.CharField(max_length=3)),
                ('day', models.DateField(auto_now_add=True)),
                ('hour', models.TimeField(auto_now_add=True)),
                ('income', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='card_incomes', to='accounts.income')),
            ],
        ),
        migrations.CreateModel(
            name='TotalExpense',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_housing_expense', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('total_food_expense', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('total_health_expense', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('total_utilities_expense', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('total_transport_expense', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('total_personal_expense', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('total_entertainment_expense', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('total_vices_expense', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('total_other_expense', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('total_expenses', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('month', models.IntegerField()),
                ('year', models.IntegerField()),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
