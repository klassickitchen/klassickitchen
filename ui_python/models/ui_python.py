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