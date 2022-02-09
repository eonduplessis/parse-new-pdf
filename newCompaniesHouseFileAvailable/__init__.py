import logging

from pdf2image import convert_from_bytes

import os

import requests

import azure.functions as func


def pdf_to_png(company_name, companies_house_pdf_file_blob):
    # Store Pdf with convert_from_path function
    pages = convert_from_bytes(companies_house_pdf_file_blob.read())

    image_list = []

    i = 0     
    for page in pages:
        # Save pages as images in the pdf
        image_name = company_name + 'page'+ str(i) +'.png'
        logging.info(f"Saving image: {image_name}")
        page.save(image_name, 'PNG')
        logging.info(f"Saving image complete: {image_name}")
        image_list.append(image_name)
        i = i + 1

    del companies_house_pdf_file_blob
    del pages

    return image_list


def png_ocr(png_file_path):
    text = ""
    
    with open(png_file_path, 'rb') as f:
        text = text + " " + requests.get('https://pngocr.azurewebsites.net/api/png-ocr?code=8ia5MihwBZcv6LlgA0DN4pENERqQPo33HKnSl95NIJJk4MoOpllSkQ==', files={'image.png': f})

    return text

def clean_up_files(file_list):
    for file in file_list:
        os.remove(file)

def main(myblob: func.InputStream):
    #Updated 1
    logging.info(f"Python blob trigger function processed blob \n"
                 f"Name: {myblob.name}\n"
                 f"Blob Size: {myblob.length} bytes")

    logging.info(f"Converting blob bytestream to PNG")
    image_list = pdf_to_png(myblob.name[15:-4], myblob)
    logging.info(f"Converting blob bytestream to PNG complete")

    del myblob


    content = ""
    
    
    logging.info(f"Executing OCR on PNG payload")
    for image in image_list:
        logging.info(f"Processing image: {image}")
        text = png_ocr(image)
        logging.info(f"Processing image complete: {image} \n"
                     f"Content size: {len(text)}")
        content = content + text

    logging.info(f"Cleaning up temporary files")
    clean_up_files(image_list)
    
    logging.info(f"Processing PDF complete. \n"
                 f"Document content size: {len(content)}")
