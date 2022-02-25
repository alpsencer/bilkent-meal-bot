import urllib.request

def pdfdownloader():
    pdf_path = "http://kafemud.bilkent.edu.tr/kumanya_menusu.pdf"

    def download_file(download_url, filename):
        response = urllib.request.urlopen(download_url)    
        file = open(filename + ".pdf", 'wb')
        file.write(response.read())
        file.close()
    
    download_file(pdf_path, "PdfDownloader/guncelliste/guncelliste")