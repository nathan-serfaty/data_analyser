from django.http import JsonResponse, HttpResponse, Http404
import pandas as pd
import os
from django.conf import settings
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from ydata_profiling import ProfileReport
import io
from django.shortcuts import render


def index(request):
    return render(request, os.path.join(settings.BASE_DIR, 'my-cleaning-app/build/index.html'))


# Serve media files (CSV, report, etc.)
def serve_media_file(request, filename):
    file_path = os.path.join(settings.MEDIA_ROOT, filename)
    
    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/force-download')
            response['Content-Disposition'] = f'inline; filename="{filename}"'
            return response
    else:
        raise Http404("Fichier non trouvé")

# Page for file upload
def file_upload_page(request):
    return render(request, 'file_upload.html')  # Ensure this template exists

# Clean and convert numeric columns
def nettoyer_et_convertir(colonne):
    colonne_propre = colonne.astype(str)\
        .str.replace(r'[€,$,£]', '', regex=True)\
        .str.replace(',', '.', regex=False)\
        .str.strip()

    colonne_propre = colonne_propre.replace('', pd.NA)
    return pd.to_numeric(colonne_propre, errors='coerce')

@csrf_exempt
def upload_file(request):
    if request.method == 'POST':
        if 'file' not in request.FILES:
            return HttpResponse("Aucun fichier n'a été soumis. Veuillez uploader un fichier.", status=400)
        
        uploaded_file = request.FILES['file']
        file_name = uploaded_file.name.lower()

        try:
            # Process file based on its extension
            if file_name.endswith('.xlsx') or file_name.endswith('.xls'):
                df = pd.read_excel(uploaded_file, keep_default_na=True)
            elif file_name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            elif file_name.endswith('.parquet'):
                df = pd.read_parquet(uploaded_file)
            else:
                return HttpResponse("Format de fichier non pris en charge. Veuillez uploader un fichier Excel, CSV, ou Parquet.", status=400)
            
            # Clean numeric columns
            colonnes_numeriques = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
            for col in colonnes_numeriques:
                df[col] = nettoyer_et_convertir(df[col])

            # Generate CSV in buffer
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            csv_buffer.seek(0)

            # Save CSV to media folder
            csv_output_path = os.path.join(settings.MEDIA_ROOT, 'donnees_nettoyees.csv')
            with open(csv_output_path, 'w') as csv_file:
                csv_file.write(csv_buffer.getvalue())

            # Generate analysis report
            rapport_analyse_output = os.path.join(settings.MEDIA_ROOT, 'rapport_analyse.html')
            profile = ProfileReport(df, title="Rapport d'analyse", explorative=True)
            profile.to_file(rapport_analyse_output)

            # Handle dynamic URL generation for media files
            protocol = 'https' if request.is_secure() else 'http'
            host = request.get_host()
            csv_url = f'{protocol}://{host}/media/donnees_nettoyees.csv'
            report_url = f'{protocol}://{host}/media/rapport_analyse.html'

            # Return URLs for downloading the CSV and report
            response_data = {
                "csv_url": csv_url,
                "report_url": report_url
            }

            return JsonResponse(response_data)

        except Exception as e:
            return HttpResponse(f"Erreur lors du traitement du fichier : {str(e)}", status=500)
    else:
        return HttpResponse("Requête invalide. Utilisez POST pour uploader des fichiers.", status=405)
