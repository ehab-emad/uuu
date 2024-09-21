#### ----------------------------Read Me----------------------------####
"""
Structure of the PDF Report feature:
-The customCanvas class creates the document template with logo, page numeration and lines and is used for all pages
-The PDFReport class is used to create the report and its content using a set of methods described below:
    -__init__ initializes the object and is used to set basic settings of the report
    -_header_footer creates the header and footer tables and is printed on all pages
    -stacked_barchart_make creates the comparative barcharts automatically, when the data is fed in the correct format. A few attributes can bes set for formatting.
    -autoScale is used by stacked_barchart_make to automatically scale the y-axis according to the given values and a user specified number of increments
    -createReport puts the report on the custom canvas and returns ist to the print_pdf.py, where it is then presented to the user as a PDF file disposition
    -reportContent is where all the content that is used to create the report is gathered from the database and objects and then processed to show in the defined layout

Further details:
-In print_pdf.py, use boolean save_file to choose of report should be saved on server or not. !!! Will overwrite exports from the same day!!!
-The list hexColors defines the colours that are used when generating charts and diagrams as well as legends. It can be extended or modified to suit the desired style

Future features to be included:
-Finish footer feature to follow QM specification
    -As soon as Analysis Comparison can be versioned, the report should inherit the version number
    -The report author and release will be the project owner, as soon as this attribute is specified in later releases
    -The propject scope should be defined somewhere and then be included in the footer correctly
-Automatic naming of processes should be more precise and not start with "Idemat 2022", as this does not help to differentiate processes and complicates the layout of charts and diagrams

To do's:
-Check number formatting!
-Check autoscale method with negative values

"""
#### ---------------------------------------------------------------####

#imports
from django.shortcuts import get_object_or_404
from django.db import models
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import *
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.lib import colors as colours
from reportlab.lib.colors import HexColor as hexcol
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import  Drawing, Rect, String
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.legends import Legend, TotalAnnotator
from django.contrib.staticfiles.storage import staticfiles_storage
from reportlab.lib.utils import ImageReader
import datetime, os
import numpy as np
from decouple import config
from django.conf import settings
from django.core.files.storage import default_storage
#create custom canvas with page numbers, lines and logo
class CustomCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []
        self.width, self.height = landscape(A4)

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def drawPageNumber(self, page_count):
        self.setFont('Helvetica', 10)
        self.drawRightString(self.width-2*cm, 0.75 * cm,
                             '%s/%s' % (self._pageNumber, page_count))

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.drawPageNumber(num_pages)
            self.drawLogos()
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def drawLogos(self):
            self.saveState()
            self.setStrokeColorRGB(0, 0, 0)
            self.setLineWidth(1.0)

            from website.models import Organisation
            current_organisation = Organisation.get_current_organisation()
            src_path = current_organisation.get_banner_path()

            if default_storage.exists(src_path):
                image_path = src_path
            else:
                fallback_image_path = os.path.join('website/customer_banner/404.png')
                if staticfiles_storage.exists(fallback_image_path):
                    image_path = staticfiles_storage.path(fallback_image_path)
                else:
                    # Handle the case where even the fallback image is missing
                    raise FileNotFoundError("Both the primary and fallback images are missing.")
            # Load the image and get its dimensions
            image = ImageReader(image_path)
            image_width, image_height = image.getSize()
            # Desired width in cm
            desired_width_cm = 4 * cm
            desired_height_cm = (image_height / image_width) * desired_width_cm  # Calculate height preserving aspect ratio

            # X, Y positioning, adjust Y based on the calculated height
            x_position = self.width - desired_width_cm - 2 * cm
            y_position = self.height - desired_height_cm - 1.5 * cm

            self.drawImage(
                image_path,
                x_position,
                y_position,
                width=desired_width_cm,
                height=desired_height_cm,
                preserveAspectRatio=True
            )

            # Draw lines at consistent positions
            self.line(2 * cm, self.height - 4.75 * cm, self.width - 2 * cm, self.height - 4.75 * cm)
            self.line(2 * cm, 1.75 * cm, self.width - 2 * cm, 1.75 * cm)

            self.restoreState()


