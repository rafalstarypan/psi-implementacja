"""
Management command to seed supply items data.
"""
from decimal import Decimal
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from apps.accounts.models import User
from apps.supplies.models import (
    SupplyCategory, UnitOfMeasure, Supplier, SupplyItem,
    Inventory, InventoryLog, SupplyOrder, SupplyOrderLine,
    InventoryOperationType, SupplyOrderStatus
)


class Command(BaseCommand):
    help = 'Seed supply items data for demonstration purposes'

    def handle(self, *args, **options):
        self.seed_categories()
        self.seed_units()
        self.seed_suppliers()
        self.seed_items()
        self.seed_orders()
        self.seed_logs()
        self.stdout.write(self.style.SUCCESS('Supply data seeding completed!'))

    def seed_categories(self):
        categories = ['Żywność', 'Leki', 'Higiena', 'Akcesoria', 'Ochrona']
        for name in categories:
            cat, created = SupplyCategory.objects.get_or_create(name=name)
            if created:
                self.stdout.write(f'Created category: {name}')

    def seed_units(self):
        units = [
            ('kilogram', 'kg'),
            ('sztuka', 'szt'),
            ('litr', 'l'),
            ('opakowanie', 'op'),
            ('para', 'par'),
        ]
        for name, abbr in units:
            unit, created = UnitOfMeasure.objects.get_or_create(
                name=name, defaults={'abbreviation': abbr}
            )
            if created:
                self.stdout.write(f'Created unit: {name}')

    def seed_suppliers(self):
        suppliers = [
            {'name': 'PetFood Sp. z o.o.', 'email': 'kontakt@petfood.pl'},
            {'name': 'ZooMarket', 'email': 'zamowienia@zoomarket.pl'},
            {'name': 'VetPharm', 'email': 'hurtownia@vetpharm.pl'},
            {'name': 'CleanPro', 'email': 'biuro@cleanpro.pl'},
            {'name': 'TextilPet', 'email': 'sklep@textilpet.pl'},
        ]
        for data in suppliers:
            supplier, created = Supplier.objects.get_or_create(
                name=data['name'], defaults={'email': data['email']}
            )
            if created:
                self.stdout.write(f'Created supplier: {data["name"]}')

    def seed_items(self):
        items_data = [
            {
                'name': 'Karma sucha dla psów',
                'description': 'Karma sucha dla psów dorosłych, wszystkie rasy',
                'min_stock': Decimal('50.00'),
                'current_quantity': Decimal('35.00'),
                'category': 'Żywność',
                'unit': 'kilogram',
            },
            {
                'name': 'Karma mokra dla kotów',
                'description': 'Karma mokra w puszkach, różne smaki',
                'min_stock': Decimal('80.00'),
                'current_quantity': Decimal('120.00'),
                'category': 'Żywność',
                'unit': 'sztuka',
            },
            {
                'name': 'Piasek dla kotów',
                'description': 'Żwirek zbrylający dla kotów',
                'min_stock': Decimal('30.00'),
                'current_quantity': Decimal('25.00'),
                'category': 'Higiena',
                'unit': 'kilogram',
            },
            {
                'name': 'Antybiotyki',
                'description': 'Antybiotyki szerokopasmowe',
                'min_stock': Decimal('20.00'),
                'current_quantity': Decimal('15.00'),
                'category': 'Leki',
                'unit': 'opakowanie',
            },
            {
                'name': 'Witaminy',
                'description': 'Suplementy witaminowe dla zwierząt',
                'min_stock': Decimal('50.00'),
                'current_quantity': Decimal('80.00'),
                'category': 'Leki',
                'unit': 'sztuka',
            },
            {
                'name': 'Środki czyszczące',
                'description': 'Środki do dezynfekcji pomieszczeń',
                'min_stock': Decimal('15.00'),
                'current_quantity': Decimal('5.00'),
                'category': 'Higiena',
                'unit': 'litr',
            },
            {
                'name': 'Smycze',
                'description': 'Smycze regulowane, różne rozmiary',
                'min_stock': Decimal('20.00'),
                'current_quantity': Decimal('25.00'),
                'category': 'Akcesoria',
                'unit': 'sztuka',
            },
            {
                'name': 'Miski dla zwierząt',
                'description': 'Miski metalowe, antypoślizgowe',
                'min_stock': Decimal('30.00'),
                'current_quantity': Decimal('50.00'),
                'category': 'Akcesoria',
                'unit': 'sztuka',
            },
            {
                'name': 'Koce',
                'description': 'Koce ciepłe dla zwierząt',
                'min_stock': Decimal('15.00'),
                'current_quantity': Decimal('12.00'),
                'category': 'Akcesoria',
                'unit': 'sztuka',
            },
            {
                'name': 'Rękawice ochronne',
                'description': 'Rękawice jednorazowe, lateksowe',
                'min_stock': Decimal('60.00'),
                'current_quantity': Decimal('100.00'),
                'category': 'Ochrona',
                'unit': 'para',
            },
            {
                'name': 'Szczepionki',
                'description': 'Szczepionki podstawowe dla psów i kotów',
                'min_stock': Decimal('10.00'),
                'current_quantity': Decimal('5.00'),
                'category': 'Leki',
                'unit': 'opakowanie',
            },
            {
                'name': 'Karma sucha dla kotów',
                'description': 'Karma sucha dla kotów dorosłych',
                'min_stock': Decimal('40.00'),
                'current_quantity': Decimal('60.00'),
                'category': 'Żywność',
                'unit': 'kilogram',
            },
        ]

        for data in items_data:
            category = SupplyCategory.objects.get(name=data['category'])
            unit = UnitOfMeasure.objects.get(name=data['unit'])

            item, created = SupplyItem.objects.get_or_create(
                name=data['name'],
                defaults={
                    'description': data['description'],
                    'min_stock': data['min_stock'],
                    'category': category,
                    'unit': unit,
                }
            )

            if created:
                Inventory.objects.create(
                    supply_item=item,
                    current_quantity=data['current_quantity'],
                )
                self.stdout.write(f'Created item: {data["name"]}')

    def seed_orders(self):
        orders_data = [
            {
                'supplier': 'PetFood Sp. z o.o.',
                'days_until_delivery': 7,
                'items': [('Karma sucha dla psów', Decimal('30.00'))],
            },
            {
                'supplier': 'ZooMarket',
                'days_until_delivery': 3,
                'items': [('Piasek dla kotów', Decimal('40.00'))],
            },
            {
                'supplier': 'VetPharm',
                'days_until_delivery': 5,
                'items': [
                    ('Antybiotyki', Decimal('10.00')),
                    ('Szczepionki', Decimal('8.00')),
                ],
            },
            {
                'supplier': 'CleanPro',
                'days_until_delivery': 2,
                'items': [('Środki czyszczące', Decimal('20.00'))],
            },
            {
                'supplier': 'TextilPet',
                'days_until_delivery': 10,
                'items': [('Koce', Decimal('10.00'))],
            },
        ]

        for data in orders_data:
            supplier = Supplier.objects.get(name=data['supplier'])
            order, created = SupplyOrder.objects.get_or_create(
                supplier=supplier,
                expected_delivery_date=date.today() + timedelta(days=data['days_until_delivery']),
                status=SupplyOrderStatus.IN_PROGRESS,
            )

            if created:
                for item_name, quantity in data['items']:
                    item = SupplyItem.objects.get(name=item_name)
                    SupplyOrderLine.objects.create(
                        order=order,
                        supply_item=item,
                        quantity=quantity,
                    )
                self.stdout.write(f'Created order from: {data["supplier"]}')

    def seed_logs(self):
        try:
            user = User.objects.filter(role='employee').first()
        except User.DoesNotExist:
            user = None

        logs_data = [
            {
                'item': 'Karma sucha dla psów',
                'logs': [
                    (InventoryOperationType.OUTBOUND, Decimal('10.00'), 'Codzienna porcja dla 15 psów'),
                    (InventoryOperationType.OUTBOUND, Decimal('12.00'), 'Karmienie wieczorne'),
                    (InventoryOperationType.INBOUND, Decimal('50.00'), 'Dostawa od PetFood Sp. z o.o.'),
                    (InventoryOperationType.OUTBOUND, Decimal('15.00'), 'Karmienie poranne i wieczorne'),
                ],
            },
            {
                'item': 'Karma mokra dla kotów',
                'logs': [
                    (InventoryOperationType.OUTBOUND, Decimal('24.00'), 'Karmienie 12 kotów - porcje dzienne'),
                    (InventoryOperationType.INBOUND, Decimal('144.00'), 'Dostawa miesięczna'),
                ],
            },
        ]

        for data in logs_data:
            try:
                item = SupplyItem.objects.get(name=data['item'])
                inventory = item.inventory

                # Only create logs if none exist
                if not inventory.logs.exists():
                    for op_type, quantity, comment in data['logs']:
                        InventoryLog.objects.create(
                            inventory=inventory,
                            operation_type=op_type,
                            quantity=quantity,
                            comment=comment,
                            performed_by=user,
                        )
                    self.stdout.write(f'Created logs for: {data["item"]}')
            except (SupplyItem.DoesNotExist, Inventory.DoesNotExist):
                pass
