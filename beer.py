"""```python type="interpreter"
import pandas as pd
import json

# 用户提供的啤酒数据
beer_data = {
    "id": "tmEthz",
    "name": "\"Admiral\" Stache",
    "nameDisplay": "\"Admiral\" Stache",
    "description": "Milwaukee Brewing Co’s take on a classic European style. Baltic Porters are the stronger lager fermented cousin of the classic London Porter. The higher strength and cold fermentation help to create a smooth, less fruity porter, rich in roasted malt flavors and aromas. The “Admiral” Stache has a deep brown hue with a light caramel head. Toffee and milk chocolate dominate the flavor with subtle hints of dried fruit. One month of aging in Bourbon Barrels imparted a layer of vanilla and oak.\r\n\r\nWe first developed this beer in 2007. Our first attempted batch of beer at the 2nd street location was a Baltic Porter. What we ended up with became known as “Shake Down Nut Brown”. You can guess what went wrong from there… But, so many things right! Every year that has gone by, the beer has gotten a little bit stronger, in flavor and alcohol.\r\n\r\nWe use a black malt for the dark rich color and an extra special malt for the dried fruit flavors. Baltic Porters are fermented cold with a lager yeast. That long slow maturation creates a smooth flavor profile. The anticipation of the bourbon barrel aging it the most exciting part of this brew process. We want that oak character with hints of bourbon, we use 3rd run barrels for this result. Each batch has been slightly different from the last.",
    "abv": "7",
    "ibu": "23",
    "glasswareId": 5,
    "srmId": 37,
    "availableId": 4,
    "styleId": 104,
    "isOrganic": "N",
    "isRetired": "N",
    "labels": {
        "icon": "<document reference_id=\"<|document|>:6508\"><url>https://brewerydb-images.s3.amazonaws.com/beer/tmEthz/upload_3Jl1St-icon.png</url></document>",
        "medium": "<document reference_id=\"<|document|>:1107\"><url>https://brewerydb-images.s3.amazonaws.com/beer/tmEthz/upload_3Jl1St-medium.png</url></document>",
        "large": "<document reference_id=\"<|document|>:c5e2\"><url>https://brewerydb-images.s3.amazonaws.com/beer/tmEthz/upload_3Jl1St-large.png</url></document>",
        "contentAwareIcon": "<document reference_id=\"<|document|>:47d7\"><url>https://brewerydb-images.s3.amazonaws.com/beer/tmEthz/upload_3Jl1St-contentAwareIcon.png</url></document>",
        "contentAwareMedium": "<document reference_id=\"<|document|>:bbc8\"><url>https://brewerydb-images.s3.amazonaws.com/beer/tmEthz/upload_3Jl1St-contentAwareMedium.png</url></document>",
        "contentAwareLarge": "<document reference_id=\"<|document|>:551f\"><url>https://brewerydb-images.s3.amazonaws.com/beer/tmEthz/upload_3Jl1St-contentAwareLarge.png</url></document>"
    },
    "status": "verified",
    "statusDisplay": "Verified",
    "originalGravity": "1.071",
    "createDate": "2012-09-09 13:35:27",
    "updateDate": "2016-11-11 14:23:06",
    "glass": {
        "id": 5,
        "name": "Pint",
        "createDate": "2012-01-03 02:41:33"
    },
    "srm": {
        "id": 37,
        "name": "37",
        "hex": "3F0708"
    },
    "available": {
        "id": 4,
        "name": "Seasonal",
        "description": "Available at the same time of year, every year."
    },
    "style": {
        "id": 104,
        "categoryId": 9,
        "category": {
            "id": 9,
            "name": "Other Lager",
            "createDate": "2012-03-21 20:06:46"
        }
    }
}

# 展平嵌套的JSON数据
def flatten_json(nested_json, parent_key='', sep='_'):
    items = []
    for k, v in nested_json.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_json(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

# 展平数据
flattened_data = flatten_json(beer_data)

# 转换为DataFrame
df = pd.DataFrame([flattened_data])

# 输出数据基本信息
print("===== 数据集基本信息 =====")
df.info()

print("\n===== 数据集所有字段列表 =====")
for idx, col in enumerate(df.columns, 1):
    print(f"{idx}. {col}")

print("\n===== 数据集核心内容预览 =====")
# 筛选核心字段展示
core_columns = [
    'id', 'name', 'abv', 'ibu', 'isOrganic', 'isRetired', 'status',
    'originalGravity', 'glass_name', 'srm_name', 'available_name',
    'style_category_name', 'createDate', 'updateDate'
]
print(df[core_columns].T)

print("\n===== 啤酒描述核心信息提取 =====")
description = beer_data['description']
# 提取关键信息
print(f"啤酒风格: Baltic Porter（波罗的海波特），属于 {beer_data['style']['category']['name']} 大类")
print(f"酒精度(ABV): {beer_data['abv']}%")
print(f"苦度值(IBU): {beer_data['ibu']}")
print(f"色度(SRM): {beer_data['srm']['name']}，色值Hex: {beer_data['srm']['hex']}")
print(f"上市类型: {beer_data['available']['name']} - {beer_data['available']['description']}")
print(f"推荐杯型: {beer_data['glass']['name']}")
print(f"是否有机: {'是' if beer_data['isOrganic'] == 'Y' else '否'}")
print(f"是否已停产: {'是' if beer_data['isRetired'] == 'Y' else '否'}")
print(f"数据状态: {beer_data['statusDisplay']}")
print(f"首次开发年份: 2007年")
print(f"数据创建时间: {beer_data['createDate']}")
print(f"数据最后更新时间: {beer_data['updateDate']}")"""


