from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status

from .models import (
    Destination, Interest, Attraction, Restaurant,
    HotelRecommendation, TransportRecommendation, CostBenchmark
)
from .serializers import (
    DestinationListSerializer, DestinationDetailSerializer,
    InterestSerializer, AttractionSerializer, RestaurantSerializer,
    HotelSerializer, TransportSerializer, CostBenchmarkSerializer
)


# =========================
# DESTINATIONS
# =========================

class DestinationListCreateView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        qs = Destination.objects.all()

        is_active = request.query_params.get('is_active')
        if is_active is not None:
            qs = qs.filter(is_active=is_active.lower() == 'true')

        province = request.query_params.get('province')
        if province:
            qs = qs.filter(province__icontains=province)

        search = request.query_params.get('search')
        if search:
            qs = qs.filter(city_name__icontains=search) | \
                 qs.filter(province__icontains=search) | \
                 qs.filter(description__icontains=search)

        ordering = request.query_params.get('ordering', 'city_name')
        allowed_ordering = ['city_name', '-city_name', 'created_at', '-created_at',
                            'avg_budget_low', '-avg_budget_low']
        if ordering in allowed_ordering:
            qs = qs.order_by(ordering)

        serializer = DestinationListSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = DestinationDetailSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DestinationRetrieveUpdateDestroyView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, pk):
        return get_object_or_404(
            Destination.objects.prefetch_related(
                'attractions', 'restaurants', 'hotels',
                'transport_options', 'cost_benchmarks'
            ),
            pk=pk
        )

    def get(self, request, pk):
        destination = self.get_object(pk)
        serializer = DestinationDetailSerializer(destination)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        destination = self.get_object(pk)
        serializer = DestinationDetailSerializer(destination, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        destination = self.get_object(pk)
        serializer = DestinationDetailSerializer(destination, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        destination = self.get_object(pk)
        destination.delete()
        return Response({"message": "Destination deleted."}, status=status.HTTP_204_NO_CONTENT)


# =========================
# ATTRACTIONS
# =========================

class AttractionListCreateView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, destination_pk):
        destination = get_object_or_404(Destination, pk=destination_pk)
        qs = Attraction.objects.filter(destination=destination)

        category = request.query_params.get('category')
        if category:
            qs = qs.filter(category=category)

        is_active = request.query_params.get('is_active')
        if is_active is not None:
            qs = qs.filter(is_active=is_active.lower() == 'true')

        search = request.query_params.get('search')
        if search:
            qs = qs.filter(name__icontains=search) | qs.filter(description__icontains=search)

        serializer = AttractionSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, destination_pk):
        destination = get_object_or_404(Destination, pk=destination_pk)
        serializer = AttractionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(destination=destination)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AttractionRetrieveUpdateDestroyView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, destination_pk, pk):
        destination = get_object_or_404(Destination, pk=destination_pk)
        return get_object_or_404(Attraction, destination=destination, pk=pk)

    def get(self, request, destination_pk, pk):
        attraction = self.get_object(destination_pk, pk)
        serializer = AttractionSerializer(attraction)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, destination_pk, pk):
        attraction = self.get_object(destination_pk, pk)
        serializer = AttractionSerializer(attraction, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, destination_pk, pk):
        attraction = self.get_object(destination_pk, pk)
        serializer = AttractionSerializer(attraction, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, destination_pk, pk):
        attraction = self.get_object(destination_pk, pk)
        attraction.delete()
        return Response({"message": "Attraction deleted."}, status=status.HTTP_204_NO_CONTENT)


# =========================
# RESTAURANTS
# =========================

class RestaurantListCreateView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, destination_pk):
        destination = get_object_or_404(Destination, pk=destination_pk)
        qs = Restaurant.objects.filter(destination=destination)

        category = request.query_params.get('category')
        if category:
            qs = qs.filter(category=category)

        cuisine_type = request.query_params.get('cuisine_type')
        if cuisine_type:
            qs = qs.filter(cuisine_type=cuisine_type)

        is_active = request.query_params.get('is_active')
        if is_active is not None:
            qs = qs.filter(is_active=is_active.lower() == 'true')

        search = request.query_params.get('search')
        if search:
            qs = qs.filter(name__icontains=search) | qs.filter(area__icontains=search)

        serializer = RestaurantSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, destination_pk):
        destination = get_object_or_404(Destination, pk=destination_pk)
        serializer = RestaurantSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(destination=destination)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RestaurantRetrieveUpdateDestroyView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, destination_pk, pk):
        destination = get_object_or_404(Destination, pk=destination_pk)
        return get_object_or_404(Restaurant, destination=destination, pk=pk)

    def get(self, request, destination_pk, pk):
        restaurant = self.get_object(destination_pk, pk)
        serializer = RestaurantSerializer(restaurant)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, destination_pk, pk):
        restaurant = self.get_object(destination_pk, pk)
        serializer = RestaurantSerializer(restaurant, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, destination_pk, pk):
        restaurant = self.get_object(destination_pk, pk)
        serializer = RestaurantSerializer(restaurant, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, destination_pk, pk):
        restaurant = self.get_object(destination_pk, pk)
        restaurant.delete()
        return Response({"message": "Restaurant deleted."}, status=status.HTTP_204_NO_CONTENT)


# =========================
# HOTELS
# =========================

