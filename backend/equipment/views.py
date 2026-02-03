import pandas as pd
import io
import os
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from .models import EquipmentDataset
from .serializers import EquipmentDatasetSerializer
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

class CSVUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        if not file_obj.name.endswith('.csv'):
            return Response({"error": "File is not a CSV"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Read CSV with pandas
            data = pd.read_csv(file_obj)
            
            # Required columns check
            required_columns = ['Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature']
            if not all(col in data.columns for col in required_columns):
                return Response({"error": f"Missing columns. Required: {required_columns}"}, status=status.HTTP_400_BAD_REQUEST)

            # Perform Analysis
            analysis = {
                "total_count": len(data),
                "averages": {
                    "flowrate": round(data['Flowrate'].mean(), 2),
                    "pressure": round(data['Pressure'].mean(), 2),
                    "temperature": round(data['Temperature'].mean(), 2),
                },
                "type_distribution": data['Type'].value_counts().to_dict()
            }

            # Save to database
            instance = EquipmentDataset.objects.create(
                file_name=file_obj.name,
                file=file_obj,
                summary_data=analysis
            )

            # Keep only last 5
            if EquipmentDataset.objects.count() > 5:
                ids_to_keep = EquipmentDataset.objects.order_by('-uploaded_at')[:5].values_list('id', flat=True)
                EquipmentDataset.objects.exclude(id__in=ids_to_keep).delete()

            return Response({
                "message": "File uploaded and analyzed successfully",
                "id": instance.id,
                "summary": analysis,
                "data": data.to_dict(orient='records')
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class HistoryView(APIView):
    def get(self, request):
        datasets = EquipmentDataset.objects.all()[:5]
        serializer = EquipmentDatasetSerializer(datasets, many=True)
        return Response(serializer.data)

class ReportView(APIView):
    def get(self, request, pk):
        try:
            instance = EquipmentDataset.objects.get(pk=pk)
            data = pd.read_csv(instance.file.path)
            
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="report_{pk}.pdf"'
            
            p = canvas.Canvas(response, pagesize=letter)
            p.drawString(100, 750, f"Equipment Parameter Report - {instance.file_name}")
            p.drawString(100, 730, f"Uploaded at: {instance.uploaded_at}")
            
            y = 700
            p.drawString(100, y, "Summary Statistics:")
            y -= 20
            summary = instance.summary_data
            p.drawString(120, y, f"Total Equipment: {summary['total_count']}")
            y -= 20
            p.drawString(120, y, f"Avg Flowrate: {summary['averages']['flowrate']}")
            y -= 20
            p.drawString(120, y, f"Avg Pressure: {summary['averages']['pressure']}")
            y -= 20
            p.drawString(120, y, f"Avg Temperature: {summary['averages']['temperature']}")
            
            y -= 40
            p.drawString(100, y, "Detailed Data (Top 10):")
            y -= 20
            headers = ['Name', 'Type', 'Flow', 'Press', 'Temp']
            p.drawString(100, y, f"{headers[0]:<20} {headers[1]:<10} {headers[2]:<8} {headers[3]:<8} {headers[4]:<8}")
            y -= 15
            
            for index, row in data.head(10).iterrows():
                if y < 50:
                    p.showPage()
                    y = 750
                p.drawString(100, y, f"{str(row['Equipment Name'])[:18]:<20} {str(row['Type'])[:9]:<10} {row['Flowrate']:<8} {row['Pressure']:<8} {row['Temperature']:<8}")
                y -= 15
            
            p.showPage()
            p.save()
            return response
            
        except EquipmentDataset.DoesNotExist:
            return Response({"error": "Dataset not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
