# Generated by Django 5.1.6 on 2025-03-03 12:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop_app', '0010_alter_order_status'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='order',
            options={'ordering': ['id'], 'verbose_name': 'Заказ', 'verbose_name_plural': 'Заказы'},
        ),
        migrations.AddField(
            model_name='product',
            name='city',
            field=models.CharField(choices=[('minsk', 'Минск'), ('gomel', 'Гомель'), ('brest', 'Брест'), ('vitebsk', 'Витебск'), ('grodno', 'Гродно'), ('mogilev', 'Могилёв'), ('bobruisk', 'Бобруйск'), ('baranovichi', 'Барановичи'), ('borisov', 'Борисов'), ('pinsk', 'Пинск'), ('orsha', 'Орша'), ('mozyr', 'Мозырь'), ('soligorsk', 'Солигорск'), ('novopolotsk', 'Новополоцк'), ('molodechno', 'Молодечно'), ('lida', 'Лида'), ('mazyr', 'Мазыр')], default='minsk', max_length=100, verbose_name='Город'),
            preserve_default=False,
        ),
    ]