"""```python type="interpreter"
import pandas as pd
import json
import unicodedata
import openpyxl
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# 用户提供的啤酒数据
beer_data = {
    "id": "tmEthz",
    "name": "\"Admiral\" Stache",
    "nameDisplay": "\"Admiral\" Stache",
    "description": "Milwaukee Brewing Co’s take on a classic European style. Baltic Porters are the stronger lager fermented cousin of the classic London Porter. The higher strength and cold fermentation help to create a smooth, less fruity porter, rich in roasted malt flavors and aromas. The “Admiral” Stache has a deep brown hue with a light caramel head. Toffee and milk chocolate dominate the flavor with subtle hints of dried fruit. One month of aging in Bourbon Barrels imparted a layer of vanilla and oak.\r\n\r\nWe first developed this beer in 2007. Our first attempted batch of beer at the 2nd street location was a Baltic Porter. What we ended up with became known as “Shake Down Nut Brown”. You can guess what went wrong from there… But, so many things right! Every year that has gone by, the beer has gotten a little bit stronger, in flavor and alcohol.\r\n\r\nWe use a black malt for the dark rich color and an extra special malt for the dried fruit flavors. Baltic Porters are fermented cold with a lager yeast. That long slow maturation creates a smooth flavor profile. The anticipation of the bourbon barrel aging it the most exciting part of this brew process. We want that oak character with hints of bourbon, we use 3rd run barrels for this result. Each batch has been slightly different from the last.",
    "abv": "7",
    "ibu": "23",
    "glasswareId": 5,
    "srmId": 37,
    "availableId": 4,
    "styleId": 104,
    "isOrganic": "N",
    "isRetired": "N",
    "labels": {
        "icon": "<document reference_id=\"<|document|>:6508\"><url>https://brewerydb-images.s3.amazonaws.com/beer/tmEthz/upload_3Jl1St-icon.png</url></document>",
        "medium": "<document reference_id=\"<|document|>:1107\"><url>https://brewerydb-images.s3.amazonaws.com/beer/tmEthz/upload_3Jl1St-medium.png</url></document>",
        "large": "<document reference_id=\"<|document|>:c5e2\"><url>https://brewerydb-images.s3.amazonaws.com/beer/tmEthz/upload_3Jl1St-large.png</url></document>",
        "contentAwareIcon": "<document reference_id=\"<|document|>:47d7\"><url>https://brewerydb-images.s3.amazonaws.com/beer/tmEthz/upload_3Jl1St-contentAwareIcon.png</url></document>",
        "contentAwareMedium": "<document reference_id=\"<|document|>:bbc8\"><url>https://brewerydb-images.s3.amazonaws.com/beer/tmEthz/upload_3Jl1St-contentAwareMedium.png</url></document>",
        "contentAwareLarge": "<document reference_id=\"<|document|>:551f\"><url>https://brewerydb-images.s3.amazonaws.com/beer/tmEthz/upload_3Jl1St-contentAwareLarge.png</url></document>"
    },
    "status": "verified",
    "statusDisplay": "Verified",
    "originalGravity": "1.071",
    "createDate": "2012-09-09 13:35:27",
    "updateDate": "2016-11-11 14:23:06",
    "glass": {
        "id": 5,
        "name": "Pint",
        "createDate": "2012-01-03 02:41:33"
    },
    "srm": {
        "id": 37,
        "name": "37",
        "hex": "3F0708"
    },
    "available": {
        "id": 4,
        "name": "Seasonal",
        "description": "Available at the same time of year, every year."
    },
    "style": {
        "id": 104,
        "categoryId": 9,
        "category": {
            "id": 9,
            "name": "Other Lager",
            "createDate": "2012-03-21 20:06:46"
        }
    }
}

# 展平嵌套的JSON数据
def flatten_json(nested_json, parent_key='', sep='_'):
    items = []
    for k, v in nested_json.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_json(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

# 展平数据
flattened_data = flatten_json(beer_data)
df = pd.DataFrame([flattened_data])

# 生成Excel文件
wb = Workbook()

# 1. 数据明细Sheet
ws_detail = wb.active
ws_detail.title = "啤酒数据明细"

# 样式定义
# 表头样式
header_fill = PatternFill('solid', fgColor='0070C0')
header_font = Font(name='Arial', bold=True, color='FFFFFF', size=11)
center_align = Alignment(horizontal='center', vertical='center', wrap_text=True)
left_align = Alignment(horizontal='left', vertical='center', wrap_text=True)
right_align = Alignment(horizontal='right', vertical='center', wrap_text=True)
thin_gray = Side(style='thin', color='D9D9D9')
h_border = Border(bottom=thin_gray)

# 写入表头
headers = df.columns.tolist()
for col_idx, header in enumerate(headers, 1):
    cell = ws_detail.cell(row=1, column=col_idx, value=header)
    cell.font = header_font
    cell.fill = header_fill
    cell.alignment = center_align
    cell.border = h_border

# 写入数据
for row_idx, row_data in enumerate(df.values, 2):
    for col_idx, value in enumerate(row_data, 1):
        cell = ws_detail.cell(row=row_idx, column=col_idx, value=value)
        # 对齐方式：文本左对齐，数值右对齐，其他居中
        if isinstance(value, str):
            cell.alignment = left_align
        elif isinstance(value, (int, float)):
            cell.alignment = right_align
        else:
            cell.alignment = center_align
        cell.border = h_border

# 自动调整列宽
def display_width(text):
    return sum(2 if unicodedata.east_asian_width(c) in ('F','W') else 1 for c in str(text or ''))

def auto_fit_columns(ws, min_w=8, max_w=50, padding=3):
    for col_cells in ws.columns:
        letter = col_cells[0].column_letter
        w = max((display_width(c.value) for c in col_cells
                 if not isinstance(c, openpyxl.cell.cell.MergedCell) and c.value is not None), default=0)
        ws.column_dimensions[letter].width = max(min_w, min(w * 1.1 + padding, max_w))

auto_fit_columns(ws_detail)
# 冻结表头
ws_detail.freeze_panes = 'A2'

# 2. 数据分析总结Sheet
ws_summary = wb.create_sheet("啤酒信息分析总结")

# 标题样式
title_fill = PatternFill('solid', fgColor='003366')
title_font = Font(name='Arial', bold=True, color='FFFFFF', size=14)
summary_header_fill = PatternFill('solid', fgColor='D9E1F2')
summary_header_font = Font(name='Arial', bold=True, color='000000', size=11)

# 写入标题
ws_summary.merge_cells('A1:B1')
title_cell = ws_summary['A1']
title_cell.value = "\"Admiral\" Stache 啤酒数据集分析总结"
title_cell.font = title_font
title_cell.fill = title_fill
title_cell.alignment = center_align
ws_summary.row_dimensions[1].height = 40

# 核心信息汇总
summary_data = [
    ["指标", "详情"],
    ["啤酒ID", beer_data['id']],
    ["啤酒名称", beer_data['name']],
    ["啤酒风格", f"Baltic Porter（波罗的海波特），属于 {beer_data['style']['category']['name']} 大类"],
    ["酒精度(ABV)", f"{beer_data['abv']}%"],
    ["苦度值(IBU)", beer_data['ibu']],
    ["色度(SRM)", f"{beer_data['srm']['name']}，色值Hex: {beer_data['srm']['hex']}"],
    ["原麦汁浓度", beer_data['originalGravity']],
    ["上市类型", f"{beer_data['available']['name']} - {beer_data['available']['description']}"],
    ["推荐杯型", beer_data['glass']['name']],
    ["是否有机", "是" if beer_data['isOrganic'] == 'Y' else "否"],
    ["是否已停产", "是" if beer_data['isRetired'] == 'Y' else "否"],
    ["数据状态", beer_data['statusDisplay']],
    ["首次开发年份", "2007年"],
    ["数据创建时间", beer_data['createDate']],
    ["数据最后更新时间", beer_data['updateDate']]
]

# 写入汇总数据
for row_idx, row_data in enumerate(summary_data, 2):
    for col_idx, value in enumerate(row_data, 1):
        cell = ws_summary.cell(row=row_idx, column=col_idx, value=value)
        # 表头行样式
        if row_idx == 2:
            cell.font = summary_header_font
            cell.fill = summary_header_fill
            cell.alignment = center_align
        else:
            if col_idx == 1:
                cell.font = Font(bold=True)
                cell.alignment = left_align
            else:
                cell.alignment = left_align
        cell.border = h_border

# 调整列宽
auto_fit_columns(ws_summary, min_w=10, max_w=60)
# 冻结表头
ws_summary.freeze_panes = 'A3'

# 3. 啤酒描述详情Sheet
ws_desc = wb.create_sheet("啤酒详细描述")
# 写入标题
ws_desc.merge_cells('A1:A1')
desc_title = ws_desc['A1']
desc_title.value = "\"Admiral\" Stache 啤酒详细描述"
desc_title.font = title_font
desc_title.fill = title_fill
desc_title.alignment = center_align
ws_desc.row_dimensions[1].height = 40

# 写入描述内容
desc_content = beer_data['description'].replace('\r\n', '\n')
ws_desc['A2'] = desc_content
ws_desc['A2'].alignment = left_align
ws_desc['A2'].font = Font(name='Arial', size=11)
# 调整列宽和行高
ws_desc.column_dimensions['A'].width = 120
ws_desc.row_dimensions[2].height = 300
# 自动换行
ws_desc['A2'].alignment = Alignment(horizontal='left', vertical='top', wrap_text=True)

# 保存文件
output_path = '/mnt/啤酒数据集分析结果.xlsx'
wb.save(output_path)

print(f"Excel文件已生成，保存路径: {output_path}")
print("文件包含3个工作表：")
print("1. 啤酒数据明细：完整的展平后所有字段数据")
print("2. 啤酒信息分析总结：核心指标的结构化汇总")
print("3. 啤酒详细描述：啤酒的完整介绍文本")"""



