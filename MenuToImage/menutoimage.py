import fitz

def menutoimage():
  doc = fitz.open("PdfDownloader/guncelliste/guncelliste.pdf")
  page = doc.load_page(0)  # number of page
  zoom_x = 2.77777777778 # horizontal zoom
  zoom_y = 2.77777777778 # vertical zoom
  mat = fitz.Matrix(zoom_x, zoom_y)  # zoom factor 2 in each dimension
  pix = page.get_pixmap(matrix=mat)  # use 'mat' instead of the identity matrix
  output = "MenuToImage/HaftaninMenuResmi/guncelliste.png"
  pix.save(output)

  doc.close()