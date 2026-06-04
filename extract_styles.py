import os
import json
import glob
import csv

DATA_DIR = r"data\beer-dataset-master\beer-database"

def load_all_beer_data(data_dir):
    all_beers = []
    json_files = glob.glob(os.path.join(data_dir, "*.json"))
    print(f"正在加载 {len(json_files)} JSON 文件...")

    for file_path in json_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            all_beers.extend(data.get('data', []))
    
    print(f"成功加载 {len(all_beers)} 条啤酒数据")
    return all_beers

def extract_styles(all_beers):
    style_info = {}
    category_info = {}
    
    for beer in all_beers:
        style = beer.get('style', {})
        if style:
            style_id = style.get('id')
            if style_id and style_id not in style_info:
                style_info[style_id] = {
                    'style_id': style_id,
                    'style_name': style.get('name', ''),
                    'style_short_name': style.get('shortName', ''),
                    'style_description': style.get('description', ''),
                    'category_id': style.get('categoryId'),
                    'category_name': style.get('category', {}).get('name', '') if style.get('category') else '',
                    'ibu_min': style.get('ibuMin'),
                    'ibu_max': style.get('ibuMax'),
                    'abv_min': style.get('abvMin'),
                    'abv_max': style.get('abvMax'),
                    'srm_min': style.get('srmMin'),
                    'srm_max': style.get('srmMax'),
                    'count': 0
                }
            if style_id in style_info:
                style_info[style_id]['count'] += 1
            
            category = style.get('category', {})
            if category:
                category_id = category.get('id')
                if category_id and category_id not in category_info:
                    category_info[category_id] = {
                        'category_id': category_id,
                        'category_name': category.get('name', ''),
                        'count': 0
                    }
                if category_id in category_info:
                    category_info[category_id]['count'] += 1
    
    return style_info, category_info

def main():
    all_beers = load_all_beer_data(DATA_DIR)
    style_info, category_info = extract_styles(all_beers)
    
    styles_list = sorted(style_info.values(), key=lambda x: x['count'], reverse=True)
    categories_list = sorted(category_info.values(), key=lambda x: x['count'], reverse=True)
    
    print("\n" + "="*80)
    print(f"啤酒类别统计（共 {len(categories_list)} 个类别）")
    print("="*80)
    for cat in categories_list:
        print(f"{cat['category_id']:3d} | {cat['category_name']:<40s} | 数量: {cat['count']}")
    
    print("\n" + "="*80)
    print(f"啤酒风格统计（共 {len(styles_list)} 种风格）")
    print("="*80)
    
    fieldnames = ['style_id', 'style_name', 'style_short_name', 'category_id', 'category_name',
                  'count', 'ibu_min', 'ibu_max', 'abv_min', 'abv_max',
                  'srm_min', 'srm_max', 'style_description']
    
    with open('beer_styles.csv', 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        for s in styles_list:
            writer.writerow(s)
    
    print(f"\n已保存完整列表到 beer_styles.csv")
    
    print("\n" + "="*80)
    print(f"Top 30 啤酒风格")
    print("="*80)
    for i, s in enumerate(styles_list[:30], 1):
        print(f"{i:2d} | {s['style_name']:<45s} | {s['category_name']:<25s} | 数量: {s['count']}")

if __name__ == "__main__":
    main()