"""python type="interpreter"
import pandas as pd
import json
import unicodedata
import openpyxl
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# 用户提供的啤酒数据
beer_data = {
    "id": "tmEthz",
    "name": "\"Admiral\" Stache",
    "nameDisplay": "\"Admiral\" Stache",
    "description": "Milwaukee Brewing Co’s take on a classic European style. Baltic Porters are the stronger lager fermented cousin of the classic London Porter. The higher strength and cold fermentation help to create a smooth, less fruity porter, rich in roasted malt flavors and aromas. The “Admiral” Stache has a deep brown hue with a light caramel head. Toffee and milk chocolate dominate the flavor with subtle hints of dried fruit. One month of aging in Bourbon Barrels imparted a layer of vanilla and oak.\r\n\r\nWe first developed this beer in 2007. Our first attempted batch of beer at the 2nd street location was a Baltic Porter. What we ended up with became known as “Shake Down Nut Brown”. You can guess what went wrong from there… But, so many things right! Every year that has gone by, the beer has gotten a little bit stronger, in flavor and alcohol.\r\n\r\nWe use a black malt for the dark rich color and an extra special malt for the dried fruit flavors. Baltic Porters are fermented cold with a lager yeast. That long slow maturation creates a smooth flavor profile. The anticipation of the bourbon barrel aging it the most exciting part of this brew process. We want that oak character with hints of bourbon, we use 3rd run barrels for this result. Each batch has been slightly different from the last.",
    "abv": "7",
    "ibu": "23",
    "glasswareId": 5,
    "srmId": 37,
    "availableId": 4,
    "styleId": 104,
    "isOrganic": "N",
    "isRetired": "N",
    "labels": {
        "icon": "<document reference_id=\"<|document|>:6508\"><url>https://brewerydb-images.s3.amazonaws.com/beer/tmEthz/upload_3Jl1St-icon.png</url></document>",
        "medium": "<document reference_id=\"<|document|>:1107\"><url>https://brewerydb-images.s3.amazonaws.com/beer/tmEthz/upload_3Jl1St-medium.png</url></document>",
        "large": "<document reference_id=\"<|document|>:c5e2\"><url>https://brewerydb-images.s3.amazonaws.com/beer/tmEthz/upload_3Jl1St-large.png</url></document>",
        "contentAwareIcon": "<document reference_id=\"<|document|>:47d7\"><url>https://brewerydb-images.s3.amazonaws.com/beer/tmEthz/upload_3Jl1St-contentAwareIcon.png</url></document>",
        "contentAwareMedium": "<document reference_id=\"<|document|>:bbc8\"><url>https://brewerydb-images.s3.amazonaws.com/beer/tmEthz/upload_3Jl1St-contentAwareMedium.png</url></document>",
        "contentAwareLarge": "<document reference_id=\"<|document|>:551f\"><url>https://brewerydb-images.s3.amazonaws.com/beer/tmEthz/upload_3Jl1St-contentAwareLarge.png</url></document>"
    },
    "status": "verified",
    "statusDisplay": "Verified",
    "originalGravity": "1.071",
    "createDate": "2012-09-09 13:35:27",
    "updateDate": "2016-11-11 14:23:06",
    "glass": {
        "id": 5,
        "name": "Pint",
        "createDate": "2012-01-03 02:41:33"
    },
    "srm": {
        "id": 37,
        "name": "37",
        "hex": "3F0708"
    },
    "available": {
        "id": 4,
        "name": "Seasonal",
        "description": "Available at the same time of year, every year."
    },
    "style": {
        "id": 104,
        "categoryId": 9,
        "category": {
            "id": 9,
            "name": "Other Lager",
            "createDate": "2012-03-21 20:06:46"
        }
    }
}

# 展平嵌套的JSON数据
def flatten_json(nested_json, parent_key='', sep='_'):
    items = []
    for k, v in nested_json.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_json(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

# 展平数据
flattened_data = flatten_json(beer_data)
df = pd.DataFrame([flattened_data])

# 生成Excel文件
wb = Workbook()

# 样式定义
# 表头样式
header_fill = PatternFill('solid', fgColor='0070C0')
header_font = Font(name='Arial', bold=True, color='FFFFFF', size=11)
center_align = Alignment(horizontal='center', vertical='center', wrap_text=True)
left_align = Alignment(horizontal='left', vertical='center', wrap_text=True)
right_align = Alignment(horizontal='right', vertical='center', wrap_text=True)
thin_gray = Side(style='thin', color='D9D9D9')
h_border = Border(bottom=thin_gray)

# 1. 数据明细Sheet
ws_detail = wb.active
ws_detail.title = "啤酒数据明细"

# 写入表头
headers = df.columns.tolist()
for col_idx, header in enumerate(headers, 1):
    cell = ws_detail.cell(row=1, column=col_idx, value=header)
    cell.font = header_font
    cell.fill = header_fill
    cell.alignment = center_align
    cell.border = h_border

# 写入数据
for row_idx, row_data in enumerate(df.values, 2):
    for col_idx, value in enumerate(row_data, 1):
        cell = ws_detail.cell(row=row_idx, column=col_idx, value=value)
        # 对齐方式：文本左对齐，数值右对齐，其他居中
        if isinstance(value, str):
            cell.alignment = left_align
        elif isinstance(value, (int, float)):
            cell.alignment = right_align
        else:
            cell.alignment = center_align
        cell.border = h_border

# 2. 数据分析总结Sheet
ws_summary = wb.create_sheet("啤酒信息分析总结")

# 标题样式
title_fill = PatternFill('solid', fgColor='003366')
title_font = Font(name='Arial', bold=True, color='FFFFFF', size=14)
summary_header_fill = PatternFill('solid', fgColor='D9E1F2')
summary_header_font = Font(name='Arial', bold=True, color='000000', size=11)

# 写入标题
ws_summary.merge_cells('A1:B1')
title_cell = ws_summary['A1']
title_cell.value = "\"Admiral\" Stache 啤酒数据集分析总结"
title_cell.font = title_font
title_cell.fill = title_fill
title_cell.alignment = center_align
ws_summary.row_dimensions[1].height = 40

# 核心信息汇总
summary_data = [
    ["指标", "详情"],
    ["啤酒ID", beer_data['id']],
    ["啤酒名称", beer_data['name']],
    ["啤酒风格", f"Baltic Porter（波罗的海波特），属于 {beer_data['style']['category']['name']} 大类"],
    ["酒精度(ABV)", f"{beer_data['abv']}%"],
    ["苦度值(IBU)", beer_data['ibu']],
    ["色度(SRM)", f"{beer_data['srm']['name']}，色值Hex: {beer_data['srm']['hex']}"],
    ["原麦汁浓度", beer_data['originalGravity']],
    ["上市类型", f"{beer_data['available']['name']} - {beer_data['available']['description']}"],
    ["推荐杯型", beer_data['glass']['name']],
    ["是否有机", "是" if beer_data['isOrganic'] == 'Y' else "否"],
    ["是否已停产", "是" if beer_data['isRetired'] == 'Y' else "否"],
    ["数据状态", beer_data['statusDisplay']],
    ["首次开发年份", "2007年"],
    ["数据创建时间", beer_data['createDate']],
    ["数据最后更新时间", beer_data['updateDate']]
]

# 写入汇总数据
for row_idx, row_data in enumerate(summary_data, 2):
    for col_idx, value in enumerate(row_data, 1):
        cell = ws_summary.cell(row=row_idx, column=col_idx, value=value)
        # 表头行样式
        if row_idx == 2:
            cell.font = summary_header_font
            cell.fill = summary_header_fill
            cell.alignment = center_align
        else:
            if col_idx == 1:
                cell.font = Font(bold=True)
                cell.alignment = left_align
            else:
                cell.alignment = left_align
        cell.border = h_border

# 3. 啤酒描述详情Sheet
ws_desc = wb.create_sheet("啤酒详细描述")
# 写入标题
desc_title = ws_desc['A1']
desc_title.value = "\"Admiral\" Stache 啤酒详细描述"
desc_title.font = title_font
desc_title.fill = title_fill
desc_title.alignment = center_align
ws_desc.row_dimensions[1].height = 40

# 写入描述内容
desc_content = beer_data['description'].replace('\r\n', '\n')
ws_desc['A2'] = desc_content
ws_desc['A2'].alignment = Alignment(horizontal='left', vertical='top', wrap_text=True)
ws_desc['A2'].font = Font(name='Arial', size=11)
# 调整列宽和行高
ws_desc.column_dimensions['A'].width = 120
ws_desc.row_dimensions[2].height = 300

# 修复后的自动调整列宽函数
def display_width(text):
    return sum(2 if unicodedata.east_asian_width(c) in ('F','W') else 1 for c in str(text or ''))

def auto_fit_columns(ws, min_w=8, max_w=50, padding=3):
    for col_idx, col_cells in enumerate(ws.columns, 1):
        # 用列索引获取列字母，避免MergedCell无column_letter属性的问题
        letter = get_column_letter(col_idx)
        # 计算该列最大宽度，跳过合并单元格
        w = max(
            (display_width(c.value) for c in col_cells
             if not isinstance(c, openpyxl.cell.cell.MergedCell) and c.value is not None),
            default=0
        )
        # 设置列宽
        final_width = max(min_w, min(w * 1.1 + padding, max_w))
        ws.column_dimensions[letter].width = final_width

# 为所有Sheet自动调整列宽
auto_fit_columns(ws_detail)
auto_fit_columns(ws_summary, min_w=10, max_w=60)

# 冻结表头
ws_detail.freeze_panes = 'A2'
ws_summary.freeze_panes = 'A3'

# 保存文件
output_path = '/mnt/啤酒数据集分析结果.xlsx'
wb.save(output_path)

print(f"✅ Excel文件已成功生成，保存路径: {output_path}")
print("\n📋 文件包含3个结构化工作表：")
print("1. 【啤酒数据明细】：完整展平后的所有37个字段的原始数据，包含嵌套对象的拆解内容")
print("2. 【啤酒信息分析总结】：核心指标的结构化汇总，清晰展示啤酒的关键属性、规格、状态等信息")
print("3. 【啤酒详细描述】：啤酒的完整介绍文本，包含风格特点、酿造工艺、发展历史等详细内容")

print("\n📊 数据集核心信息总结：")
print(f"- 啤酒名称：{beer_data['name']}")
print(f"- 啤酒风格：Baltic Porter（波罗的海波特），属于Other Lager大类")
print(f"- 核心规格：酒精度7%ABV，苦度23IBU，色度37SRM，原麦汁浓度1.071")
print(f"- 上市属性：季节性供应，每年固定时间上市")
print(f"- 数据状态：已验证，未停产，非有机酿造")
print(f"- 开发历史：2007年首次开发，2012年录入数据，2016年最后更新")"""


