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
        updated_count = 0
        skipped_count = 0
        moved_to_barcode = 0

        for row in range(4, sheet.max_row + 1):


            item_code = str(sheet.cell(row=row,
                                       column=ITEM_CODE_COL + 1).value or '').strip()
            product_name = str(sheet.cell(row=row,
                                          column=PRODUCT_NAME_COL + 1).value or '').strip()
            description = str(sheet.cell(row=row,
                                         column=DESCRIPTION_COL + 1).value or '').strip()
            arabic_name = str(sheet.cell(row=row,
                                         column=ARABIC_NAME_COL + 1).value or '').strip()
            sub_category = str(sheet.cell(row=row,
                                          column=SUB_CATEGORY_COL + 1).value or '').strip()
            brand = str(
                sheet.cell(row=row, column=BRAND_COL + 1).value or '').strip()
            origin = str(
                sheet.cell(row=row, column=ORIGIN_COL + 1).value or '').strip()
            uom_name = str(
                sheet.cell(row=row, column=UOM_COL + 1).value or '').strip()
            cost = sheet.cell(row=row, column=COST_COL + 1).value or 0.0
            sale_price = sheet.cell(row=row,
                                    column=SALE_PRICE_COL + 1).value or 0.0
            barcode = str(sheet.cell(row=row,
                                     column=BARCODE_COL + 1).value or '').strip()
            # company_name = str(sheet.cell(row=row,
            #                               column=COMPANY_COL + 1).value or '').strip()

            company_name = self.env['res.company'].search(
                [('code', '=', 'KK')], limit=1).name
            print(
                f"\nRow {row}: "
                f"item_code={item_code}, "
                f"product_name={product_name}, "
                f"description={description}, "
                f"arabic_name={arabic_name}, "
                f"sub_category={sub_category}, "
                f"brand={brand}, "
                f"origin={origin}, "
                f"uom_name={uom_name}, "
                f"cost={cost}, "
                f"sale_price={sale_price}, "
                f"barcode={barcode}, "
                f"company_name={company_name}"
            )


            if not item_code and not barcode and not product_name:
                skipped_count += 1
                continue


            company = self.env['res.company'].search(
                [('name', '=', company_name)], limit=1)
            if not company:
                print(f"Company not found: {company_name}")
                skipped_count += 1
                continue


            category_id = False
            if sub_category:
                category = self.env['product.category'].search(
                    [('name', '=', sub_category)], limit=1)
                if category:
                    category_id = category.id


            uom = False
            uom_id = False
            if uom_name:
                uom = self.env['uom.uom'].search([('name', '=', uom_name)],
                                                 limit=1)
                if uom:
                    uom_id = uom.id
            else:
                print("No UoM name provided in Excel row")

            current_company = self.env.company
            print("Current Company:", self.env.company.name)


            existing_product = self.env['product.product'].search([
                '|',
                ('default_code', '=', item_code),
                ('barcode', '=', barcode)
            ], limit=1)

            if existing_product:
                #Already exists move barcode
                existing = self.env['product.barcode'].search([
                    ('barcode', '=', barcode),
                    ('product_id', '=', existing_product.id),
                    ('company_id', '=', current_company.id)
                ], limit=1)

                if not existing:
                    self.env['product.barcode'].create({
                        'product_id': existing_product.id,
                        'barcode': barcode,
                        'uom_id': existing_product.uom_id.id or (uom_id or 28),
                        'price': sale_price or existing_product.lst_price or 0.0,
                        'company_id': current_company.id,
                        'arabic_price_alt': getattr(existing_product,
                                                    'arabic_price_alt',
                                                    '') or '',
                    })
                    moved_to_barcode += 1

                    existing_product.write({
                        'barcode': False,
                        'lst_price': 0.0,
                    })
                else:
                    skipped_count += 1

                updated_count += 1

            else:

                tmpl_vals = {
                    'name': product_name or 'Unnamed',
                    'default_code': item_code or '',
                    'list_price': sale_price or 0.0,
                    'standard_price': cost or 0.0,
                    'description': description or '',
                    'arabic_name': arabic_name or '',
                    'brand': brand or '',
                    'categ_id': category_id if category_id else 447,
                    'uom_id': uom_id if uom_id else 28,
                    'uom_po_id': uom_id if uom_id else 28,
                    'company_id': current_company.id,
                }

                tmpl = self.env['product.template'].create(tmpl_vals)
                product_variant = tmpl.product_variant_id

                if barcode:
                    product_variant.barcode = barcode

                self.env['product.barcode'].sudo().create({
                    'product_id': product_variant.id,
                    'barcode': barcode,
                    'uom_id': product_variant.uom_id.id or uom_id,
                    'price': sale_price or 0.0,
                    'company_id': company.id,
                    'arabic_price_alt': getattr(product_variant,
                                                'arabic_price_alt', '') or '',
                })

                product_variant.write({
                    'barcode': False,
                    'lst_price': 0.0,
                })

                created_count += 1


        self.results = (
            f"Created New: {created_count}\n"
            f"Updated Existing: {updated_count}\n"
            f"Moved to Barcode: {moved_to_barcode}\n"
            f"Skipped: {skipped_count}"
        )

        print(self.results)
        return True

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











