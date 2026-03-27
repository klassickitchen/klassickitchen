import os

from odoo import api, fields, models, _
from odoo.tools.safe_eval import safe_eval
import base64
from odoo.exceptions import UserError

import io
import xlrd
# import logging
from odoo.tools import config
import tempfile
import zipfile
import openpyxl
from io import BytesIO
import xlsxwriter


# _logger = logging.getLogger(__name__)


class UiPython(models.Model):
    _name = 'ui.python'
    _description = 'Ui Python'
    _rec_name = 'rec_name'

    DEFAULT_ENV_VARIABLES = """ #Available variables:
    #  - self: Current Object
    #  - self.env: Odoo Enviroment on which the action is triggered
    #  - self.env.user: Return the current user (as an instance)
    #  - self.env.is_system: Return whether the current user has group "settings", or is in superuser mode.
    #  - self.env.is_admin: Return whether the current user has group "Access Rights", or is in superuser mode.
    #  - self.env.is_superuser: Return Whether the enviroment is in superuser mode.
    #  - self.env.company: Return the current company (as an instance)
    #  - self.env.companies: Return a recordset of the enabled campanies by the user  
    #  - self.env.lang: Return the current language code"""

    rec_name = fields.Char(default='Ui Python', readonly=1, invisible=True)
    model_id = fields.Many2one('ir.model', string='Model')
    python_code = fields.Text(string='Python Code')
    results = fields.Text(string='Results')
    helpful_commands = fields.Text(string='Helpful Commands', default=DEFAULT_ENV_VARIABLES)
    worksheet = fields.Binary('Attach Excel')
    image_zip_file = fields.Binary(string="Image Zip File", help="Zip file containing product images")

    def execute_method(self):
        try:
            if self.model_id:
                model = self.env[self.model_id.model]
            else:
                model = self
            if self.python_code:
                self.results = safe_eval(self.python_code.strip(), {'self': model}, mode="eval")
            else:
                self.results = "Please add some codes !"
        except Exception as error:
            self.results = str(error)

    def clear_method(self):
        self.python_code = ''
        self.results = ''

    def execute_my_script(self):
        print('--------Code Execute Started --------')
        ##########   CODE FOR FINDING COST PRICE GREATER THAN SALES PRICE
        # template = self.env['product.template'].search([('id', '=', 122)])
        # templates = self.env['product.template'].search([('detailed_type','=','product')])
        # for tmpl in templates:
        #     prod = self.env['product.product'].search([('name', '=', tmpl.name)], limit=1)
        #
        #     if prod.standard_price > prod.lst_price:
        #         print(prod.name,'cost--->>>',prod.standard_price,' sale price------->', prod.lst_price)

        #########################################

        try:
            file_data = self.worksheet
            binary_data = base64.b64decode(file_data)
            # Decode the binary data from base64
            binary_data = base64.b64decode(file_data)

            # Open the file using xlrd as a BytesIO object
            excel_file = io.BytesIO(binary_data)
            workbook = xlrd.open_workbook(file_contents=excel_file.read())

        except FileNotFoundError:
            raise UserError('No such file or not excel file.')

        except xlrd.biffh.XLRDError:
            raise UserError('Only excel files are supported.')

        for sheet in workbook.sheets():
            try:
                print('-----------inside excel page--------------')
                print(sheet.nrows, '-----------sheet n rows')
                print(sheet.name, '-----------sheet name')
                # if sheet.name == 'Worksheet':
                for row in range(sheet.nrows):
                    if row >= 1:
                        main_categ = sheet.cell_value(row, 0)
                        sub_categ = sheet.cell_value(row, 1)
                        print('main----->>', main_categ)
                        print('sub----->>', sub_categ)
                        main_categ_id = self.env['product.category'].search([('name', '=', main_categ)])
                        sub_categ_id = self.env['product.category'].search([('name', '=', sub_categ)])
                        print('main---33-->>', main_categ_id)
                        print('sub---33-->>', sub_categ_id)
                        if sub_categ_id and main_categ_id:
                            sub_categ_id.parent_id = main_categ_id
                            sub_categ_id.property_cost_method = 'fifo'
                            sub_categ_id.property_valuation = 'real_time'
                            sub_categ_id.property_account_income_categ_id = main_categ_id.property_account_income_categ_id
                            sub_categ_id.property_account_expense_categ_id = main_categ_id.property_account_expense_categ_id
                            sub_categ_id.property_stock_valuation_account_id = main_categ_id.property_stock_valuation_account_id
                        else:
                            raise UserError(_('No such category  --  %s --- %s') % (main_categ, sub_categ))





            except IndexError:
                pass

    def add_delivery_boys_to_zone(self):
        print('--------Code Execute Started --------')
        self.ensure_one()
        try:
            file_data = self.worksheet
            binary_data = base64.b64decode(file_data)
            # Decode the binary data from base64
            binary_data = base64.b64decode(file_data)

            # Open the file using xlrd as a BytesIO object
            excel_file = io.BytesIO(binary_data)
            workbook = xlrd.open_workbook(file_contents=excel_file.read())

        except FileNotFoundError:
            raise UserError('No such file or not excel file.')

        except xlrd.biffh.XLRDError:
            raise UserError('Only excel files are supported.')

        for sheet in workbook.sheets():
            try:
                print('-----------inside excel page--------------')
                # print(sheet.nrows, '-----------sheet n rows')
                # print(sheet.name, '-----------sheet name')
                if sheet.name == 'delivery':
                    for row in range(sheet.nrows):
                        if row >= 1:
                            location = sheet.cell_value(row, 1)
                            delivery_boy = sheet.cell_value(row, 2)
                            print('locaiton--->>', location)
                            print('delivery_boy--->>', delivery_boy)
                            boy_id = self.env['res.users'].search([('name', '=', delivery_boy)])
                            location_id = self.env['res.partner.location'].search([('name', 'ilike', location)])

                            print('location_id--->>', location_id)
                            print('boy_id--->>', boy_id)
                            # if not location_id:
                            #     raise UserError(
                            #         _('This location is not available in attributes--- %s') % (location))
                            # if delivery_boy != 'NO DELIVERY' and not boy_id:
                            #     raise UserError(
                            #         _('This boy_id is not available in attributes--- %s') % (delivery_boy))
                            for order in location_id:
                                # print(order.id, order.name)
                                if boy_id:
                                    order.delivery_boy_id = boy_id
                            # if boy_id:
                            #     print(boy_id.id, boy_id.name)


            except IndexError:
                pass

    def create_compo_products(self):
        print('--------Code Execute Started --------')
        self.ensure_one()
        try:
            file_data = self.worksheet
            binary_data = base64.b64decode(file_data)
            # Decode the binary data from base64
            binary_data = base64.b64decode(file_data)

            # Open the file using xlrd as a BytesIO object
            excel_file = io.BytesIO(binary_data)
            workbook = xlrd.open_workbook(file_contents=excel_file.read())

        except FileNotFoundError:
            raise UserError('No such file or not excel file.')

        except xlrd.biffh.XLRDError:
            raise UserError('Only excel files are supported.')

        for sheet in workbook.sheets():
            try:
                print('-----------inside excel page--------------')
                # print(sheet.nrows, '-----------sheet n rows')
                # print(sheet.name, '-----------sheet name')
                # if sheet.name == 'delivery':
                for row in range(sheet.nrows):
                    if row >= 1:
                        product_name = sheet.cell_value(row, 0)
                        compo_name = sheet.cell_value(row, 1)
                        quantity = sheet.cell_value(row, 2)
                        sale_price = sheet.cell_value(row, 3)
                        print('product_name--->>', product_name)
                        print('compo_name--->>', compo_name)
                        print('quantity--->>', quantity)
                        print('sale_price--->>', sale_price)
                        product_id = self.env['product.product'].search([('name', '=', product_name)], limit=1)
                        print(product_id, '---------product id')
                        if product_id:
                            print('111111')
                            product_template = self.env['product.template'].create({
                                'name': compo_name,
                                'sale_ok': False,
                                'purchase_ok': False,
                                'is_pack': True,
                                'can_be_expensed': False,
                                'detailed_type': 'consu',
                                'invoice_policy': 'delivery',
                                'categ_id': 100,
                                'list_price': sale_price,
                                'description_sale': product_id.product_tmpl_id.description_sale,
                                'pack_products_ids': [
                                    (0, 0, {
                                        'product_id': product_id.id,
                                        'quantity': quantity
                                    })
                                ]
                            })
                            print(product_template)

                        ########## Update categ id before pushing###########

                        else:
                            raise UserError(
                                _('This product is not available--- %s') % (product_name))



            except IndexError:
                pass

    def add_products(self):
        print("hello----------------------------")

        self.ensure_one()
        file_data = self.worksheet
        binary_data = base64.b64decode(file_data)

        excel_file = io.BytesIO(binary_data)
        workbook = xlrd.open_workbook(file_contents=excel_file.read())
        for sheet in workbook.sheets():
            n = 1
            for row in range(sheet.nrows):
                if row >= 1:
                    n += 1
                    print("-------", n)
                    name = sheet.cell_value(row, 2)
                    sale_description = sheet.cell_value(row, 1)
                    product_type = 'product'

                    color_values = sheet.cell_value(row, 9)
                    size_values = sheet.cell_value(row, 10)
                    selling_price = sheet.cell_value(row, 13)
                    purchase_cost = sheet.cell_value(row, 16)
                    product_category = sheet.cell_value(row, 6)
                    unique_code = sheet.cell_value(row, 18)
                    category_id = self.env['product.category'].search(
                        [('name', '=', product_category)])
                    if not category_id:
                        category_id = None
                        raise UserError(
                            _('This product_category is not available--- %s') % (product_category))
                    if isinstance(size_values, float):
                        size_values = int(size_values)
                    if isinstance(unique_code, float):
                        unique_code = int(unique_code)
                    color = None
                    if color_values and color_values != "DEFAULT":
                        color = self.env['product.attribute.value'].search(
                            [('name', '=', str(color_values)), ('attribute_id', '=', 4)])
                        if not color:
                            color = None
                            raise UserError(
                                _('This color is not available in attributes--- %s') % (color_values))
                    size = None
                    if size_values != "DEFAULT":
                        size = self.env['product.attribute.value'].search(
                            [('name', '=', size_values), ('attribute_id', '=', 3)])
                        if not size:
                            size = None
                            raise UserError(
                                _('This Size is not available in attributes--- %s') % (size_values))
                    #####  Creating Product template
                    product_template = self.env['product.template'].search([('name', '=', name)])
                    if not product_template:
                        context = {'default_code': unique_code, 'lst_price': selling_price,
                                   'standard_price': purchase_cost, }
                        product_template = self.env['product.template'].with_context(context).create({
                            'name': name,
                            'detailed_type': product_type,
                            'categ_id': category_id.id,
                            'list_price': selling_price,
                            'description_sale': sale_description,
                            'invoice_policy': "delivery",
                        })

                    ########   Adding color Values
                    context = {'default_code': unique_code, 'lst_price': selling_price,
                               'standard_price': purchase_cost, 'description_sale': sale_description}
                    if color:
                        color_line = self.env['product.template.attribute.line'].search([
                            ('product_tmpl_id', '=', product_template.id),
                            ('attribute_id', '=', 4),
                        ])
                        if color_line:
                            color_line.with_context(context).write({
                                'value_ids': [(4, color.id, 0)]
                            })

                        else:

                            color_line = self.env['product.template.attribute.line'].with_context(context).create({
                                'attribute_id': 4,
                                'product_tmpl_id': product_template.id,
                                'value_ids': [(6, 0, color.ids)]
                            })

                    ########   Adding size Values
                    if size:
                        size_line = self.env['product.template.attribute.line'].search([
                            ('product_tmpl_id', '=', product_template.id),
                            ('attribute_id', '=', 3),
                        ])

                        if size_line:

                            size_line.with_context(context).write({
                                'value_ids': [(4, size.id, 0)]
                            })
                        else:

                            size_line = self.env['product.template.attribute.line'].with_context(context).create({
                                'attribute_id': 3,
                                'product_tmpl_id': product_template.id,
                                'value_ids': [(6, 0, size.ids)]

                            })

    def set_cost(self):
        print("hello----------------------------")

        self.ensure_one()
        file_data = self.worksheet
        binary_data = base64.b64decode(file_data)

        excel_file = io.BytesIO(binary_data)
        workbook = xlrd.open_workbook(file_contents=excel_file.read())
        for sheet in workbook.sheets():
            n = 1
            for row in range(sheet.nrows):
                if row >= 1:
                    n += 1
                    name = sheet.cell_value(row, 0)
                    cost = sheet.cell_value(row, 2)
                    print(name)
                    print(cost)
                    products = self.env['product.product'].search([('name', '=', name), ('standard_price', '=', 0)])

                    # print(products)
                    if products:
                        for product in products:
                            product.standard_price = cost

    def set_stock_arora(self):
        print("hello----------------------------")

        self.ensure_one()
        file_data = self.worksheet
        binary_data = base64.b64decode(file_data)

        excel_file = io.BytesIO(binary_data)
        workbook = xlrd.open_workbook(file_contents=excel_file.read())
        # name=' AR66'
        # produ = self.env['product.product'].search([('id', '=',16210)])
        #
        # print(produ.product_template_attribute_value_ids,'---------test')

        for sheet in workbook.sheets():
            n = 1

            for row in range(sheet.nrows):
                if row >= 1 and sheet.cell_value(row, 0):
                    n += 1
                    print("-------", n)
                    name = sheet.cell_value(row, 0)
                    print(name, '-----name')
                    product = None
                    product_template = self.env['product.template'].search([
                        ('name', '=', name)])
                    print(product_template, '-----tmpl')
                    for order in product_template:
                        print(order.name, '-----tmpl')
                    if product_template:
                        color = sheet.cell_value(row, 5)
                        print(color, '------color')
                        color_vals = None
                        size_vals = None
                        if color:
                            color_vals = self.env['product.template.attribute.value'].search(
                                [('name', '=', color), ('attribute_id', '=', 1),
                                 ('product_tmpl_id', '=', product_template.id)])
                        else:
                            color = None
                        if row + 1 < sheet.nrows and not sheet.cell_value(row + 1, 1):
                            size = sheet.cell_value(row + 1, 5)
                            print(size, '-------size')
                        else:
                            size = None
                        print(color_vals, '---------color vals')
                        print(size, '---------size')
                        if size:
                            size_vals = self.env['product.template.attribute.value'].search(
                                [('name', '=', size), ('attribute_id', '=', 2),
                                 ('product_tmpl_id', '=', product_template.id)])
                        print(size_vals, '---------size vals')
                        if size_vals and color_vals:
                            print('1111111111')
                            print([color_vals.id, size_vals.id], '----------product_template_attribute_value_ids')
                            product = self.env['product.product'].search([
                                ('product_template_attribute_value_ids', 'in', [color_vals.id]),
                                ('product_template_attribute_value_ids', 'in', [size_vals.id]),
                                ('product_tmpl_id', '=', product_template.id)])
                            print("product -->>>", product)
                            for line in product:
                                print(line.display_name)
                            print("product -->>>", product.display_name)
                            if not product:
                                print('----no product')
                        elif not size_vals:
                            print('2222222222')
                            product = self.env['product.product'].search([
                                ('product_template_attribute_value_ids', 'in', color_vals.id),
                                ('product_tmpl_id', '=', product_template.id)])
                            print("product with only color---->>>>", product)
                            print("product with only color---->>>>", product.display_name)
                            if not product:
                                print('----no product')
                        elif not color_vals:
                            print('3333333333')
                            product = self.env['product.product'].search([
                                ('product_template_attribute_value_ids', 'in', size_vals.id),
                                ('product_tmpl_id', '=', product_template.id)])
                            print("product with only size---->>>>", product)
                            print("product with only size---->>>>", product.display_name)
                            if not product:
                                # _logger.warning("zzzzzz: %s", name)
                                print('----no product')
                        else:
                            # _logger.warning("aaaaaa: %s", name)
                            print("no product found-------", name)
                    else:
                        # _logger.warning("cccc : %s", name)
                        print("no template found for the product", name)
                    if product:
                        print('x')

                        self.env['stock.quant'].with_context(inventory_mode=True).create({
                            'product_id': product.id,
                            'inventory_quantity': sheet.cell_value(row, 3),
                            'location_id': 8,
                        })


    def get_product_with_no_image(self):
        # console.log("--------ui start------------------------------------");
        product_template=self.env['product.template'].search([('is_published', '=', 'True')])
        product_list=[]
        for product in product_template:
            if product.attribute_line_ids:
                for attribute in product.attribute_line_ids:
                    if attribute.attribute_id.name=='Colour':
                        for variant in product.product_variant_ids:
                            if not variant.image_1920:
                                product_list.append(product.name)
                                break
        print("products==>",product_list)
        print("Total Number Of Products:",len(product_list))



    # def add_product_images(self):
    #         print("-------add product images started-------")
    #         self.ensure_one()
    #         if not self.image_zip_file:
    #             raise UserError(_('Please choose a zip file'))
    #         if not self.worksheet:
    #             raise UserError(_('Please choose a excel file'))
    #
    #         # Decode and read the Excel file
    #         binary_data = base64.b64decode(self.worksheet)
    #         excel_io = io.BytesIO(binary_data)
    #         workbook = xlrd.open_workbook(file_contents=excel_io.read())
    #         sheet = workbook.sheet_by_index(0)  # Assuming first sheet contains data
    #
    #         # Read the ZIP file
    #         zip_io = io.BytesIO(base64.b64decode(self.image_zip_file))
    #         zip_archive = zipfile.ZipFile(zip_io, 'r')
    #
    #         color_attribute = self.env['product.attribute'].search([('name', '=', 'Color')], limit=1)
    #         size_attribute = self.env['product.attribute'].search([('name', '=', 'Size')], limit=1)
    #
    #         image_filenames_in_zip = [os.path.splitext(f)[0] for f in zip_archive.namelist()]
    #         print(image_filenames_in_zip, '-----image_filenames_in_zip')
    #         for row in range(1, sheet.nrows):  # Skip header
    #             item_code = str(sheet.cell_value(row, 0)).strip()
    #             print(item_code, '---------item_code')
    #             main_product = str(sheet.cell_value(row, 1)).strip()
    #             name = str(sheet.cell_value(row, 2)).strip()
    #             category_name = str(sheet.cell_value(row, 5)).strip()
    #             color_name = str(sheet.cell_value(row, 6)).strip()
    #             size_name = str(sheet.cell_value(row, 7)).strip()
    #             sale_price = sheet.cell_value(row, 14)
    #
    #             # Find or create category
    #             category = self.env['product.category'].search([('name', '=', category_name)], limit=1)
    #             if not category:
    #                 category = self.env['product.category'].create({'name': category_name})
    #
    #             # Find or create product template
    #             product_template = self.env['product.template'].search([('name', '=', main_product)], limit=1)
    #             if not product_template:
    #                 product_template = self.env['product.template'].create({
    #                     'name': main_product,
    #                     'default_code': item_code,
    #                     'categ_id': category.id,
    #                     'list_price': sale_price,
    #                     # 'detailed_type': 'product',
    #                 })
    #
    #             # Find attributes
    #             color = self.env['product.attribute.value'].search(
    #                 [('name', '=', color_name), ('attribute_id', '=', color_attribute.id)],
    #                 limit=1) if color_name and color_attribute else None
    #             size = self.env['product.attribute.value'].search(
    #                 [('name', '=', size_name), ('attribute_id', '=', size_attribute.id)],
    #                 limit=1) if size_name and size_attribute else None
    #
    #             # Add attributes to product
    #             if color and color_attribute:
    #                 self.env['product.template.attribute.line'].create({
    #                     'product_tmpl_id': product_template.id,
    #                     'attribute_id': color_attribute.id,
    #                     'value_ids': [(6, 0, [color.id])],
    #                 })
    #             if size and size_attribute:
    #                 self.env['product.template.attribute.line'].create({
    #                     'product_tmpl_id': product_template.id,
    #                     'attribute_id': size_attribute.id,
    #                     'value_ids': [(6, 0, [size.id])],
    #                 })
    #             # Assign image from ZIP
    #             image_filename = next((f for f in zip_archive.namelist() if f.endswith(f"{item_code}.jpeg") or f.endswith(f"{item_code}.jpg") or f.endswith(f"{item_code}.png")), None)
    #             print(image_filename)
    #             if image_filename:
    #                 with zip_archive.open(image_filename) as img_file:
    #                     img_data = base64.b64encode(img_file.read())
    #                     product_template.image_1920 = img_data
    #             else:
    #                 raise UserError(f"Image not found for Item Code: {item_code}")
    #
    #         print("-------add product images Ended-------")
    def add_product_images(self):
        print("-------add product images started-------")
        self.ensure_one()
        if not self.image_zip_file:
            raise UserError(_('Please choose a zip file'))
        if not self.worksheet:
            raise UserError(_('Please choose a excel file'))

        # Decode and read the Excel file
        binary_data = base64.b64decode(self.worksheet)
        excel_io = io.BytesIO(binary_data)
        workbook = xlrd.open_workbook(file_contents=excel_io.read())
        sheet = workbook.sheet_by_index(0)  # Assuming first sheet contains data

        # Read the ZIP file
        zip_io = io.BytesIO(base64.b64decode(self.image_zip_file))
        zip_archive = zipfile.ZipFile(zip_io, 'r')

        # Get or create attributes
        color_attribute = self.env['product.attribute'].search([('name', '=', 'Color')], limit=1)
        if not color_attribute:
            color_attribute = self.env['product.attribute'].create({'name': 'Color', 'sequence': 1})
        size_attribute = self.env['product.attribute'].search([('name', '=', 'Size')], limit=1)
        if not size_attribute:
            size_attribute = self.env['product.attribute'].create({'name': 'Size', 'sequence': 2})
        image_filenames_in_zip = [os.path.splitext(f)[0] for f in zip_archive.namelist()]
        print(image_filenames_in_zip, '-----image_filenames_in_zip')
        for row in range(1, sheet.nrows):  # Skip header
            item_code = str(sheet.cell_value(row, 0)).strip()
            print(item_code, '---------item_code')
            main_product = str(sheet.cell_value(row, 1)).strip()
            name = str(sheet.cell_value(row, 2)).strip()
            category_name = str(sheet.cell_value(row, 5)).strip()
            color_name = str(sheet.cell_value(row, 6)).strip()
            size_name = str(sheet.cell_value(row, 7)).strip()
            sale_price = sheet.cell_value(row, 14)

            # Find or create category
            category = self.env['product.category'].search([('name', '=', category_name)], limit=1)
            if not category:
                category = self.env['product.category'].create({'name': category_name})

            # Find or create product template
            product_template = self.env['product.template'].search([('name', '=', main_product)], limit=1)
            if not product_template:
                product_template = self.env['product.template'].create({
                    'name': main_product,
                    'categ_id': category.id,
                    'list_price': sale_price,
                    'attribute_line_ids': [],
                })
            # Get or create attributes values
            color = self.env['product.attribute.value'].search(
                [('name', '=', color_name), ('attribute_id', '=', color_attribute.id)],
                limit=1) if color_name and color_attribute else None
            if color_name and color_attribute and not color:
                color = self.env['product.attribute.value'].create({
                    'name': color_name,
                    'attribute_id': color_attribute.id
                })
            size = self.env['product.attribute.value'].search(
                [('name', '=', size_name), ('attribute_id', '=', size_attribute.id)],
                limit=1) if size_name and size_attribute else None
            if size_name and size_attribute and not size:
                size = self.env['product.attribute.value'].create({
                    'name': size_name,
                    'attribute_id': size_attribute.id
                })

            # Add attributes to product template
            attribute_line_values = []
            if color:
                attribute_line_values.append(color.id)
            if size:
                attribute_line_values.append(size.id)

            if color and color_attribute:
                if product_template.attribute_line_ids.filtered(lambda l: l.attribute_id == color_attribute):
                    product_template.attribute_line_ids.filtered(lambda l: l.attribute_id == color_attribute).write({
                        'value_ids': [(4, color.id, 0)]
                    })
                else:
                    product_template.write({
                        'attribute_line_ids': [(0, 0, {
                            'attribute_id': color_attribute.id,
                            'value_ids': [(6, 0, [color.id])]
                        })]
                    })

            if size and size_attribute:
                if product_template.attribute_line_ids.filtered(lambda l: l.attribute_id == size_attribute):
                    product_template.attribute_line_ids.filtered(lambda l: l.attribute_id == size_attribute).write({
                        'value_ids': [(4, size.id, 0)]
                    })
                else:
                    product_template.write({
                        'attribute_line_ids': [(0, 0, {
                            'attribute_id': size_attribute.id,
                            'value_ids': [(6, 0, [size.id])]
                        })]
                    })
            if attribute_line_values:
                # search if already exists

                product_variant = self.env['product.product'].search([
                    ('product_tmpl_id', '=', product_template.id),
                ])

                if product_variant:
                    product_variant = self.env['product.product'].search([
                        ('product_tmpl_id', '=', product_template.id),
                        ('product_template_attribute_value_ids', 'in', attribute_line_values)
                    ])

                if not product_variant:
                    # Create new variant
                    product_variant = self.env['product.product'].create({
                        'product_tmpl_id': product_template.id,
                        'default_code': item_code,  # set unique reference.
                    })

                    # Add attributes
                    product_variant.write({
                        'product_template_attribute_value_ids': [(6, 0, attribute_line_values)]
                    })
            else:
                product_variant = product_template.product_variant_id
                product_variant.default_code = item_code

            # Assign image from ZIP
            image_filename = next((f for f in zip_archive.namelist() if
                                   f.endswith(f"{item_code}.jpeg") or f.endswith(f"{item_code}.jpg") or f.endswith(
                                       f"{item_code}.png")), None)
            print(image_filename)
            if image_filename:
                with zip_archive.open(image_filename) as img_file:
                    img_data = base64.b64encode(img_file.read())
                    product_variant.image_1920 = img_data
            else:
                raise UserError(f"Image not found for Item Code: {item_code}")

        print("-------add product images Ended-------")


    # duplicate checking

    filename = fields.Char(string='Uploaded Filename')


    duplicate_file = fields.Binary(string='Duplicate Result File',
                                   readonly=True)
    duplicate_filename = fields.Char(string='Duplicate Filename',
                                     readonly=True)

    def check_duplicate_products(self):

        if not self.worksheet:
            raise UserError("Please upload an Excel file first.")

        try:

            excel_data = base64.b64decode(self.worksheet)
            wb = openpyxl.load_workbook(BytesIO(excel_data))
            sheet = wb.active

            ITEM_CODE_COL = 1
            BARCODE_COL = 14

            duplicate_products = []

            for row_idx in range(2, sheet.max_row + 1):
                item_code = str(sheet.cell(row=row_idx,
                                           column=ITEM_CODE_COL + 1).value or '').strip()
                print("item",item_code)
                barcode = str(sheet.cell(row=row_idx,
                                         column=BARCODE_COL + 1).value or '').strip()
                print("barcode",barcode)

                if not item_code or not barcode:
                    continue  # Skip empty rows


                existing_product = self.env['product.product'].search([
                    '|',
                    ('default_code', '=', item_code),
                    ('barcode', '=', barcode)
                ], limit=1)

                if existing_product:
                    print(f"duplicate: {existing_product.name} | Item Code: {existing_product.default_code} | Barcode: {existing_product.barcode}")
                    duplicate_products.append({
                        'Product Name': existing_product.name,
                        'Item Code': existing_product.default_code,
                        'Barcode': existing_product.barcode,
                    })



            if not duplicate_products:
                raise UserError(
                    "No duplicate products found based on 'ITEM CODE' and 'BARCODE 1'.")

            #Create output workbook in memory
            output = BytesIO()
            wb_result = openpyxl.Workbook()
            ws = wb_result.active
            ws.title = "Duplicates Found"
            ws.append(['Product Name', 'Item Code', 'Barcode'])

            for p in duplicate_products:
                ws.append([p['Product Name'], p['Item Code'], p['Barcode']])

            wb_result.save(output)
            output.seek(0)

            # save to new binary field
            file_data = base64.b64encode(output.read())
            self.write({
                'duplicate_file': file_data,
                'duplicate_filename': 'duplicate_products.xlsx'
            })

            # download action
            return {
                'type': 'ir.actions.act_url',
                'url': '/web/content/?model=ui.python&id=%s&field=duplicate_file&filename_field=duplicate_filename&download=true' % self.id,
                'target': 'new',
            }

        except Exception as e:
            raise UserError(f"Error reading Excel file: {e}")



    # def add_non_duplicate_product(self):
    #     print("add_non_duplicate_product started")
    #     self.ensure_one()
    #
    #     if not self.worksheet:
    #         raise UserError(_('Please upload an Excel file'))
    #
    #
    #     excel_data = base64.b64decode(self.worksheet)
    #     try:
    #         wb = openpyxl.load_workbook(BytesIO(excel_data))
    #         sheet = wb.active
    #     except Exception as e:
    #         raise UserError(f"Error opening Excel file: {e}")
    #
    #
    #     ITEM_CODE_COL = 1
    #     PRODUCT_NAME_COL = 2
    #     DESCRIPTION_COL = 3
    #     ARABIC_NAME_COL = 4
    #     SUB_CATEGORY_COL = 6
    #     BRAND_COL = 7
    #     ORIGIN_COL = 8
    #     UOM_COL = 10
    #     COST_COL = 12
    #     SALE_PRICE_COL = 13
    #     BARCODE_COL = 14
    #
    #     created_count = 0
    #     updated_count = 0
    #     skipped_count = 0
    #
    #     for row in range(4, sheet.max_row + 1):  # skip header
    #         item_code = str(sheet.cell(row=row,
    #                                    column=ITEM_CODE_COL + 1).value or '').strip()
    #         product_name = str(sheet.cell(row=row,
    #                                       column=PRODUCT_NAME_COL + 1).value or '').strip()
    #         description = str(sheet.cell(row=row,
    #                                      column=DESCRIPTION_COL + 1).value or '').strip()
    #         arabic_name = str(sheet.cell(row=row,
    #                                      column=ARABIC_NAME_COL + 1).value or '').strip()
    #         sub_category = str(sheet.cell(row=row,
    #                                       column=SUB_CATEGORY_COL + 1).value or '').strip()
    #         brand = str(
    #             sheet.cell(row=row, column=BRAND_COL + 1).value or '').strip()
    #         origin = str(
    #             sheet.cell(row=row, column=ORIGIN_COL + 1).value or '').strip()
    #         uom_name = str(
    #             sheet.cell(row=row, column=UOM_COL + 1).value or '').strip()
    #         cost = sheet.cell(row=row, column=COST_COL + 1).value or 0.0
    #         sale_price = sheet.cell(row=row,
    #                                 column=SALE_PRICE_COL + 1).value or 0.0
    #         barcode = str(sheet.cell(row=row,
    #                                  column=BARCODE_COL + 1).value or '').strip()
    #
    #         print(
    #             f"Row {row}: "
    #             f"item_code={item_code}, "
    #             f"product_name={product_name}, "
    #             f"description={description}, "
    #             f"arabic_name={arabic_name}, "
    #             f"sub_category={sub_category}, "
    #             f"brand={brand}, "
    #             f"origin={origin}, "
    #             f"uom_name={uom_name}, "
    #             f"cost={cost}, "
    #             f"sale_price={sale_price}, "
    #             f"barcode={barcode}"
    #         )
    #
    #
    #
    #         if not item_code and not barcode and not product_name:
    #             skipped_count += 1
    #             continue
    #
    #         try:
    #             cost = float(cost) if cost not in (None, '') else 0.0
    #             sale_price = float(sale_price) if sale_price not in (None,
    #                                                                  '') else 0.0
    #         except:
    #             cost = sale_price = 0.0
    #
    #         #Search item_code or barcode
    #         existing = self.env['product.product'].search([
    #             '|',
    #             ('default_code', '=', item_code),
    #             ('barcode', '=', barcode)
    #         ], limit=1)
    #
    #         if existing:
    #             tmpl = existing.product_tmpl_id
    #             if sale_price and tmpl.list_price != sale_price:
    #                 tmpl.list_price = sale_price
    #             updated_count += 1
    #         else:
    #             #subcategory if exists
    #             category_id = False
    #             if sub_category:
    #                 category = self.env['product.category'].search(
    #                     [('name', '=', sub_category)], limit=1)
    #                 print("category\n\n\n\n",category)
    #                 if category:
    #                     category_id=category.id
    #
    #             #UoM if exists
    #             uom_id = False
    #             if uom_name:
    #                 uom = self.env['uom.uom'].search([('name', '=', uom_name)],
    #                                                  limit=1)
    #                 print("\n \n\n\nuom",uom)
    #                 if uom:
    #                     uom_id = uom.id
    #
    #             # origin_id = False
    #             # if origin:
    #             #     country = self.env['res.country'].search([
    #             #         '|',
    #             #         ('name', '=', origin),
    #             #     ], limit=1)
    #             #     print("\n\n\n country",country)
    #             #     if country:
    #             #         origin_id = country.id
    #
    #             #Create new template
    #             tmpl_vals = {
    #                 'name': product_name or 'Unnamed',
    #                 'default_code': item_code or '',
    #                 'list_price': sale_price,
    #                 'standard_price': cost,
    #                 'description': description or '',
    #                 'arabic_name': arabic_name or '',
    #                 'brand': brand or '',
    #                 # 'country_of_origin': origin_id,
    #                 # 'categ_id': category_id,
    #                 'categ_id':447,
    #                 # 'uom_id': uom_id,
    #                 'uom_id': 28,
    #                 # 'uom_po_id': uom_id,
    #                 'uom_po_id': 28,
    #             }
    #
    #             tmpl = self.env['product.template'].create(tmpl_vals)
    #
    #             #existing variant or create one
    #             variant = tmpl.product_variant_id or self.env[
    #                 'product.product'].create({
    #                 'product_tmpl_id': tmpl.id
    #             })
    #
    #             #Update codes/barcodes
    #             if item_code:
    #                 variant.default_code = item_code
    #             if barcode:
    #                 variant.barcode = barcode
    #
    #             created_count += 1
    #
    #     self.results = (
    #         f"Import Complete \n"
    #         f"Created: {created_count}\n"
    #         f"Updated: {updated_count}\n"
    #         f"Skipped Empty Rows: {skipped_count}"
    #     )
    #     print("Ended")
    #     return True

    def import_products_with_barcode_move(self):
        if not self.worksheet:
            raise UserError(_('Please upload an Excel file.'))

        excel_data = base64.b64decode(self.worksheet)
        try:
            wb = openpyxl.load_workbook(BytesIO(excel_data))
            sheet = wb.active
        except Exception as e:
            raise UserError(f"Error opening Excel file: {e}")

        # Define column indices
        ITEM_CODE_COL = 1
        PRODUCT_NAME_COL = 2
        DESCRIPTION_COL = 3
        ARABIC_NAME_COL = 4
        SUB_CATEGORY_COL = 6
        BRAND_COL = 7
        ORIGIN_COL = 8
        UOM_COL = 10
        COST_COL = 12
        SALE_PRICE_COL = 13
        BARCODE_COL = 14
        COMPANY_COL = 15

        created_count = 0
        barcode_created_count = 0
        skipped_count = 0

        # Company fixed by code
        kk_company = self.env['res.company'].sudo().search([('code', '=', 'KL')], limit=1)
        if not kk_company:
            raise UserError(_("Company with code 'KK' not found."))

        for row in range(4, sheet.max_row + 1):
            item_code = str(sheet.cell(row=row, column=ITEM_CODE_COL + 1).value or '').strip()
            product_name = str(sheet.cell(row=row, column=PRODUCT_NAME_COL + 1).value or '').strip()
            description = str(sheet.cell(row=row, column=DESCRIPTION_COL + 1).value or '').strip()
            arabic_name = str(sheet.cell(row=row, column=ARABIC_NAME_COL + 1).value or '').strip()
            sub_category = str(sheet.cell(row=row, column=SUB_CATEGORY_COL + 1).value or '').strip()
            brand = str(sheet.cell(row=row, column=BRAND_COL + 1).value or '').strip()
            origin = str(sheet.cell(row=row, column=ORIGIN_COL + 1).value or '').strip()
            uom_name = str(sheet.cell(row=row, column=UOM_COL + 1).value or '').strip()
            cost = float(sheet.cell(row=row, column=COST_COL + 1).value or 0.0)
            sale_price = float(sheet.cell(row=row, column=SALE_PRICE_COL + 1).value or 0.0)
            barcode = str(sheet.cell(row=row, column=BARCODE_COL + 1).value or '').strip()
            print(product_name)

            if not barcode and not item_code and not product_name:
                skipped_count += 1
                continue

            # Category
            category = self.env['product.category'].sudo().search([('name', '=', sub_category)], limit=1)
            category_id = category.id if category else 447

            # UoM
            uom = self.env['uom.uom'].sudo().search([('name', '=', uom_name)], limit=1)
            uom_id = uom.id if uom else 28  # fallback UoM

            # Search for existing product
            existing_product = self.env['product.product'].sudo().search([
                '|', ('default_code', '=', item_code),
                ('barcode', '=', barcode)
            ], limit=1)

            # ---------------------
            # CASE 1: Product exists
            # ---------------------
            if existing_product:
                existing_barcode = self.env['product.barcode'].sudo().search([
                    ('barcode', '=', barcode),
                    ('product_id', '=', existing_product.id),
                    ('company_id', '=', kk_company.id)
                ], limit=1)
                if not existing_barcode:
                    self.env['product.barcode'].sudo().create({
                        'product_id': existing_product.id,
                        'barcode': barcode,
                        'uom_id': uom_id,
                        'price': sale_price,
                        'company_id': kk_company.id,
                        'arabic_price_alt': getattr(existing_product, 'arabic_price_alt', '') or '',
                    })
                    barcode_created_count += 1
                else:
                    skipped_count += 1
                continue

            # ---------------------
            # CASE 2: Product does not exist → Create new
            # ---------------------
            tmpl_vals = {
                'name': product_name or 'Unnamed',
                'default_code': item_code or '',
                'list_price': sale_price,
                'standard_price': cost,
                'description': description or '',
                'arabic_name': arabic_name or '',
                'brand': brand or '',
                'categ_id': category_id,
                'uom_id': uom_id,
                'uom_po_id': uom_id,
                'company_id': kk_company.id,
            }

            tmpl = self.env['product.template'].sudo().create(tmpl_vals)
            product_variant = tmpl.product_variant_id

            # Create product.barcode entry
            if barcode:
                self.env['product.barcode'].sudo().create({
                    'product_id': product_variant.id,
                    'barcode': barcode,
                    'uom_id': uom_id,
                    'price': sale_price,
                    'company_id': kk_company.id,
                    'arabic_price_alt': getattr(product_variant, 'arabic_price_alt', '') or '',
                })

            created_count += 1

        # Save result summary
        self.results = (
            f"New Products Created: {created_count}\n"
            f"New Barcode Records: {barcode_created_count}\n"
            f"Skipped (duplicates/missing): {skipped_count}"
        )

        print(self.results)
        return True

    def update_existing_product_cost_and_price(self):
        if not self.worksheet:
            raise UserError(_('Please upload an Excel file.'))

        excel_data = base64.b64decode(self.worksheet)
        try:
            wb = openpyxl.load_workbook(BytesIO(excel_data))
            sheet = wb.active
        except Exception as e:
            raise UserError(f"Error opening Excel file: {e}")

        # Define column indices (same as before)
        ITEM_CODE_COL = 1
        BARCODE_COL = 14
        COST_COL = 12
        SALE_PRICE_COL = 13

        updated_count = 0
        skipped_count = 0

        for row in range(4, sheet.max_row + 1):
            item_code = str(sheet.cell(row=row, column=ITEM_CODE_COL + 1).value or '').strip()
            barcode = str(sheet.cell(row=row, column=BARCODE_COL + 1).value or '').strip()
            cost = sheet.cell(row=row, column=COST_COL + 1).value
            sale_price = sheet.cell(row=row, column=SALE_PRICE_COL + 1).value

            if not (item_code or barcode):
                skipped_count += 1
                continue

            # Convert numeric fields safely
            try:
                cost_value = float(cost or 0.0)
            except Exception:
                cost_value = 0.0

            try:
                sale_price_value = float(sale_price or 0.0)
            except Exception:
                sale_price_value = 0.0

            # Find existing product
            product = self.env['product.product'].sudo().search([
                '|', ('default_code', '=', item_code),
                ('barcode', '=', barcode)
            ], limit=1)

            if product:
                tmpl = product.product_tmpl_id
                # Update only if values are different
                vals = {}
                if tmpl.standard_price != cost_value:
                    vals['standard_price'] = cost_value
                if tmpl.list_price != sale_price_value:
                    vals['list_price'] = sale_price_value

                if vals:
                    tmpl.sudo().write(vals)
                    updated_count += 1
            else:
                skipped_count += 1

        self.results = (
            f"Updated Product Costs/Prices: {updated_count}\n"
            f"Skipped (not found or invalid): {skipped_count}"
        )
        print(self.results)
        return True

    def assign_pos_categories_based_on_company(self):
        PosCategory = self.env['pos.category'].sudo()
        ProductTmpl = self.env['product.template'].sudo()
        Barcode = self.env['product.barcode'].sudo()
        Company = self.env['res.company'].sudo()

        # Ensure the three POS categories exist (create if missing)
        kitchenkraft_categ = PosCategory.search([('name', '=', 'Kitchenkraft')], limit=1)
        if not kitchenkraft_categ:
            kitchenkraft_categ = PosCategory.create({'name': 'Kitchenkraft'})

        klassic_categ = PosCategory.search([('name', '=', 'Klassic Kitchen')], limit=1)
        if not klassic_categ:
            klassic_categ = PosCategory.create({'name': 'Klassic Kitchen'})

        common_categ = PosCategory.search([('name', '=', 'Common')], limit=1)
        if not common_categ:
            common_categ = PosCategory.create({'name': 'Common'})

        # Get company records
        kk_company = Company.search([('code', '=', 'KK')], limit=1)
        kl_company = Company.search([('code', '=', 'KL')], limit=1)

        if not kk_company or not kl_company:
            raise UserError(_("Both companies with code 'KK' and 'KL' must exist."))

        updated_count = 0
        no_barcode_count = 0

        # Loop through all products
        all_products = ProductTmpl.search([])

        for tmpl in all_products:
            # Find all barcodes for this product template
            barcodes = Barcode.search([('product_id.product_tmpl_id', '=', tmpl.id)])
            if not barcodes:
                no_barcode_count += 1
                continue

            # Extract company codes from linked barcodes
            company_codes = set(barcodes.mapped('company_id.code'))

            if {'KK', 'KL'}.issubset(company_codes):
                # Has both KK & KL → Common
                tmpl.pos_categ_ids = [(6, 0, [common_categ.id])]
            elif 'KK' in company_codes:
                # Only KK
                tmpl.pos_categ_ids = [(6, 0, [kitchenkraft_categ.id])]
            elif 'KL' in company_codes:
                # Only KL
                tmpl.pos_categ_ids = [(6, 0, [klassic_categ.id])]
            else:
                continue

            updated_count += 1

        self.results = (
            f"POS Category Assignment Completed\n"
            f"Products Updated: {updated_count}\n"
            f"Products Without Barcodes: {no_barcode_count}"
        )
        print(self.results)
        return True

    def update_existing_product_price(self):
        # Open Odoo shell
        products = self.env['product.product'].search([])
        products._compute_price_for_company()

    def assign_pos_category_by_company(self):

        Product = self.env['product.product']
        POSCategory = self.env['pos.category']

        created_cat = 0
        updated_prod = 0
        skipped = 0

        all_products = Product.search([])

        for product in all_products:
            #all barcodes related to product
            barcode_recs = self.env['product.barcode'].search([
                ('product_id', '=', product.id)
            ])
            print("Processing Product:", product.name, "(ID:", product.id, ")")

            if barcode_recs:
                print("  Found", len(barcode_recs), "barcode(s):")
                for b in barcode_recs:
                    print("   Barcode:", b.barcode or "N/A",
                          "| Company:", b.company_id.name or "No Company",
                          "| Barcode ID:", b.id)
            else:
                print("  No barcode records found. Skipped.")
                skipped += 1
                continue


            company_ids = barcode_recs.mapped('company_id')

            #Remove empty companies
            company_ids = company_ids.filtered(lambda c: c)

            if not company_ids:
                skipped += 1
                continue

            if len(company_ids) == 1:
                pos_category_name = company_ids.name
            else:
                pos_category_name = 'Common'

            pos_category = POSCategory.search(
                [('name', '=', pos_category_name)],
                limit=1
            )
            if not pos_category:
                pos_category = POSCategory.create({'name': pos_category_name})
                created_cat += 1

            #Assign POS category to product template
            template = product.product_tmpl_id
            if pos_category not in template.pos_categ_ids:
                template.pos_categ_ids = [(4, pos_category.id)]
                updated_prod += 1
            else:
                skipped += 1

        result_msg = (
            f"Created Categories: {created_cat}\n"
            f"Updated Products: {updated_prod}\n"
            f"Skipped (No barcode or company): {skipped}"
        )

        self.results = result_msg
        print(result_msg)
        return True


    def action_move_to_barcode(self):
        skipped_products = []
        created_products = []

        all_products = self.env['product.product'].search([])

        for product in all_products:
            if not product.barcode or not product.uom_id:
                skipped_products.append(f"{product.display_name} (No Barcode or UoM)")
                continue

            current_company = self.env.company
            print("Processing Product:", product.display_name)
            print("Current Company:", current_company.name)

            existing = self.env['product.barcode'].search([
                ('barcode', '=', product.barcode),
                ('product_id', '=', product.id),
                ('company_id', '=', current_company.id)
            ], limit=1)

            if existing:
                print("Skipped (Already Exists):", product.display_name)
                skipped_products.append(f"{product.display_name} (Already Exists)")
                continue

            # Create barcode
            self.env['product.barcode'].create({
                'product_id': product.id,
                'barcode': product.barcode,
                'uom_id': product.uom_id.id,
                'price': product.lst_price or 0.0,
                'company_id': current_company.id,
                'arabic_price_alt': product.arabic_price_alt or '',
            })
            print("Created new barcode for:", product.display_name)
            created_products.append(product.display_name)


            product.write({
                'barcode': False,
                'lst_price': 0.0,
            })

        print("\nBarcode Move Completed Successfully.")
        print("Created Barcodes for:", created_products)
        print("Skipped Products:", skipped_products)


        summary = (
            f"Created: {len(created_products)} product(s)\n"
            f"Skipped: {len(skipped_products)} product(s)\n\n"
            f"Skipped Products:\n" + "\n".join(skipped_products)
        )

        self.results = summary
        return True



    def import_products_barcode_flo(self):

        if not self.worksheet:
            raise UserError(_('Please upload an Excel file'))

        excel_data = base64.b64decode(self.worksheet)

        try:
            wb = openpyxl.load_workbook(BytesIO(excel_data))
            sheet = wb.active
        except Exception as e:
            raise UserError(f"Error opening Excel: {e}")

        # Excel Columns
        INTERNAL_REF_COL = 1
        NAME_COL = 2
        DESC_COL = 3
        BARCODE_COL = 4
        UOM_COL = 5
        CATEGORY_COL = 6
        BRAND_COL = 7
        COST_COL = 8
        SALE_PRICE_COL = 9
        PURCHASE_COL = 10
        SALES_COL = 11
        POS_COL = 12
        TRACK_COL = 13

        product_created_results = []
        barcode_created_results = []
        skipped_results = []
        updated_cost_results = []
        category_not_found_results = []

        created_products = 0
        barcode_created = 0
        skipped = 0
        cost_updated = 0
        category_not_found = 0

        created_categories = set()

        # Company KL
        company_kl = self.env['res.company'].sudo().search(
            [('code', '=', 'KL')], limit=1)

        if not company_kl:
            raise UserError("Company KK not found")

        for row in range(3, sheet.max_row + 1):

            internal_ref = str(sheet.cell(row=row, column=INTERNAL_REF_COL).value or '').strip()
            name = str(sheet.cell(row=row, column=NAME_COL).value or '').strip()
            desc = str(sheet.cell(row=row, column=DESC_COL).value or '').strip()
            barcode = str(sheet.cell(row=row, column=BARCODE_COL).value or '').strip()
            uom_name = str(sheet.cell(row=row, column=UOM_COL).value or '').strip()
            categ_name = str(sheet.cell(row=row, column=CATEGORY_COL).value or '').strip()
            brand = str(sheet.cell(row=row, column=BRAND_COL).value or '').strip()

            cost = sheet.cell(row=row, column=COST_COL).value or 0
            sale_price = sheet.cell(row=row, column=SALE_PRICE_COL).value or 0

            purchase_ok = sheet.cell(row=row, column=PURCHASE_COL).value
            sale_ok = sheet.cell(row=row, column=SALES_COL).value
            pos_ok = sheet.cell(row=row, column=POS_COL).value
            track_inventory = sheet.cell(row=row, column=TRACK_COL).value
            print("track_inventory",track_inventory,name,row)

            if not internal_ref:
                skipped += 1
                print("skipped",row,internal_ref,barcode,name)
                continue

            try:
                cost = float(cost)
            except:
                cost = 0.0

            try:
                sale_price = float(sale_price)
            except:
                sale_price = 0.0

            # Find UOM
            uom = self.env['uom.uom'].sudo().search(
                [('name', '=', uom_name)], limit=1)



            categ_name = (categ_name or '').strip()

            category = False

            if categ_name:
                category = self.env['product.category'].sudo().search(
                    [('name', '=ilike', categ_name)], limit=1)

                # Category not found in DB - skip this product
                if not category:
                    category_not_found += 1
                    category_not_found_results.append(
                        f"{name} | {internal_ref} | {barcode} | {categ_name}"
                    )
                    print("category not found, skipping", categ_name, row)
                    continue


            # Search existing product
            product = self.env['product.product'].sudo().search([
                ('default_code', '=', internal_ref)
            ], limit=1)
            print("product exists",product.name,product.barcode)

            # ----------------------------
            # PRODUCT EXISTS
            # ----------------------------
            if product:
                # tmpl = product.product_tmpl_id
                # old_cost = tmpl.with_company(company_kl).standard_price
                #
                # # Check if cost needs to be updated
                # if old_cost != cost:
                #     tmpl.with_company(company_kl).sudo().write({
                #         'standard_price': cost
                #     })
                #     cost_updated += 1
                #     updated_cost_results.append(
                #         f"{product.name} | {internal_ref} | {old_cost} | {cost}"
                #     )

                # barcode_record = self.env['product.barcode'].sudo().search([
                #     ('barcode', '=', barcode),
                #     ('product_id', '=', product.id),
                #     ('company_id', '=', company_kl.id)
                # ], limit=1)
                #
                # # BARCODE EXISTS
                # if barcode_record:
                #
                #     skipped_results.append(
                #         f"{product.name} | {internal_ref} | {barcode}"
                #     )
                #
                #     skipped += 1
                #     continue
                #
                # # CREATE BARCODE
                # self.env['product.barcode'].sudo().create({
                #     'product_id': product.id,
                #     'barcode': barcode,
                #     'uom_id': product.uom_id.id,
                #     'price': product.list_price,
                #     'company_id': company_kl.id,
                #     'arabic_price_alt': getattr(product, 'arabic_price_alt', '') or '',
                # })
                #
                # barcode_created += 1
                #
                # barcode_created_results.append(
                #     f"{product.name} | {internal_ref} | {barcode}"
                # )

                skipped_results.append(
                     f"{product.name} | {internal_ref} | {barcode}"
                  )

                continue

            # ----------------------------
            # PRODUCT NOT EXISTS
            # ----------------------------

            tmpl_vals = {
                'name': name,
                'default_code': internal_ref,
                'description': desc,
                'brand': brand,
                'categ_id': category.id if category else self.env.ref('product.product_category_all').id,
                'uom_id': uom.id if uom else False,
                'purchase_ok': bool(purchase_ok),
                'sale_ok': bool(sale_ok),
                'available_in_pos': bool(pos_ok),
                'is_storable': bool(track_inventory),
                'list_price': sale_price,
            }

            tmpl = self.env['product.template'].sudo().create(tmpl_vals)

            # Cost only for KL company
            tmpl.with_company(company_kl).sudo().write({
                'standard_price': cost
            })

            product_variant = tmpl.product_variant_id
            # Create Barcode
            self.env['product.barcode'].sudo().create({
                'product_id': product_variant.id,
                'barcode': barcode,
                'uom_id': product_variant.uom_id.id,
                'price': sale_price,
                'company_id': company_kl.id,
                'arabic_price_alt': getattr(product_variant, 'arabic_price_alt', '') or '',
            })

            created_products += 1

            product_created_results.append(
                f"{name} | {internal_ref} | {barcode}"
            )

        # Build section header format
        section_header = "Product Name | Internal Reference | Barcode"
        separator = "-" * 60

        output_parts = [
            f"Products Created: {created_products}",
            f"Barcode Created: {barcode_created}",
            f"Skipped: {skipped}",
            f"Cost Updated: {cost_updated}",
            f"New Categories Created: {len(created_categories)}",
            f"Category Not Found (Skipped): {category_not_found}",
        ]

        if created_categories:
            output_parts.append(f"\nCreated Categories:\n" + "\n".join(created_categories))

        # Section 1: New Products & Barcode Created
        output_parts.append(f"\n{separator}")
        output_parts.append(f"NEW PRODUCTS CREATED ({len(product_created_results)})")
        output_parts.append(separator)
        output_parts.append(section_header)
        output_parts.append(separator)
        if product_created_results:
            output_parts.extend(product_created_results)
        else:
            output_parts.append("(none)")

        # Section 2: Product Existed, Barcode Created
        output_parts.append(f"\n{separator}")
        output_parts.append(f"PRODUCT EXISTED - BARCODE CREATED ({len(barcode_created_results)})")
        output_parts.append(separator)
        output_parts.append(section_header)
        output_parts.append(separator)
        if barcode_created_results:
            output_parts.extend(barcode_created_results)
        else:
            output_parts.append("(none)")

        # Section 3: Skipped (Product & Barcode Already Exist)
        output_parts.append(f"\n{separator}")
        output_parts.append(f"SKIPPED - PRODUCT & BARCODE ALREADY EXIST ({len(skipped_results)})")
        output_parts.append(separator)
        output_parts.append(section_header)
        output_parts.append(separator)
        if skipped_results:
            output_parts.extend(skipped_results)
        else:
            output_parts.append("(none)")

        # Section 4: Cost Updated
        output_parts.append(f"\n{separator}")
        output_parts.append(f"COST UPDATED ({len(updated_cost_results)})")
        output_parts.append(separator)
        output_parts.append("Product Name | Internal Reference | Old Cost | New Cost")
        output_parts.append(separator)
        if updated_cost_results:
            output_parts.extend(updated_cost_results)
        else:
            output_parts.append("(none)")

        # Section 5: Category Not Found (Skipped)
        output_parts.append(f"\n{separator}")
        output_parts.append(f"CATEGORY NOT FOUND - SKIPPED ({len(category_not_found_results)})")
        output_parts.append(separator)
        output_parts.append("Product Name | Internal Reference | Barcode | Category Name")
        output_parts.append(separator)
        if category_not_found_results:
            output_parts.extend(category_not_found_results)
        else:
            output_parts.append("(none)")

        self.results = "\n".join(output_parts)
        return True


    def import_products_barcode_flow(self):

        if not self.worksheet:
            raise UserError(_('Please upload an Excel file'))

        excel_data = base64.b64decode(self.worksheet)

        try:
            wb = openpyxl.load_workbook(BytesIO(excel_data))
            sheet = wb.active
        except Exception as e:
            raise UserError(f"Error opening Excel: {e}")

        # Excel Columns
        INTERNAL_REF_COL = 1
        NAME_COL = 2
        DESC_COL = 3
        BARCODE_COL = 4
        UOM_COL = 5
        CATEGORY_COL = 6
        BRAND_COL = 7
        COST_COL = 8
        SALE_PRICE_COL = 9
        PURCHASE_COL = 10
        SALES_COL = 11
        POS_COL = 12
        TRACK_COL = 13

        product_created_results = []
        barcode_created_results = []
        skipped_results = []
        updated_cost_results = []
        barcode_conflict_results = []  # NEW: Track barcode conflicts

        created_products = 0
        barcode_created = 0
        skipped = 0
        cost_updated = 0
        barcode_conflicts = 0  # NEW: Counter for barcode conflicts

        created_categories = set()

        # Company KL
        company_kl = self.env['res.company'].sudo().search(
            [('code', '=', 'KK')], limit=1)

        if not company_kl:
            raise UserError("Company KK not found")

        # Find or create the KRsample category for all new products
        krsample_category = self.env['product.category'].sudo().search(
            [('name', '=', 'KRsample')], limit=1)
        if not krsample_category:
            krsample_category = self.env['product.category'].sudo().create({
                'name': 'KRsample',
            })

        for row in range(3, sheet.max_row + 1):

            internal_ref = str(sheet.cell(row=row, column=INTERNAL_REF_COL).value or '').strip()
            name = str(sheet.cell(row=row, column=NAME_COL).value or '').strip()
            desc = str(sheet.cell(row=row, column=DESC_COL).value or '').strip()
            barcode = str(sheet.cell(row=row, column=BARCODE_COL).value or '').strip()
            uom_name = str(sheet.cell(row=row, column=UOM_COL).value or '').strip()
            categ_name = str(sheet.cell(row=row, column=CATEGORY_COL).value or '').strip()
            brand = str(sheet.cell(row=row, column=BRAND_COL).value or '').strip()

            cost = sheet.cell(row=row, column=COST_COL).value or 0
            sale_price = sheet.cell(row=row, column=SALE_PRICE_COL).value or 0

            purchase_ok = sheet.cell(row=row, column=PURCHASE_COL).value
            sale_ok = sheet.cell(row=row, column=SALES_COL).value
            pos_ok = sheet.cell(row=row, column=POS_COL).value
            track_inventory = sheet.cell(row=row, column=TRACK_COL).value
            print("track_inventory", track_inventory, name, row)

            if not internal_ref:
                skipped += 1
                print("skipped", row, internal_ref, barcode, name)
                continue

            try:
                cost = float(cost)
            except:
                cost = 0.0

            try:
                sale_price = float(sale_price)
            except:
                sale_price = 0.0

            # Find UOM
            uom = self.env['uom.uom'].sudo().search(
                [('name', '=', uom_name)], limit=1)
            print("uom", uom.name, uom.id, row)
            if not uom:
                print("uom not found", uom_name, row)
                break

            # Search existing product
            product = self.env['product.product'].sudo().search([
                '|',
                ('default_code', '=', internal_ref),
                ('barcode', '=', barcode)
            ], limit=1)
            print("product exists", product.name, product.barcode)

            # ----------------------------
            # PRODUCT EXISTS
            # ----------------------------
            if product:
                tmpl = product.product_tmpl_id
                old_cost = tmpl.with_company(company_kl).standard_price

                # Check if cost needs to be updated
                if old_cost != cost:
                    tmpl.with_company(company_kl).sudo().write({
                        'standard_price': cost
                    })
                    cost_updated += 1
                    updated_cost_results.append(
                        f"{product.name} | {internal_ref} | {old_cost} | {cost}"
                    )

                barcode_record = self.env['product.barcode'].sudo().search([
                    ('barcode', '=', barcode),
                    ('product_id', '=', product.id),
                    ('company_id', '=', company_kl.id)
                ], limit=1)

                # BARCODE EXISTS
                if barcode_record:
                    skipped_results.append(
                        f"{product.name} | {internal_ref} | {barcode}"
                    )
                    skipped += 1
                    continue

                # NEW: Check if barcode already exists for ANOTHER product
                existing_barcode = self.env['product.barcode'].sudo().search([
                    ('barcode', '=', barcode),
                    ('company_id', '=', company_kl.id),
                ], limit=1)

                if existing_barcode:
                    # Barcode is already assigned to a different product or company
                    existing_product = existing_barcode.product_id
                    existing_company = existing_barcode.company_id
                    barcode_conflicts += 1
                    barcode_conflict_results.append(
                        f"{name} | {internal_ref} | {barcode} | "
                        f"{existing_product.name} | {existing_product.default_code or ''} | "
                        f"{existing_company.name or 'No Company'}"
                    )
                    continue

                # CREATE BARCODE
                self.env['product.barcode'].sudo().create({
                    'product_id': product.id,
                    'barcode': barcode,
                    'uom_id': product.uom_id.id,
                    'price': product.list_price,
                    'company_id': company_kl.id,
                    'arabic_price_alt': getattr(product, 'arabic_price_alt', '') or '',
                })

                barcode_created += 1

                barcode_created_results.append(
                    f"{product.name} | {internal_ref} | {barcode}"
                )

                continue

            # ----------------------------
            # PRODUCT NOT EXISTS
            # ----------------------------

            # NEW: Check if barcode already exists for another product before creating
            if barcode:
                existing_barcode = self.env['product.barcode'].sudo().search([
                    ('barcode', '=', barcode),
                    ('company_id', '=', company_kl.id),
                ], limit=1)

                if existing_barcode:
                    existing_product = existing_barcode.product_id
                    existing_company = existing_barcode.company_id
                    barcode_conflicts += 1
                    barcode_conflict_results.append(
                        f"{name} | {internal_ref} | {barcode} | "
                        f"{existing_product.name} | {existing_product.default_code or ''} | "
                        f"{existing_company.name or 'No Company'}"
                    )
                    # Still create the product, just skip barcode creation
                    # tmpl_vals = {
                    #     'name': name,
                    #     'default_code': internal_ref,
                    #     'uom_id': uom.id if uom else False,
                    #     'purchase_ok': bool(purchase_ok),
                    #     'sale_ok': bool(sale_ok),
                    #     'available_in_pos': bool(pos_ok),
                    #     'is_storable': bool(track_inventory),
                    #     'list_price': sale_price,
                    # }
                    # tmpl = self.env['product.template'].sudo().create(tmpl_vals)
                    # tmpl.with_company(company_kl).sudo().write({
                    #     'standard_price': cost
                    # })
                    # created_products += 1
                    # product_created_results.append(
                    #     f"{name} | {internal_ref} | {barcode} (barcode skipped - conflict)"
                    # )
                    continue

            tmpl_vals = {
                'name': name,
                'default_code': internal_ref,
                'categ_id': krsample_category.id,
                'uom_id': uom.id if uom else False,
                'purchase_ok': bool(purchase_ok),
                'sale_ok': bool(sale_ok),
                'available_in_pos': bool(pos_ok),
                'is_storable': bool(track_inventory),
                'list_price': sale_price,
            }

            tmpl = self.env['product.template'].sudo().create(tmpl_vals)

            # Cost only for KL company
            tmpl.with_company(company_kl).sudo().write({
                'standard_price': cost
            })

            product_variant = tmpl.product_variant_id
            # Create Barcode
            self.env['product.barcode'].sudo().create({
                'product_id': product_variant.id,
                'barcode': barcode,
                'uom_id': product_variant.uom_id.id,
                'price': sale_price,
                'company_id': company_kl.id,
                'arabic_price_alt': getattr(product_variant, 'arabic_price_alt', '') or '',
            })

            created_products += 1

            product_created_results.append(
                f"{name} | {internal_ref} | {barcode}"
            )

        # Build section header format
        section_header = "Product Name | Internal Reference | Barcode"
        separator = "-" * 60

        output_parts = [
            f"Products Created: {created_products}",
            f"Barcode Created: {barcode_created}",
            f"Skipped: {skipped}",
            f"Cost Updated: {cost_updated}",
            f"Barcode Conflicts: {barcode_conflicts}",  # NEW
            f"New Categories Created: {len(created_categories)}",
        ]

        if created_categories:
            output_parts.append(f"\nCreated Categories:\n" + "\n".join(created_categories))

        # Section 1: New Products & Barcode Created
        output_parts.append(f"\n{separator}")
        output_parts.append(f"NEW PRODUCTS CREATED ({len(product_created_results)})")
        output_parts.append(separator)
        output_parts.append(section_header)
        output_parts.append(separator)
        if product_created_results:
            output_parts.extend(product_created_results)
        else:
            output_parts.append("(none)")

        # Section 2: Product Existed, Barcode Created
        output_parts.append(f"\n{separator}")
        output_parts.append(f"PRODUCT EXISTED - BARCODE CREATED ({len(barcode_created_results)})")
        output_parts.append(separator)
        output_parts.append(section_header)
        output_parts.append(separator)
        if barcode_created_results:
            output_parts.extend(barcode_created_results)
        else:
            output_parts.append("(none)")

        # Section 3: Skipped (Product & Barcode Already Exist)
        output_parts.append(f"\n{separator}")
        output_parts.append(f"SKIPPED - PRODUCT & BARCODE ALREADY EXIST ({len(skipped_results)})")
        output_parts.append(separator)
        output_parts.append(section_header)
        output_parts.append(separator)
        if skipped_results:
            output_parts.extend(skipped_results)
        else:
            output_parts.append("(none)")

        # Section 4: Cost Updated
        output_parts.append(f"\n{separator}")
        output_parts.append(f"COST UPDATED ({len(updated_cost_results)})")
        output_parts.append(separator)
        output_parts.append("Product Name | Internal Reference | Old Cost | New Cost")
        output_parts.append(separator)
        if updated_cost_results:
            output_parts.extend(updated_cost_results)
        else:
            output_parts.append("(none)")

        # NEW: Section 5: Barcode Conflicts
        output_parts.append(f"\n{separator}")
        output_parts.append(f"BARCODE ALREADY ASSIGNED TO ANOTHER PRODUCT ({len(barcode_conflict_results)})")
        output_parts.append(separator)
        output_parts.append("Product Name | Internal Ref | Barcode | Already Linked To | Linked Product Ref | Linked Company")
        output_parts.append(separator)
        if barcode_conflict_results:
            output_parts.extend(barcode_conflict_results)
        else:
            output_parts.append("(none)")

        self.results = "\n".join(output_parts)
        return True

    def import_products_kk_company(self):
        """
        Import products for KK company from Excel.
        Excel columns (starting row 2):
          A: Internal Reference
          B: Cost
          C: Selling Price
          D: Category
          E: Product Name
          F: Barcode
          G: Purchase
          H: Sales
          I: Available in POS
          J: Track Inventory

        Logic:
          - Skip row if Internal Reference already exists in product.product
          - Stop if Category from Excel does not exist in Odoo (raise error)
          - Check if barcode already exists in product.barcode for KK company → if yes, skip row
          - Create product.product (with cost for KK company, no barcode/sale_price on product itself)
          - Create product.barcode record with price=sale_price, uom=product.uom_id, company=KK
        """
        if not self.worksheet:
            raise UserError(_('Please upload an Excel file'))

        excel_data = base64.b64decode(self.worksheet)
        try:
            wb = openpyxl.load_workbook(BytesIO(excel_data))
            sheet = wb.active
        except Exception as e:
            raise UserError(f"Error opening Excel: {e}")

        # Excel column indices
        INTERNAL_REF_COL = 1
        COST_COL = 2
        SALE_PRICE_COL = 3
        CATEGORY_COL = 4
        NAME_COL = 5
        BARCODE_COL = 6
        PURCHASE_COL = 7
        SALES_COL = 8
        POS_COL = 9
        TRACK_COL = 10

        # Find KK company
        company_kk = self.env['res.company'].sudo().search([('code', '=', 'KK')], limit=1)
        if not company_kk:
            raise UserError(_("Company with code 'KK' not found."))

        # Result buckets
        created_results = []
        barcode_created_results = []
        skipped_internal_ref = []
        skipped_barcode_conflict = []
        category_not_found_results = []

        created_count = 0
        barcode_created_count = 0
        skipped_ir_count = 0
        skipped_bc_count = 0
        category_stop_count = 0

        for row in range(2, sheet.max_row + 1):
            internal_ref = str(sheet.cell(row=row, column=INTERNAL_REF_COL).value or '').strip()
            name = str(sheet.cell(row=row, column=NAME_COL).value or '').strip()
            categ_name = str(sheet.cell(row=row, column=CATEGORY_COL).value or '').strip()
            barcode = str(sheet.cell(row=row, column=BARCODE_COL).value or '').strip()

            cost_val = sheet.cell(row=row, column=COST_COL).value or 0
            sale_price_val = sheet.cell(row=row, column=SALE_PRICE_COL).value or 0
            purchase_ok = sheet.cell(row=row, column=PURCHASE_COL).value
            sale_ok = sheet.cell(row=row, column=SALES_COL).value
            pos_ok = sheet.cell(row=row, column=POS_COL).value
            track_inventory = sheet.cell(row=row, column=TRACK_COL).value

            # Skip completely empty rows
            if not internal_ref and not name:
                continue

            try:
                cost = float(cost_val)
            except (TypeError, ValueError):
                cost = 0.0

            try:
                sale_price = float(sale_price_val)
            except (TypeError, ValueError):
                sale_price = 0.0

            # 1. Check if Internal Reference already exists → skip
            existing_product = self.env['product.product'].sudo().search(
                [('default_code', '=', internal_ref)], limit=1
            )
            if existing_product:
                skipped_ir_count += 1
                skipped_internal_ref.append(
                    f"{name} | {internal_ref} | {barcode}"
                )
                continue

            # 2. Check if category exists — STOP if not found
            if categ_name:
                category = self.env['product.category'].sudo().search(
                    [('name', '=', categ_name)], limit=1
                )
                if not category:
                    category_stop_count += 1
                    category_not_found_results.append(
                        f"{name} | {internal_ref} | {barcode} | Category: '{categ_name}'"
                    )
                    # Stop processing further rows
                    break
            else:
                category = False

            # 3. Check if barcode already exists in product.barcode for KK company → skip
            if barcode:
                existing_barcode = self.env['product.barcode'].sudo().search([
                    ('barcode', '=', barcode),
                    ('company_id', '=', company_kk.id),
                ], limit=1)
                if existing_barcode:
                    skipped_bc_count += 1
                    skipped_barcode_conflict.append(
                        f"{name} | {internal_ref} | {barcode} | "
                        f"Linked to: {existing_barcode.product_id.name} | "
                        f"{existing_barcode.product_id.default_code or ''}"
                    )
                    continue

            # 4. Create product.template / product.product
            tmpl_vals = {
                'name': name,
                'default_code': internal_ref,
                'purchase_ok': bool(purchase_ok),
                'sale_ok': bool(sale_ok),
                'available_in_pos': bool(pos_ok),
                'is_storable': bool(track_inventory),
                # No list_price / barcode on the product itself
            }
            if category:
                tmpl_vals['categ_id'] = category.id

            tmpl = self.env['product.template'].sudo().create(tmpl_vals)

            # 5. Set cost for KK company only
            tmpl.with_company(company_kk).sudo().write({'standard_price': cost})

            product_variant = tmpl.product_variant_id
            created_count += 1
            created_results.append(f"{name} | {internal_ref} | {barcode}")

            # 6. Create product.barcode record for KK company
            if barcode:
                self.env['product.barcode'].sudo().create({
                    'product_id': product_variant.id,
                    'barcode': barcode,
                    'uom_id': product_variant.uom_id.id,
                    'price': sale_price,
                    'company_id': company_kk.id,
                })
                barcode_created_count += 1
                barcode_created_results.append(f"{name} | {internal_ref} | {barcode} | Price: {sale_price}")

        # Build result output
        separator = "-" * 60
        section_header = "Product Name | Internal Reference | Barcode"

        output_parts = [
            f"[KK Company Import]",
            f"Products Created: {created_count}",
            f"Barcodes Created: {barcode_created_count}",
            f"Skipped (Internal Ref Exists): {skipped_ir_count}",
            f"Skipped (Barcode Conflict in KK): {skipped_bc_count}",
            f"Stopped (Category Not Found): {category_stop_count}",
        ]

        # Section 1: Products Created
        output_parts.append(f"\n{separator}")
        output_parts.append(f"PRODUCTS CREATED ({len(created_results)})")
        output_parts.append(separator)
        output_parts.append(section_header)
        output_parts.append(separator)
        output_parts.extend(created_results) if created_results else output_parts.append("(none)")

        # Section 2: Barcodes Created
        output_parts.append(f"\n{separator}")
        output_parts.append(f"BARCODES CREATED ({len(barcode_created_results)})")
        output_parts.append(separator)
        output_parts.append("Product Name | Internal Reference | Barcode | Price")
        output_parts.append(separator)
        output_parts.extend(barcode_created_results) if barcode_created_results else output_parts.append("(none)")

        # Section 3: Skipped - Internal Ref Exists
        output_parts.append(f"\n{separator}")
        output_parts.append(f"SKIPPED - INTERNAL REF ALREADY EXISTS ({len(skipped_internal_ref)})")
        output_parts.append(separator)
        output_parts.append(section_header)
        output_parts.append(separator)
        output_parts.extend(skipped_internal_ref) if skipped_internal_ref else output_parts.append("(none)")

        # Section 4: Skipped - Barcode Conflict
        output_parts.append(f"\n{separator}")
        output_parts.append(f"SKIPPED - BARCODE ALREADY EXISTS IN KK ({len(skipped_barcode_conflict)})")
        output_parts.append(separator)
        output_parts.append("Product Name | Internal Ref | Barcode | Linked To | Linked Ref")
        output_parts.append(separator)
        output_parts.extend(skipped_barcode_conflict) if skipped_barcode_conflict else output_parts.append("(none)")

        # Section 5: Category Not Found (caused stop)
        output_parts.append(f"\n{separator}")
        output_parts.append(f"STOPPED - CATEGORY NOT FOUND ({len(category_not_found_results)})")
        output_parts.append(separator)
        output_parts.append("Product Name | Internal Ref | Barcode | Category")
        output_parts.append(separator)
        output_parts.extend(category_not_found_results) if category_not_found_results else output_parts.append("(none)")

        self.results = "\n".join(output_parts)
        return True


    def assign_pos_category_by_companys(self):
        """
        Assign POS categories to products based on which company's product.barcode records exist.
        """
        Product = self.env['product.product']
        POSCategory = self.env['pos.category']
        Barcode = self.env['product.barcode'].sudo()

        # --- Step 1: Look up companies by code ---
        company_kk = self.env['res.company'].sudo().search([('code', '=', 'KK')], limit=1)
        company_kl = self.env['res.company'].sudo().search([('code', '=', 'KL')], limit=1)

        if not company_kk or not company_kl:
            raise UserError(_("Both companies with code 'KK' and 'KL' must exist."))

        # --- Step 2: Ensure the 3 fixed POS categories exist ---
        kitchenkraft_categ = POSCategory.search([('name', '=', 'Kitchenkraft')], limit=1)
        if not kitchenkraft_categ:
            kitchenkraft_categ = POSCategory.create({'name': 'Kitchenkraft'})

        klassic_categ = POSCategory.search([('name', '=', 'Klassic Kitchen')], limit=1)
        if not klassic_categ:
            klassic_categ = POSCategory.create({'name': 'Klassic Kitchen'})

        common_categ = POSCategory.search([('name', '=', 'Common')], limit=1)
        if not common_categ:
            common_categ = POSCategory.create({'name': 'Common'})

        updated_prod = 0
        skipped = 0
        common_count = 0
        kitchenkraft_count = 0
        klassic_count = 0

        # Set to track products that exist but have no product.barcode records
        # Format: "product_name | internal_reference | company"
        no_barcode_products = set()

        all_products = Product.search([])

        for product in all_products:
            # --- Step 3: Check if product.barcode exists for each company ---
            barcode_kk = Barcode.search([
                ('product_id', '=', product.id),
                ('company_id', '=', company_kk.id)
            ], limit=1)
            print("product name",product.name,"barcode_kk",barcode_kk.barcode if barcode_kk else "No Barcode")

            barcode_kl = Barcode.search([
                ('product_id', '=', product.id),
                ('company_id', '=', company_kl.id)
            ], limit=1)
            print("product name", product.name, "barcode_kl", barcode_kl.barcode if barcode_kl else "No Barcode")

            has_kk = bool(barcode_kk)
            has_kl = bool(barcode_kl)

            print("Processing Product:", product.name, "(ID:", product.id, ")",
                  "| KK:", has_kk, "| KL:", has_kl)

            if has_kk and has_kl:
                # Barcode exists in BOTH companies → Common
                pos_category = common_categ
                common_count += 1
            elif has_kk:
                # Barcode exists ONLY in KK → Kitchenkraft
                pos_category = kitchenkraft_categ
                kitchenkraft_count += 1
            elif has_kl:
                # Barcode exists ONLY in KL → Klassic Kitchen
                pos_category = klassic_categ
                klassic_count += 1
            else:
                # No barcode in either company → skip & track
                company_name = product.company_id.name if product.company_id else 'No Company'
                internal_ref = product.default_code or 'N/A'
                no_barcode_products.add(
                    f"{product.name} | {internal_ref} | {company_name}"
                )
                skipped += 1
                continue

            # --- Step 4: Assign POS category to product template (replace) ---
            template = product.product_tmpl_id
            if pos_category not in template.pos_categ_ids:
                template.pos_categ_ids = [(6, 0, [pos_category.id])]
                updated_prod += 1
            else:
                skipped += 1

        # --- Step 5: Build the no-barcode product list ---
        no_barcode_list = "\n".join(sorted(no_barcode_products)) if no_barcode_products else "None"

        result_msg = (
            f"POS Category Assignment Completed\n"
            f"Updated Products: {updated_prod}\n"
            f"Skipped: {skipped}\n\n"
            f"--- Category Breakdown ---\n"
            f"Common: {common_count}\n"
            f"Kitchenkraft: {kitchenkraft_count}\n"
            f"Klassic Kitchen: {klassic_count}\n\n"
            f"--- Products with NO product.barcode ({len(no_barcode_products)}) ---\n"
            f"Name | Internal Reference | Company\n"
            f"{no_barcode_list}"
        )

        self.results = result_msg
        print(result_msg)
        return True


    def compare_barcodes_excel_odoo(self):
        print("====== Started compare_barcodes_excel_odoo ======")
        if not self.worksheet:
            raise UserError(_('Please upload an Excel file'))

        excel_data = base64.b64decode(self.worksheet)

        try:
            wb = openpyxl.load_workbook(BytesIO(excel_data))
            sheet = wb.active
            print(f"Loaded Excel sheet with max_row: {sheet.max_row}")
        except Exception as e:
            raise UserError(f"Error opening Excel: {e}")
            
        company_kk = self.env['res.company'].sudo().search([('code', '=', 'KK')], limit=1)
        print(f"Company KK found: {company_kk.name if company_kk else 'Not Found'}")
        if not company_kk:
            raise UserError(_("Company with code 'KK' not found."))

        matched_records = []
        price_mismatch = []
        not_found_odoo = []
        no_barcode_in_odoo = []
        multiple_barcodes_skipped = []

        total_records = 0

        # Start from row 3 to skip header
        for row in range(3, sheet.max_row + 1):
            icode_val = sheet.cell(row=row, column=1).value
            price_val = sheet.cell(row=row, column=4).value
            item_name_val = sheet.cell(row=row, column=2).value
            barcode_val = sheet.cell(row=row, column=5).value
            
            icode = str(icode_val).strip() if icode_val is not None else ''
            item_name = str(item_name_val).strip() if item_name_val is not None else ''
            excel_barcode = str(barcode_val).strip() if barcode_val is not None else ''
            if not icode:
                continue
                
            total_records += 1
            print(f"\n--- Checking Row {row} | ICODE: '{icode}' | Excel Price: '{price_val}' ---")
                
            try:
                excel_price = float(price_val) if price_val is not None else 0.0
            except:
                excel_price = 0.0
                
            # Step 1: Search product by internal reference
            product = self.env['product.product'].sudo().search([('default_code', '=', icode)], limit=1)
            
            if not product:
                print(f"[X] Product NOT FOUND for ICODE: '{icode}'")
                not_found_odoo.append(f"{icode} | {excel_price} | {item_name} | {excel_barcode}")
                continue
                
            print(f"[OK] Product Found: '{product.name}' (ID: {product.id})")
            
            # Step 2: Get product_id and check product.barcode for price
            odoo_barcodes = self.env['product.barcode'].sudo().search([
                ('product_id', '=', product.id),
                ('company_id', '=', company_kk.id)
            ])
            
            if not odoo_barcodes:
                print(f"[!] NO KK BARCODE in Odoo for Product: '{product.name}'")
                product_name = product.name or ''
                no_barcode_in_odoo.append(f"{icode} | {excel_price} | {product_name}")
                continue
            if len(odoo_barcodes) > 1:
                print(f"[!] MULTIPLE Barcodes Found for Product: '{product.name}'. Skipping update.")
                multiple_barcodes_skipped.append(f"{icode} | {excel_price} | {product.name or ''} | {len(odoo_barcodes)} barcodes")
                continue
                
            # If exactly 1 barcode
            ob = odoo_barcodes[0]
            odoo_price = float(ob.price)
            if abs(excel_price - odoo_price) < 0.001:
                print(f"[OK] Price MATCHED! (Excel: {excel_price} == Odoo: {odoo_price}) Barcode: {ob.barcode}")
                matched_records.append(f"{icode} | {excel_price} | {odoo_price} | {product.name or ''} | {ob.barcode or ''}")
            else:
                print(f"[X] Price MISMATCH! (Excel: {excel_price} != Odoo: {odoo_price}) Barcode: {ob.barcode}. UPDATING PRICE.")
                # Update price
                ob.write({'price': excel_price})
                price_mismatch.append(f"{icode} | {excel_price} | {odoo_price} | {product.name or ''} | {ob.barcode or ''} -> (Updated to {excel_price})")

        print("\n====== Comparison Summary ======")
        print(f"Total Processed: {total_records}")
        print(f"Matched Records (Same Price): {len(matched_records)}")
        print(f"Price Mismatch (Price UPDATED): {len(price_mismatch)}")
        print(f"Product Not Found in Odoo: {len(not_found_odoo)}")
        print(f"Product Found but NO KK Barcode: {len(no_barcode_in_odoo)}")
        print(f"Multiple Barcodes (Skipped Update): {len(multiple_barcodes_skipped)}")
        print("================================\n")

        separator = "-" * 80
        
        output_parts = [
            f"Matched Records (Same Price): {len(matched_records)}",
            f"Price Mismatch (Price UPDATED): {len(price_mismatch)}",
            f"Product Not Found in Odoo: {len(not_found_odoo)}",
            f"Product Found but NO KK Barcode in Odoo: {len(no_barcode_in_odoo)}",
            f"Multiple Barcodes (Skipped Update): {len(multiple_barcodes_skipped)}"
        ]
        
        output_parts.append(f"\n{separator}")
        output_parts.append(f"PRICE MISMATCH (PRICE UPDATED MAPPED TO EXCEL) ({len(price_mismatch)})")
        output_parts.append(separator)
        output_parts.append("ICODE | Excel Price | Odoo Old Price | Product Name | Barcode -> Status")
        output_parts.append(separator)
        if price_mismatch:
            output_parts.extend(price_mismatch)
        else:
            output_parts.append("(none)")
            
        output_parts.append(f"\n{separator}")
        output_parts.append(f"MULTIPLE BARCODES (SKIPPED UPDATE) ({len(multiple_barcodes_skipped)})")
        output_parts.append(separator)
        output_parts.append("ICODE | Excel Price | Product Name | Info")
        output_parts.append(separator)
        if multiple_barcodes_skipped:
            output_parts.extend(multiple_barcodes_skipped)
        else:
            output_parts.append("(none)")
            
        output_parts.append(f"\n{separator}")
        output_parts.append(f"PRODUCT NOT FOUND IN ODOO ({len(not_found_odoo)})")
        output_parts.append(separator)
        output_parts.append("ICODE | Excel Price | Product Name | Barcode")
        output_parts.append(separator)
        if not_found_odoo:
            output_parts.extend(not_found_odoo)
        else:
            output_parts.append("(none)")
            
        output_parts.append(f"\n{separator}")
        output_parts.append(f"PRODUCT FOUND BUT NO KK BARCODE IN ODOO ({len(no_barcode_in_odoo)})")
        output_parts.append(separator)
        output_parts.append("ICODE | Excel Price | Product Name")
        output_parts.append(separator)
        if no_barcode_in_odoo:
            output_parts.extend(no_barcode_in_odoo)
        else:
            output_parts.append("(none)")
            
        output_parts.append(f"\n{separator}")
        output_parts.append(f"MATCHED RECORDS (PRICE IS SAME) ({len(matched_records)})")
        output_parts.append(separator)
        output_parts.append("ICODE | Excel Price | Odoo Price | Product Name | Barcode")
        output_parts.append(separator)
        if matched_records:
            output_parts.extend(matched_records)
        else:
            output_parts.append("(none)")

        self.results = "\n".join(output_parts)
        return True

    def check_sold_in_pos(self):
        print("====== Started check_sold_in_pos ======")
        if not self.worksheet:
            raise UserError(_('Please upload an Excel file'))

        excel_data = base64.b64decode(self.worksheet)

        try:
            wb = openpyxl.load_workbook(BytesIO(excel_data))
            sheet = wb.active
            print(f"Loaded Excel sheet with max_row: {sheet.max_row}")
        except Exception as e:
            raise UserError(f"Error opening Excel: {e}")

        # Lists for final output
        sold_in_pos = []
        never_sold_in_pos = []
        barcode_not_linked = []
        product_not_found = []

        total_records = 0
        company_kk = self.env['res.company'].sudo().search([('code', '=', 'KK')], limit=1)
        print(f"Company KK found: {company_kk.name if company_kk else 'Not Found'}")

        # Start from row 2 to skip header (Barcode, Internal Reference)
        for row in range(2, sheet.max_row + 1):
            barcode_val = sheet.cell(row=row, column=1).value
            internal_ref_val = sheet.cell(row=row, column=2).value
            
            barcode = str(barcode_val).strip() if barcode_val is not None else ''
            internal_ref = str(internal_ref_val).strip() if internal_ref_val is not None else ''

            if not barcode and not internal_ref:
                continue


            total_records += 1
            print(f"\n--- Checking Row {row} | Barcode: '{barcode}' | Internal Ref: '{internal_ref}' ---")

            # Step 1: Find Product
            product = self.env['product.product'].sudo().search([('default_code', '=', internal_ref)], limit=1)
            if not product:
                print(f"[X] Product NOT FOUND for Internal Ref: '{internal_ref}'")
                product_not_found.append(f"{barcode} | {internal_ref}")
                continue
                
            product_name = product.name or ''
            print(f"[OK] Product Found: '{product_name}' (ID: {product.id})")

            # Step 2: Validate Barcode
            barcode_record = self.env['product.barcode'].sudo().search([
                ('product_id', '=', product.id),
                ('barcode', '=', barcode),
                ('company_id', '=', company_kk.id)
            ], limit=1)

            if not barcode_record:
                print(f"[!] Barcode NOT LINKED for Product: '{product_name}', Barcode: '{barcode}' under Company KK")
                barcode_not_linked.append(f"{barcode} | {internal_ref} | {product_name}")
                continue

            print("[OK] Barcode cleanly linked to product and company.")

            # Step 3: Check POS Sales
            pos_line = self.env['pos.order.line'].sudo().search([
                ('product_id', '=', product.id),
                ('order_id.state', 'in', ['paid', 'done', 'invoiced'])
            ], limit=1)

            if pos_line:
                print(f"[OK] SOLD IN POS! Found pos.order.line (ID: {pos_line.id})")
                sold_in_pos.append(f"{barcode} | {internal_ref} | {product_name}")
            else:
                print("[X] NEVER SOLD IN POS!")
                never_sold_in_pos.append(f"{barcode} | {internal_ref} | {product_name}")

        print("\n====== Validation Summary ======")
        print(f"Total Processed: {total_records}")
        print(f"Sold in POS: {len(sold_in_pos)}")
        print(f"Never Sold in POS: {len(never_sold_in_pos)}")
        print(f"Barcode Not Linked: {len(barcode_not_linked)}")
        print(f"Product Not Found: {len(product_not_found)}")
        print("================================\n")

        separator = "-" * 80
        
        output_parts = [
            f"Total Records: {total_records}",
        ]
        
        output_parts.append(f"\nSOLD IN POS ({len(sold_in_pos)})")
        output_parts.append(separator)
        output_parts.append("Barcode | Internal Ref | Product Name")
        output_parts.append(separator)
        if sold_in_pos:
            output_parts.extend(sold_in_pos)
        else:
            output_parts.append("(none)")

        output_parts.append(f"\nNEVER SOLD IN POS ({len(never_sold_in_pos)})")
        output_parts.append(separator)
        output_parts.append("Barcode | Internal Ref | Product Name")
        output_parts.append(separator)
        if never_sold_in_pos:
            output_parts.extend(never_sold_in_pos)
        else:
            output_parts.append("(none)")

        output_parts.append(f"\nBARCODE NOT LINKED ({len(barcode_not_linked)})")
        output_parts.append(separator)
        output_parts.append("Barcode | Internal Ref | Product Name")
        output_parts.append(separator)
        if barcode_not_linked:
            output_parts.extend(barcode_not_linked)
        else:
            output_parts.append("(none)")

        output_parts.append(f"\nPRODUCT NOT FOUND ({len(product_not_found)})")
        output_parts.append(separator)
        output_parts.append("Barcode | Internal Ref")
        output_parts.append(separator)
        if product_not_found:
            output_parts.extend(product_not_found)
        else:
            output_parts.append("(none)")

        self.results = "\n".join(output_parts)
        return True
