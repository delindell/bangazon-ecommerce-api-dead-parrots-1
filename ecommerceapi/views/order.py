from django.http import HttpResponseServerError
from datetime import date
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework import status
from ecommerceapi.models import PaymentType, Customer, Order

class OrderSerializer(serializers.HyperlinkedModelSerializer):
    """JSON serializer for payment types

    Arguments:
        serializers
    """
    class Meta:
        model = Order
        url = serializers.HyperlinkedIdentityField(
            view_name="orders",
            lookup_field="id"
        )
        fields = (
          'id', 'url', 'customer', 'payment_type',
          'products', 'created_at'
        )
        depth = 2


class Orders(ViewSet):
    """Orders for Bangazon customers"""

    def update(self, request, pk=None):

        customer = Customer.objects.get(user=request.auth.user)
        order = Order.objects.get(pk=pk)
        order.customer = customer
        order.payment_type_id = request.data["payment_type_id"]
        order.created_at = order.created_at
        order.save()
        new_order = Order.objects.create(customer_id = customer.id, payment_type_id = None)
        serializer = OrderSerializer(order, context={'request': request})

        return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)


    def destroy(self, request, pk=None):

        customer = Customer.objects.get(user=request.auth.user)

        try:
            order = Order.objects.get(pk=pk)
            order.delete()
            new_order = Order.objects.create(customer_id = customer.id, payment_type_id = None)
            return Response({}, status=status.HTTP_204_NO_CONTENT)

        except Order.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single customer payment type
        
          Returns: JSON serialized payment type instance
        """
        try:
            order = Order.objects.get(pk=pk)
            serializer = OrderSerializer(order, context={'request': request})
            return Response(serializer.data)
        except Exception as ex:
            return HttpResponseServerError(ex)

    def list(self, request):
        """Handle GET requests to orders
        
          Returns: Response JSON serialized list of order
        """
        history = self.request.query_params.get('history', None)
        customer = Customer.objects.get(user=request.auth.user)

        orders = Order.objects.filter(customer_id=customer.id, payment_type_id=None)

        if history is not None:
          orders = Order.objects.filter(customer_id=customer.id)

        serializer = OrderSerializer(
          orders,
          many=True,
          context={'request': request}
        )

        return Response(serializer.data)