class HotelListCreateView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, destination_pk):
        destination = get_object_or_404(Destination, pk=destination_pk)
        qs = HotelRecommendation.objects.filter(destination=destination)

        accommodation_type = request.query_params.get('accommodation_type')
        if accommodation_type:
            qs = qs.filter(accommodation_type=accommodation_type)

        is_active = request.query_params.get('is_active')
        if is_active is not None:
            qs = qs.filter(is_active=is_active.lower() == 'true')

        search = request.query_params.get('search')
        if search:
            qs = qs.filter(hotel_name__icontains=search) | qs.filter(location__icontains=search)

        serializer = HotelSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, destination_pk):
        destination = get_object_or_404(Destination, pk=destination_pk)
        serializer = HotelSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(destination=destination)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HotelRetrieveUpdateDestroyView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, destination_pk, pk):
        destination = get_object_or_404(Destination, pk=destination_pk)
        return get_object_or_404(HotelRecommendation, destination=destination, pk=pk)

    def get(self, request, destination_pk, pk):
        hotel = self.get_object(destination_pk, pk)
        serializer = HotelSerializer(hotel)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, destination_pk, pk):
        hotel = self.get_object(destination_pk, pk)
        serializer = HotelSerializer(hotel, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, destination_pk, pk):
        hotel = self.get_object(destination_pk, pk)
        serializer = HotelSerializer(hotel, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, destination_pk, pk):
        hotel = self.get_object(destination_pk, pk)
        hotel.delete()
        return Response({"message": "Hotel deleted."}, status=status.HTTP_204_NO_CONTENT)


# =========================
# TRANSPORT
# =========================

class TransportListCreateView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, destination_pk):
        destination = get_object_or_404(Destination, pk=destination_pk)
        qs = TransportRecommendation.objects.filter(destination=destination)

        transport_type = request.query_params.get('transport_type')
        if transport_type:
            qs = qs.filter(transport_type=transport_type)

        search = request.query_params.get('search')
        if search:
            qs = qs.filter(provider__icontains=search) | qs.filter(origin__icontains=search)

        serializer = TransportSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, destination_pk):
        destination = get_object_or_404(Destination, pk=destination_pk)
        serializer = TransportSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(destination=destination)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TransportRetrieveUpdateDestroyView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, destination_pk, pk):
        destination = get_object_or_404(Destination, pk=destination_pk)
        return get_object_or_404(TransportRecommendation, destination=destination, pk=pk)

    def get(self, request, destination_pk, pk):
        transport = self.get_object(destination_pk, pk)
        serializer = TransportSerializer(transport)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, destination_pk, pk):
        transport = self.get_object(destination_pk, pk)
        serializer = TransportSerializer(transport, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, destination_pk, pk):
        transport = self.get_object(destination_pk, pk)
        serializer = TransportSerializer(transport, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, destination_pk, pk):
        transport = self.get_object(destination_pk, pk)
        transport.delete()
        return Response({"message": "Transport option deleted."}, status=status.HTTP_204_NO_CONTENT)


# =========================
# COST BENCHMARKS
# =========================

class CostBenchmarkListCreateView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, destination_pk):
        destination = get_object_or_404(Destination, pk=destination_pk)
        qs = CostBenchmark.objects.filter(destination=destination)

        travel_style = request.query_params.get('travel_style')
        if travel_style:
            qs = qs.filter(travel_style=travel_style)

        serializer = CostBenchmarkSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, destination_pk):
        destination = get_object_or_404(Destination, pk=destination_pk)
        serializer = CostBenchmarkSerializer(data=request.data)
        if serializer.is_valid():
            travel_style = serializer.validated_data.get('travel_style')
            if CostBenchmark.objects.filter(destination=destination, travel_style=travel_style).exists():
                return Response(
                    {"error": f"Cost benchmark for '{travel_style}' already exists. Use PATCH to update."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer.save(destination=destination)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CostBenchmarkRetrieveUpdateDestroyView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, destination_pk, pk):
        destination = get_object_or_404(Destination, pk=destination_pk)
        return get_object_or_404(CostBenchmark, destination=destination, pk=pk)

    def get(self, request, destination_pk, pk):
        benchmark = self.get_object(destination_pk, pk)
        serializer = CostBenchmarkSerializer(benchmark)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, destination_pk, pk):
        benchmark = self.get_object(destination_pk, pk)
        serializer = CostBenchmarkSerializer(benchmark, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, destination_pk, pk):
        benchmark = self.get_object(destination_pk, pk)
        serializer = CostBenchmarkSerializer(benchmark, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, destination_pk, pk):
        benchmark = self.get_object(destination_pk, pk)
        benchmark.delete()
        return Response({"message": "Cost benchmark deleted."}, status=status.HTTP_204_NO_CONTENT)


# =========================
# INTERESTS
# =========================

class InterestListCreateView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        qs = Interest.objects.all().order_by('name')

        search = request.query_params.get('search')
        if search:
            qs = qs.filter(name__icontains=search)

        serializer = InterestSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = InterestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InterestRetrieveUpdateDestroyView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, pk):
        return get_object_or_404(Interest, pk=pk)

    def get(self, request, pk):
        interest = self.get_object(pk)
        serializer = InterestSerializer(interest)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        interest = self.get_object(pk)
        serializer = InterestSerializer(interest, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        interest = self.get_object(pk)
        serializer = InterestSerializer(interest, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        interest = self.get_object(pk)
        interest.delete()
        return Response({"message": "Interest deleted."}, status=status.HTTP_204_NO_CONTENT)