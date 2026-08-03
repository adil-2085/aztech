from django.core.management.base import BaseCommand
from utils.models import Category, Brand


class Command(BaseCommand):
    help = (
        "Seeds a couple of Category/Brand rows so the product form's dropdowns "
        "aren't empty on a fresh install. Product data itself is meant to be "
        "entered through the new dashboard UI, not this command."
    )

    def handle(self, *args, **options):
        categories = [
            ('Jackets', 'jackets'),
            ('Knitwear', 'knitwear'),
            ('Footwear', 'footwear'),
        ]
        brands = [
            ('Loom Originals', 'loom-originals'),
        ]

        for name, slug in categories:
            obj, created = Category.objects.get_or_create(slug=slug, defaults={'name': name})
            self.stdout.write(f"{'Created' if created else 'Already exists'}: Category '{obj.name}'")

        for name, slug in brands:
            obj, created = Brand.objects.get_or_create(slug=slug, defaults={'name': name})
            self.stdout.write(f"{'Created' if created else 'Already exists'}: Brand '{obj.name}'")

        self.stdout.write(self.style.SUCCESS(
            "\nDone. Now: python manage.py createsuperuser (if you haven't), "
            "log in at /admin/, then visit /dashboard/products/ to add real products."
        ))