#Create PDF Report on custom canvas
class PdfReport_one_column:
    def __init__(self, buffer, analysis_id):
        from EcoMan.models import Analysis
        # create buffer
        self.buffer = buffer
        # store analysis ID and dictionary for loop creation from dictionary
        self.analysis_id = analysis_id

        # here it will be decided if report will be printed for single analysis or for analysis_comparison
        query = Analysis.objects.filter(pk = self.analysis_id)
        if query:
            self.analysis = query.get()
        self.analysis_dict = self.analysis.as_dict()

        # Report settings from analysis
        self.include_object_ids = self.analysis.analysis_settings.report_include_object_ids
        self.include_title_and_summ_pages = self.analysis.analysis_settings.report_include_title_and_summ_pages
        self.include_part_list_pages = self.analysis.analysis_settings.report_include_part_list_pages
        self.include_processes_list_pages = self.analysis.analysis_settings.report_include_processes_list_pages
        self.include_goal_definition =  self.analysis.analysis_settings.report_include_goal_definition
        self.include_scope_definition = self.analysis.analysis_settings.report_include_scope_definition
        self.include_circularity = self.analysis.analysis_settings.include_circularity
        self.include_utilisation = self.analysis.analysis_settings.include_utilisation
        self.user_id_visible = self.analysis.analysis_settings.report_is_anonymized


        # set some characteristics for pdf document
        self.pageSize = landscape(A4)
        self.width, self.height = self.pageSize
        self.Story = []
        self.doc = SimpleDocTemplate(
            self.buffer,
            showBoundary=0,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=5*cm,
            bottomMargin=2*cm,
            height=self.height,
            width=self.width,
            pagesize=self.pageSize)

        #set colours for report
        hexColors = ['#455561','#b9254c','#d92446','#e14d47','#e86b47','#ed8648','#f29f48','#f0b872','#ead0af','#e4e5e6']
        self.coloursList = []
        for code in hexColors:
            self.coloursList.append(hexcol(code))

    def _header_footer(self, canvas, doc):

        #get analysis dict and rename locally for ease of use
        ac = self.analysis

        #create canvas
        canvas.saveState()
        styles = getSampleStyleSheet()

        #Header Title
        header_title = Paragraph('QLCA Report', styles['Heading1'])
        w, h = header_title.wrap(doc.width, doc.topMargin)
        header_title.drawOn(canvas, doc.leftMargin, doc.height + doc.topMargin -h)

        #Header Table
        timestamp = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
        table_data = [['Analysis Name', 'Project', 'Signature Date'],
                      [ ac.name, ac.project_model.reference_project.name, timestamp]]
        if self.include_object_ids == True:
            table_data[0].insert(1, 'Analysis ID')
            table_data[1].insert(1, ac.id)
        if self.user_id_visible == True:
            table_data[0].insert(-1, 'Owner')
            table_data[1].insert(-1, ac.owner)

        header_table = Table(table_data, colWidths=doc.width/len(table_data[0]))

        header_table.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'LEFT'),('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold')]))
        w, h = header_table.wrap(doc.width, doc.topMargin)
        header_table.drawOn(canvas, doc.leftMargin, doc.height + doc.topMargin -2*h)

        #Footer Table
        from website.models import Organisation
        current_organisation = Organisation.get_current_organisation()
        django_customer_full_name = current_organisation.full_name
        django_customer_short_name = current_organisation.name
        application_version = os.environ.get('APP_ECOMAN_VERSION', config('APP_ECOMAN_VERSION', default='1.0.0'))
        footer_data = [[ django_customer_short_name + ' QLCA Report', 'Author: ' + ac.owner.reference_projectuser.user.username, 'Software Version: '+ application_version, 
                         'Scope: ' + django_customer_full_name,  ac.analysis_settings.get_protection_class_display()]]
        footer_table = Table(footer_data,) #colWidths=doc.width/(len(footer_data[0])))
        footer_table.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'LEFT'),
                                          ('FONTNAME', (0,0), (-1,0), 'Helvetica')]))
        w, h = footer_table.wrap(doc.width, doc.bottomMargin)
        footer_table.drawOn(canvas, doc.leftMargin, 1.5*h)

        #Release Canvas
        canvas.restoreState()


    #autoscale function for barcharts
    def autoScale(self, max_value, min_value, desired_steps):

        #generate alist of typical multiples for displaying barcharts
        base_multiples = np.array([10, 15, 20, 25, 30, 50])
        final_multiples = np.copy(base_multiples)
        up = base_multiples
        down = base_multiples
        n = 4
        for n in range(n):
            times_10 = np.multiply(up,10)
            by_10= np.around(np.multiply(down, 1/10),5)
            temp_multiples = np.concatenate((by_10, final_multiples, times_10))
            up = times_10
            down = by_10
            final_multiples = temp_multiples

        multiples = final_multiples
        steps = np.linspace(min_value, max_value, desired_steps + 1) #remove outer bracket with np.abs()
        step_size = np.min(np.abs(np.diff(steps)))
        rounded_step = multiples[np.argmin(np.abs(multiples - step_size))]
        value_min = np.floor(min_value / rounded_step) * rounded_step
        value_max = np.ceil(max_value / rounded_step) * rounded_step

        return value_max, value_min, rounded_step

    #method to create barcharts
    def stacked_barchart_maker(self, scale_factor, data, legend_items, categories, unit, desired_steps, decimals = 3):

        #scale_factor should be between 0-0.5 for optimal results
        if len(data) == 0 or data[0] == (0, None):
            styles = getSampleStyleSheet()
            txt = 'The user has not specified sufficient data to generate this chart.'
            self.Story.append(Paragraph(txt, styles['Normal']))
            return

        barchart = Drawing(self.doc.width, self.doc.width*scale_factor)

        #Chart Creation
        bc = VerticalBarChart()
        bc.height = barchart.height*0.8
        bc.width = bc.height
        bc.y = (barchart.height-bc.height)/2
        bc.x = bc.y*2
        bc.data = data
        bc.strokeColor = None

        #scale the y-axis for max, min and step using the autoscale function
        if len(data[0])>1:
            max_data =sum(i for i, j in data if i is not None and i >= 0)
            min_data =sum(i for i, j in data if i is not None and i < 0)
        else:
            max_data =sum(i[0] for i in data if i is not None and i[0] >= 0)
            min_data =sum(i[0] for i in data if i is not None and i[0] < 0)            
        max_min_step = self.autoScale(max_data,min_data,desired_steps )
        bc.valueAxis.valueMax = max_min_step[0]
        bc.valueAxis.valueMin = max_min_step[1]
        bc.valueAxis.valueStep = max_min_step[2]
        bc.valueAxis.labelTextFormat = '%g '+ unit

        #format category axis (x-axis)
        bc.categoryAxis.labels.boxAnchor = 'n'
        bc.categoryAxis.labels.dx = 0
        bc.categoryAxis.labels.dy = -2 if max_min_step[1] == 0 else abs(max_min_step[1])/(max_min_step[0]-max_min_step[1])*bc.height
        bc.categoryAxis.labels.angle = 0
        bc.categoryAxis.categoryNames = [categories[0]]
        bc.categoryAxis.style = 'stacked'
        colouring = []
        for i, s in enumerate(bc.data):
            bc.bars[i].fillColor = self.coloursList[i % len(self.coloursList)]
            colouring.append(bc.bars[i].fillColor)
        bc.barWidth = 5

        #Create total weight labels and two column legend with headers
        try:
            bc._computeBarPositions()
        except:
            pass
        else:
            
            #Total weight label left
            bp_left = [p[0] for p in bc._barPositions if all(p[0])]
            spacer = 5
            coord_left =[bp_left[0][0]+bp_left[0][2]/2,bp_left[0][1]+ sum(p[3] for p in bp_left if p[3] >=0)+spacer]
            weight_left = sum(tup[0] for tup in data if tup[0] is not None)
            weight_string_left = String(coord_left[0],coord_left[1],'Total: '+f"{weight_left:.{decimals}f}"+' '+unit, fontSize=10, textAnchor= 'middle')
            barchart.add(weight_string_left)

            #Legend Left Creation
            cleaned_data= [tup[0] for tup in data if tup[0] is not None]
           
            labels_subCols = [(name[0:20],(f"{weight:.{decimals}f}"+' '+ unit)) for  name, weight in zip(legend_items, cleaned_data)]
            for i, s in enumerate(legend_items):
                bc.bars[i].name = s[0:20]
            cNP = list(zip(colouring, labels_subCols))
            cNP_left = cNP[:len([tup for tup in bc.data if tup[0]!=None])]
            cNP_right = cNP[len([tup for tup in bc.data if tup[0]!=None]):]
            cNP_left_rev = list(reversed(cNP_left))
            cNP_right_rev= list(reversed(cNP_right))
            legend_left = Legend()
            legend_left.alignment = 'right'
            legend_left.x = 2*bc.x + bc.width
            legend_left.y = barchart.height - 2*bc.y + 30
            legend_left.subCols.rpad = 5
            legend_left.colorNamePairs = cNP_left_rev
            legend_left.deltax = 5
            legend_left.deltay = 10
            legend_left.columnMaximum = 25 # len(legend_items)
            legend_left.variColumn = 1
            legend_header_left = String(legend_left.x, legend_left.y+bc.y/2, categories[0], fontSize=10, fontName = 'Times-Bold', textAnchor= 'start')
            legend_left_width = max(legend_left._calculateMaxBoundaries(cNP_left_rev)[0]) + 2*legend_left.deltax + legend_left.subCols.rpad
            legend_left_height = legend_left._calcHeight()
            barchart.add(legend_left)
            barchart.add(legend_header_left)

        if any(item[0] is None for item in data) and 'legend_left' in locals():
            #Total weight label right
            bc._computeBarPositions()
            bp = [p[0] for p in bc._barPositions if all(p[0])] + [p[1] for p in bc._barPositions if all(p[1])]
            bp_right = [p[1] for p in bc._barPositions if all(p[1])]
            spacer = 3
            coord_right =[bp_right[0][0]+bp_right[0][2]/2,bp_right[0][1]+ sum(p[3] for p in bp_right if p[3] >=0)+spacer]
            weight_right = sum(tup[1] for tup in data if tup[1] is not None)
            weight_string_right = String(coord_right[0],coord_right[1],'Total: ' + f"{weight_right:.{decimals}f}" + ' ' + unit, fontSize=10, textAnchor='middle')
            barchart.add(weight_string_right)


        #Add Chart to drawing and append to story
        barchart.add(bc)
        barchart.hAlign = 'LEFT'
        self.Story.append(barchart)

        #Check legend height and adjust Drawing size if necessary

        if 'legend_left' in locals():
            legend_height = legend_left._calcHeight()
        else:
            legend_height = 0
        required_height = 2*bc.y + legend_height
        if required_height > barchart.height:
            delta = required_height - barchart.height
            self.Story.append(Spacer(1,delta))


    def createReport(self, request):
        # build document, write to buffer and return pdf
        self.reportContent(request)
        self.doc.build(self.Story,canvasmaker=CustomCanvas, onFirstPage=self._header_footer, onLaterPages=self._header_footer)
        pdf = self.buffer.getvalue()
        self.buffer.close()
        return pdf
    
    def createReportForAnalysis(self, request):
        # build document, write to buffer and return pdf
        self.reportContent(request)
        self.doc.build(self.Story,canvasmaker=CustomCanvas, onFirstPage=self._header_footer, onLaterPages=self._header_footer)
        pdf = self.buffer.getvalue()
        self.buffer.close()
        return pdf

    def reportContent(self, request):

        #Import and creation of local objects for report
        from EcoMan.models import Instance_Idemat_Database_Process
        analysis = self.analysis
        concept = self.analysis.concept_model
        vehicle = concept.vehicles.all()[:1].get().reference_vehicle
        energy = vehicle.energy_source_model
        production = vehicle.production_rate_model
        utilisation = None #analysis.utilisation_instance_model.first()
        primary_property = analysis.primary_property
        secondary_properties = analysis.secondary_properties
        lca_parts_all = analysis.lca_part_models.all()
       
        #define units for weight
        weight_unit =""
        if analysis.analysis_settings.weight_units == "KILOGRAMS":
            weight_unit ="[kg]"
        if analysis.analysis_settings.weight_units == "GRAMS":
            weight_unit ="[g]"

        decimals = analysis.analysis_settings.weight_decimal_points
        weight_concept = analysis.get_weight_in_units(analysis.analysis_settings.weight_units)
        lca_processes_all = Instance_Idemat_Database_Process.objects.filter(lca_part_instance__in= lca_parts_all, is_active= True)
        #import styles and add metadata
        styles = getSampleStyleSheet()
        styles.add
        styles['Heading3'].fontName = 'Helvetica-Bold' #remove Italic property from H3
        self.doc.title = 'EDAG QLCA Report'
        self.doc.author = 'Author'
        self.doc.subject = 'Quick Life Cycle Assessment'

        #set colours for report
        hexColors = ['#455561','#b9254c','#d92446','#e14d47','#e86b47','#ed8648','#f29f48','#f0b872','#ead0af','#e4e5e6']
        coloursList = []
        for code in hexColors:
            coloursList.append(hexcol(code))

        ########################## Section 1 ################################

        #Header
        self.Story.append(Paragraph('Quick Life Cycle Assessment', styles['Heading2']))
        self.Story[-1].keepWithNext = True

        #Goal Definition
        if self.include_goal_definition == True:
            self.Story.append(Paragraph('Goal Definition', styles['Heading3']))
            self.Story[-1].keepWithNext = True
            goal = Paragraph(analysis.goal_definition , styles['Normal'])
            self.Story.append(goal)

        #Scope Definition
        if self.include_scope_definition == True:
            self.Story.append(Paragraph('Scope Definition', styles['Heading3']))
            self.Story[-1].keepWithNext = True
            scope = Paragraph(analysis.scope_definition, styles['Normal'])
            self.Story.append(scope)

        #Title and Summary Tables and Charts
        if self.include_title_and_summ_pages == True:

            if analysis.analysis_settings.is_automotive:
                #Vehicle Data Header
                self.Story.append(Paragraph('Vehicle Specification', styles['Heading3']))
                self.Story[-1].keepWithNext = True
                #Overview table from objects
                overview_data = [['Vehicle name', vehicle.name,'Vehicle class', vehicle.get_vehicle_classification_display().split("(")[0]],
                                ['Lifetime [years]', vehicle.life_time_in_years,'Lifetime [km]', vehicle.life_distance_in_km],
                                ['Target weight [kg]', vehicle.target_weight, 'Weight estimation [kg]', vehicle.estimated_weight],
                                ['Primary Energy', energy.get_energysource_1_display(),'Secondary Energy',energy.get_energysource_2_display()]]
                overview_table = Table(overview_data, colWidths=self.doc.width/4) #
                overview_table.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'LEFT'),
                                                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                                                    ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
                                                    ('FONTNAME', (2,0), (-2,-1), 'Helvetica-Bold')]))
                self.Story.append(overview_table)

            #Comparison of Concepts from objects
            carbon_footprint = 0.00
            for part in lca_parts_all:
                carbon_footprint += round(part.as_dict()['lca_result']['carbon_footprint'],3)

            self.Story.append(Paragraph('Concept summary', styles['Heading3']))
            self.Story[-1].keepWithNext = True
            comparison_data =   [
                                ['Name', analysis.name],
                                ['Number of different parts', lca_parts_all.count()],
                                ['Total number of parts', sum(part.multiplier for part in lca_parts_all)],
                                ['Weight ' + weight_unit,  f"{weight_concept:.{decimals}f}"],
                                ['GWP CO2eq' + '[kg]', f"{carbon_footprint:.{decimals}f}"]
                                ]
            if utilisation is not None and self.include_utilisation == True:
                comparison_data.append(['Emissions CO2eq [g/km]',"{:g}".format(round(utilisation.engwpperkm_vehicle_for_analysis_left*10,2))+'*',str(round(utilisation.engwpperkm_vehicle_for_analysis_right*10,2))+'*'])
            comparison_table = Table(comparison_data,colWidths=[self.doc.width*0.6,self.doc.width*0.4])
            comparison_table.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'LEFT'),
                                                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                                                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                                                ('FONTNAME', (0,0), (-3,-1), 'Helvetica-Bold')]))
            self.Story.append(comparison_table)
            self.Story.append(PageBreak())
            if utilisation is not None:
                self.Story[-1].keepWithNext = True
                self.Story.append(Paragraph('*Assuming a utilisation lifetime of ' + str(utilisation.quantity) + ' km with additional loading of ' + str(utilisation.goods_weight) + ' kg at ' + str(utilisation.goods_weight_utilisation) + '%'+' utilisation.'))

            #Weight Comparison
            self.Story.append(Paragraph('Weight', styles['Heading3']))
            self.Story[-1].keepWithNext = True

            #dataprep for stacked barchart
            weight_data = []
            weight_legend_items = []
            weight_data.append((analysis.get_weight_in_units(),))
            weight_legend_items.append(analysis.name)
            weight_categories = [analysis.name]


            #barchart maker
            self.stacked_barchart_maker(0.25, weight_data, weight_legend_items, weight_categories, weight_unit, 5)

            # Page Break
            self.Story.append(PageBreak())


        ####################################### Section 2 #############################################

        #Check if Partlist Pages are wanted
        if self.include_part_list_pages == True:
            #Page Header
            if lca_parts_all.exists():
                self.Story.append(Paragraph('Overview of Parts', styles['Heading2']))
                self.Story[-1].keepWithNext = True

            #Parts Looper from objects in table format (one table per part)

            categories = []
            data_left = []
            data_right = []


            if len(lca_parts_all) != 0:
                categories.append('Reference')


            header = Table([['Part Name', 'Part Properties', '']],colWidths=[self.doc.width/2,self.doc.width/4,self.doc.width/4])
            header.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'LEFT'),
                                        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                                        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                                        ('LINEBELOW', (0,0), (-1,0), 1.5, colours.black)]))

            for category in categories:

                if category == 'Reference':
                    partlist = lca_parts_all
                    datasets = [data_left]
                    commodity =''
                    data_left.append(header) if len(data_left)==0 else None

                for dataset in datasets:
                    for part in partlist:
                        data = []
                        weight = part.get_weight_conceptman(units=analysis.analysis_settings.weight_units)
                        data.extend([[part.part_model.name,'Weight' + weight_unit, f"{weight:.{decimals}f}"],
                                    ['%s'%commodity,'Instances',str(part.multiplier)]])
                        if self.include_object_ids == True:
                            data.extend([['','ID',str(part.part_model.id)]])
                        #Configure word wrap
                        s = getSampleStyleSheet()
                        s = s["BodyText"]
                        s.wordWrap = 'CJK'
                        data_wrapped = [[Paragraph(cell, s) for cell in row] for row in data]
                        single_part = Table(data_wrapped,colWidths=[self.doc.width/2,self.doc.width/4,self.doc.width/4])
                        single_part.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'LEFT'),
                                                        ('VALIGN', (0,0), (-1,-1), 'TOP'),
                                                        ('SPAN', (0,0), (0,1)),
                                                        ('LINEBELOW', (1,0), (-1,-2), 0.25, colours.lightgrey),
                                                        ('LINEBELOW', (0,-1), (-1,-1), 0.25, colours.black)]))
                        dataset.append(single_part)

            overall_data = [['Concept: '+ analysis.name]]

            for i in range(len(data_left)):
                        sub_list = []
                        if i < len(data_left):
                            sub_list.append(data_left[i])

                        overall_data.append(sub_list)

            table = Table(overall_data,colWidths=[self.doc.width], repeatRows=1)
            table.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'LEFT'),
                                        ('VALIGN', (0,0), (-1,-1), 'TOP'),
                                        ('LEFTPADDING', (0,1), (-1,-1), 0),
                                        ('RIGHTPADDING', (0,0), (-1,-1), 0),
                                        ('BOTTOMPADDING', (0,1), (-1,-1), 0),
                                        ('TOPPADDING', (0,0), (-1,-1), 0),
                                        ('LINEBELOW', (0,0), (-1,0), 1.5, colours.black),
                                        ('LINEBEFORE', (1,0), (-1,-1), 1.5, colours.black),
                                        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                                        ('FONTSIZE', (0,0), (-1,0), 10)]))
            self.Story.append(table)

        ####################################### Section 3 #############################################

        #Check if process list pages are required
        if self.include_processes_list_pages == True:
            #Process Looper from objects in table format (multiple small tables)
            if lca_processes_all.exists():
                self.Story.append(Paragraph('Overview of Processes (per part instance)', styles['Heading2']))
                self.Story[-1].keepWithNext = True
                self.Story.append(Paragraph('The QLCA primary property is ' + primary_property.verbose_name + '.' , styles['Normal']))
                self.Story[-1].keepWithNext = True
                if primary_property.name == 'carbon_footprint':
                    self.Story.append(Paragraph('GWP Calculation is performed according to ReCiPe 2016.', styles['Normal']))
                    self.Story[-1].keepWithNext = True

            phases=[('LCASTEP1','Upstream'),('LCASTEP2','Core'),('LCASTEP3','Downstream'),('LCASTEP4','Circularity')]
            categories = []
            if len(lca_parts_all) != 0:
                categories.append('Concept: ' + analysis.name)

            for phase, phasename in phases:
                if lca_processes_all.filter(lca_step = phase).exists():
                    current_phase = phasename
                    self.Story.append(Paragraph(current_phase+' Processes', styles['Heading3']))
                    self.Story[-1].keepWithNext = True
                    data_left = []
                    data_right = []
                    phase_processes = Instance_Idemat_Database_Process.objects.none()
                    for category in categories:
                        header = Table([['Part Name','Process Name', 'Process Properties', '']],colWidths=[self.doc.width/4,self.doc.width/4,self.doc.width/4,self.doc.width/4])
                        header.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'LEFT'),
                                                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                                                    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                                                    ('LINEBELOW', (0,0), (-1,0), 1.5, colours.black)]))
            
                        phase_processes =lca_processes_all.filter(lca_step = phase).order_by('lca_part_instance__created_at').all()
                        data_left.append(header)

                        if phase_processes:
                            for process in phase_processes:
                                part = lca_parts_all.filter(lca_process_model = process).get()
                                data = []
                                data.extend([[part.part_model.name, process.name, 'Quantity', f"{process.process_quantity:.{decimals}f}"],
                                            ['','','Unit',process.process_model.unit],
                                            ['','',primary_property.unit,f"{getattr(process.results_model, primary_property.name):.{decimals}f}"]])
                                if process.process_total_quantity > process.process_quantity:
                                    data.extend([['', '', 'MEQ [%]', str(round((process.process_total_quantity/process.process_quantity)*100, 2))]])
                                if phasename == 'Circularity' and part.circularity_process_model.ispartreused == True:
                                    data.extend([['','','Reuse Interval [km]', str(part.circularity_process_model.lifetimeinkm)]])
                                    data[0][0] = data[0][0] + '\n(Part reused)'
                                if self.include_object_ids == True:
                                    data.extend([['','','ID',str(process.id)]])
                                if process.process_flag != 'REF_CORRECT':
                                    data.extend([['','','Process flag',str(process.PROCESS_FLAG[[x[0] for x in process.PROCESS_FLAG].index(process.process_flag)][1])]])

                                data.extend([['','','Calculation flag',str(process.CALC_FLAG[[x[0] for x in process.CALC_FLAG].index(process.calculation_flag)][1])]])
                                #Configure word wrap
                                s = getSampleStyleSheet()
                                s = s["BodyText"]
                                s.wordWrap = 'CJK'
                                data_wrapped = [[Paragraph(cell, s) for cell in row] for row in data]
                                single_process = Table(data_wrapped,colWidths=[self.doc.width/4,self.doc.width/4,self.doc.width/4,self.doc.width/4])
                                single_process.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'LEFT'),
                                                                    ('VALIGN', (0,0), (-1,-1), 'TOP'),
                                                                    ('SPAN', (0,0), (0,-1)),
                                                                    ('SPAN', (1,0), (1,-1)),
                                                                    ('LINEBELOW', (2,0), (-1,-2), 0.25, colours.lightgrey),
                                                                    ('LINEBELOW', (0,-1), (-1,-1), 0.25, colours.black)]))
                                data_left.append(single_process)


                    overall_data = [['Concept: ' + analysis.name,]]

                    for i in range(len(data_left)):
                        sub_list = []
                        if i < len(data_left):
                            sub_list.append(data_left[i])
                        else:
                            sub_list.append('')
                        overall_data.append(sub_list)

                    table = Table(overall_data,colWidths=[self.doc.width,self.doc.width], repeatRows=2)
                    table.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'LEFT'),
                                                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                                                ('LEFTPADDING', (0,1), (-1,-1), 0),
                                                ('RIGHTPADDING', (0,0), (-1,-1), 0),
                                                ('BOTTOMPADDING', (0,1), (-1,-1), 0),
                                                ('TOPPADDING', (0,0), (-1,-1), 0),
                                                ('LINEBELOW', (0,0), (-1,0), 1.5, colours.black),
                                                ('LINEBEFORE', (1,0), (-1,-1), 1.5, colours.black),
                                                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                                                ('FONTSIZE', (0,0), (-1,0), 10)]))
                    self.Story.append(table)

            # Page Break
            self.Story.append(PageBreak())


        ################################# Section 4 ##############################################

        #Header
        self.Story.append(Paragraph('Charts and Diagrams', styles['Heading2']))

        #Weight Comparison by parts
        self.Story.append(Paragraph('Weight Comparison by Parts', styles['Heading3']))
        self.Story[-1].keepWithNext = True
        #dataprep for stacked barchart
        weight_data = []
        weight_legend_items = []
        for part in lca_parts_all.order_by('created_at'):
            weight = part.get_weight_conceptman(units=analysis.analysis_settings.weight_units) * part.multiplier
            weight_data.append((weight, ))
            weight_legend_items.append(str(part.multiplier) + ' x ' + part.part_model.name + '=')

        weight_categories = [analysis.name]

        #barchart maker
        self.stacked_barchart_maker(0.4, weight_data, weight_legend_items, weight_categories,'kg', 5)

        #GWP Comparison
        self.Story.append(Paragraph('Concepts ' + primary_property.verbose_name + ' Comparison by Parts', styles['Heading3']))
        self.Story[-1].keepWithNext = True

        #dataprep
        gwp_data = []
        gwp_legend_items = []
        for part in lca_parts_all.order_by('created_at'):
            gwp_data.append((round(part.as_dict()['lca_result'][primary_property.name],3), ))
            gwp_legend_items.append(str(part.multiplier) + ' x ' + part.part_model.name)
        gwp_categories = [analysis.name]
        #barchart maker
        self.stacked_barchart_maker(0.4, gwp_data, gwp_legend_items, gwp_categories, primary_property.unit, 5, decimals)

        #GWP Comparison by Processes
        self.Story.append(Paragraph('Concepts ' + primary_property.verbose_name + ' Comparison by Processes', styles['Heading3']))
        self.Story[-1].keepWithNext = True

        #dataprep
        gwp_data = []
        gwp_legend_items = []
        for process in lca_processes_all.order_by('lca_part_instance__created_at'):
            part = lca_parts_all.filter(lca_process_model = process).get()
            gwp_data.append((round(getattr(process.results_model, primary_property.name)*part.multiplier,3),))
            gwp_legend_items.append(process.name)

        gwp_categories = [analysis.name]

        #barchart maker
        self.stacked_barchart_maker(0.4, gwp_data, gwp_legend_items, gwp_categories, primary_property.unit, 5)

        # # Page Break
        self.Story.append(PageBreak())

        ############################### Section 5 (Optional, yet to be integrated/requested) #############################################

        # if self.include_title_and_summ_pages == True:
        #     self.Story.append(Paragraph('Conclusion', styles['Heading2']))
        #     self.Story[-1].keepWithNext = True
        #     #Summary
        #     self.Story.append(Paragraph('Summary', styles['Heading3']))
        #     self.Story[-1].keepWithNext = True
        #     text_list = ["This life cycle assessment evaluates the environmental impact of a product over its entire life cycle.",
        #                 "The results of the assessment suggest that the product has a positive impact on the environment.",
        #                 "The analysis revealed that the product had a low carbon footprint with an average of 0.2 kg of CO2 per unit.",
        #                 "The assessment also found that the product had a minimal amount of waste generated over its life cycle.",
        #                 "The findings of this life cycle assessment suggest that the product is an environmentally friendly option."]
        #     txt = ''
        #     for _ in range(random.randint(1, len(text_list))):
        #         txt += text_list[random.randint(0, len(text_list) - 1)] + ' '
        #     txt = txt*4
        #     description = Paragraph(txt, styles['Normal'])
        #     self.Story.append(description)

        #     #Outlook
        #     self.Story.append(Paragraph('Outlook', styles['Heading3']))
        #     self.Story[-1].keepWithNext = True
        #     text_list = ["This life cycle assessment provides an important insight into the environmental impact of the product.",
        #                 "Continued research and development of the product could further reduce its environmental impact.",
        #                 "The results of the assessment suggest that the product has a positive impact on the environment.",
        #                 "This assessment provides an opportunity to compare the environmental performance of the product to other similar products.",
        #                 "The findings of this life cycle assessment can be used to inform decisions about the product's environmental impact in the future."]
        #     txt = ''
        #     for _ in range(random.randint(1, len(text_list))):
        #         txt += text_list[random.randint(0, len(text_list) - 1)] + ' '
        #     txt = txt*4
        #     description = Paragraph(txt, styles['Normal'])
        #     self.Story.append(description)
