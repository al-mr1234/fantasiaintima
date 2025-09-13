from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received
from django.dispatch import receiver
from .models import HistorialPedido
from decimal import Decimal
from django.utils import timezone

@receiver(valid_ipn_received)
def pago_paypal_exitoso(sender, **kwargs):
    ipn_obj = sender
    if ipn_obj.payment_status == ST_PP_COMPLETED:
        codigo_pedido = ipn_obj.invoice
        HistorialPedido.objects.filter(codigo_pedido=codigo_pedido).update(
            estado='Pagado',
            fecha_compra=timezone.now()
        )