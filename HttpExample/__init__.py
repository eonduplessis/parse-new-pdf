import logging

from rpy2 import robjects
import pytesseract
from PIL import Image
from pdf2image import convert_from_path

import azure.functions as func

def get_pdf_file_location():
    return 'companies_house_document.pdf'

def pdf_to_png(pdfFilePath):
    # Store Pdf with convert_from_path function
    images = convert_from_path(pdfFilePath)
    image_list = []

    for i in range(len(images)):
        # Save pages as images in the pdf
        image_name = 'page'+ str(i) +'.png'
        images[i].save(image_name, 'PNG')
        image_list.append(image_name)
    
    return image_list

def png_ocr(png_file_path):
    text = pytesseract.image_to_string(Image.open(png_file_path))
    return text

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    if name:
        return func.HttpResponse(f"Hello, {name}. This HTTP triggered function executed successfully.")
    else:
        location = get_pdf_file_location()

        image_list = pdf_to_png(location)

        content = ""

        for image in image_list:
            text = png_ocr(image)
            content = content + text

        return func.HttpResponse(
             #"This HTTP triggered function executed successfully! Pass a name in the query string or in the request body for a personalized response.",
             content,
             status_code=200
        )
