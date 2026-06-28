from django.core.management.base import BaseCommand

from suoi_tien.models import HalinkPost, HalinkMeta


class Command(BaseCommand):
    help = (
        "Dong bo lai post_amount (gia THAT, duoc API public/dat ve-dat mon doc) "
        "cho cac San pham co gia da nhap qua Admin nhung chua tung duoc ghi vao "
        "post_amount (bug truoc khi fix ProductProxyAdmin.save_model)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--apply', action='store_true',
            help='Thuc su ghi de DB. Khong truyen co nay se chi in ra (dry-run), khong sua gi.',
        )

    def handle(self, *args, **options):
        import sys
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')

        apply_changes = options['apply']
        mode = "AP DUNG THAY DOI" if apply_changes else "DRY-RUN (chi xem truoc, chua sua)"
        self.stdout.write(self.style.WARNING(f"=== BACKFILL post_amount CHO SAN PHAM — {mode} ==="))

        products = HalinkPost.objects.filter(post_type='product')
        metas = HalinkMeta.objects.filter(
            Id_post__in=products.values_list('Id', flat=True),
            meta_title__in=['halink_metabox_gia', 'halink_metabox_gia_khuyen_mai'],
        )
        price_by_post = {}
        for meta in metas:
            try:
                value = int(meta.meta_value)
            except (TypeError, ValueError):
                continue
            entry = price_by_post.setdefault(meta.Id_post, {})
            if meta.meta_title == 'halink_metabox_gia':
                entry['price'] = value
            else:
                entry['promo'] = value

        changed = 0
        for product in products:
            entry = price_by_post.get(product.Id)
            if not entry:
                continue
            correct_amount = entry.get('promo') or entry.get('price') or 0
            if correct_amount and product.post_amount != correct_amount:
                self.stdout.write(
                    f"  San pham #{product.Id} ({product.clean_title}): "
                    f"post_amount {product.post_amount} -> {correct_amount}"
                )
                changed += 1
                if apply_changes:
                    product.post_amount = correct_amount
                    product.save(update_fields=['post_amount'])

        self.stdout.write(self.style.SUCCESS(
            f"Tong so san pham can sua: {changed}."
            + ("" if apply_changes else " Chay lai voi --apply de ghi thuc su.")
        ))