"""
我计划分析啤酒数据集，第一步按规则读取 excel_core_operations 技能，接着调用工具读取该技能，以了解数据结构。

我计划分析啤酒数据集，先梳理步骤。第一步调用工具读取技能，学习表格操作；第二步将 JSON 数据整理为 DataFrame，查看结构等；第三步分析数据集信息，包括字段分类、数据内容及统计信息。当前先执行第一步，调用工具读取相关技能。


我计划处理用户啤酒数据，先将 JSON 数据整理成结构化 DataFrame。首先，调用工具编写代码，解析 JSON 对象，展平如 labels、glass 等嵌套字段，查看字段名、数据类型等基本信息，分析数据内容分类。


已完成代码运行
完成啤酒数据探查分析后，我计划先整理分析结果，接着生成结构化分析报告。若需生成 Excel 文件，会先读取相关技能来美化报告。


我计划生成 Excel 文件，将啤酒数据整理进去并按可视化规范美化。先思考文件结构，考虑设两个 sheet，一个放数据明细，一个作分析总结，后决定先整理数据再美化。接着编写代码，调用工具生成 Excel 文件，并设置表头、对齐、列宽等样式。


已完成代码运行

发现代码报错，错误原因是 auto_fit_columns 函数中获取列字母时，因 col_cells [0] 为 MergedCell 对象无 column_letter 属性致错。我意识到 summary sheet 的 A1:B1 是合并单元格，col_cells [0] 为 MergedCell。我决定修改函数，将 letter = col_cells [0].column_letter 改为 letter = get_column_letter (col_cells [0].column)，重新编写代码以修复问题。


已完成代码运行
已完成思考"""




